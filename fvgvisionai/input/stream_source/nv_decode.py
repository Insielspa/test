#
# Copyright 2019 NVIDIA Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import argparse
import logging
from enum import Enum
from pathlib import Path

import PyNvCodec as nvc
import cv2
import numpy as np

logger = logging.getLogger(__file__)


class cconverter:
    """
    Colorspace conversion chain.
    """

    def __init__(self, width: int, height: int, gpu_id: int):
        self.gpu_id = gpu_id
        self.w = width
        self.h = height
        self.chain = []

    def add(self, src_fmt: nvc.PixelFormat, dst_fmt: nvc.PixelFormat) -> None:
        self.chain.append(
            nvc.PySurfaceConverter(self.w, self.h, src_fmt, dst_fmt, self.gpu_id)
        )

    def run(self, src_surface: nvc.Surface) -> nvc.Surface:
        surf = src_surface
        cc = nvc.ColorspaceConversionContext(nvc.ColorSpace.BT_601, nvc.ColorRange.MPEG)

        for cvt in self.chain:
            surf = cvt.Execute(surf, cc)
            if surf.Empty():
                raise RuntimeError("Failed to perform color conversion")

        return surf.Clone(self.gpu_id)


class InitMode(Enum):
    # Decoder will be created with built-in demuxer.
    BUILTIN = (0,)
    # Decoder will be created with standalone FFmpeg VPF demuxer.
    STANDALONE = 1


class DecodeStatus(Enum):
    # Decoding error.
    DEC_ERR = (0,)
    # Frame was submitted to decoder.
    # No frames are ready for display yet.
    DEC_SUBM = (1,)
    # Frame was submitted to decoder.
    # There's a frame ready for display.
    DEC_READY = 2


class NvDecoder:
    def __init__(
            self,
            gpu_id: int,
            enc_file: str,
            dec_file: str,
            dmx_mode=InitMode.STANDALONE,
    ):
        # Save mode, we will need this later
        self.init_mode = dmx_mode

        if self.init_mode == InitMode.STANDALONE:
            # Initialize standalone demuxer.
            self.nv_dmx = nvc.PyFFmpegDemuxer(enc_file)
            # Initialize decoder.
            self.nv_dec = nvc.PyNvDecoder(
                self.nv_dmx.Width(),
                self.nv_dmx.Height(),
                self.nv_dmx.Format(),
                self.nv_dmx.Codec(),
                gpu_id,
            )
        else:
            # Initialize decoder with built-in demuxer.
            self.nv_dmx = None
            self.nv_dec = nvc.PyNvDecoder(enc_file, gpu_id)

        # Frame to seek to next time decoding function is called.
        # Negative values means 'don't use seek'.  Non-negative values mean
        # seek frame number.
        self.sk_frm = int(-1)
        # Total amount of decoded frames
        self.num_frames_decoded = int(0)
        # Numpy array to store decoded frames pixels
        self.frame_nv12 = np.ndarray(shape=(0), dtype=np.uint8)
        # Output file
        self.out_file = open(dec_file, "wb")
        # Encoded video packet
        self.packet = np.ndarray(shape=(0), dtype=np.uint8)
        # Encoded packet data
        self.packet_data = nvc.PacketData()
        # Seek mode
        self.seek_mode = nvc.SeekMode.PREV_KEY_FRAME

        # Dimensioni del frame noto dal video di test (800x600)
        self.known_width = 800
        self.known_height = 600

    # Returns decoder creation mode
    def mode(self) -> InitMode:
        return self.init_mode

    # Returns video width in pixels
    def width(self) -> int:
        if self.mode() == InitMode.STANDALONE:
            return self.nv_dmx.Width()
        else:
            return self.nv_dec.Width()

    # Returns video height in pixels
    def height(self) -> int:
        if self.mode() == InitMode.STANDALONE:
            return self.nv_dmx.Height()
        else:
            return self.nv_dec.Height()

    # Returns number of decoded frames.
    def dec_frames(self) -> int:
        return self.num_frames_decoded

    # Returns frame rate
    def framerate(self) -> float:
        if self.mode() == InitMode.STANDALONE:
            return self.nv_dmx.Framerate()
        else:
            return self.nv_dec.Framerate()

    # Returns average frame rate
    def avg_framerate(self) -> float:
        if self.mode() == InitMode.STANDALONE:
            return self.nv_dmx.AvgFramerate()
        else:
            return self.nv_dec.AvgFramerate()

    # Returns True if video has various frame rate, False otherwise
    def is_vfr(self) -> bool:
        if self.mode() == InitMode.STANDALONE:
            return self.nv_dmx.IsVFR()
        else:
            return self.nv_dec.IsVFR()

    # Returns number of frames in video.
    def stream_num_frames(self) -> int:
        if self.mode() == InitMode.STANDALONE:
            return self.nv_dmx.Numframes()
        else:
            return self.nv_dec.Numframes()

    # Seek for particular frame number.
    def seek(
            self,
            seek_frame: int,
            seek_mode: nvc.SeekMode,
            seek_criteria: str = "ts",
    ) -> None:
        # Next time we decode frame decoder will seek for this frame first.
        self.sk_frm = seek_frame
        self.seek_mode = seek_mode
        self.seek_criteria = seek_criteria
        self.num_frames_decoded = 0

    def _decode_frame_standalone(self, verbose=False) -> DecodeStatus:
        _status = DecodeStatus.DEC_ERR

        try:
            # Check if we need to seek first.
            if self.sk_frm >= 0:
                if self.sk_frm.is_integer():
                    self.sk_frm = int(self.sk_frm)
                logger.info(f"Seeking for the {self.seek_criteria} {self.sk_frm}")
                seek_ctx = nvc.SeekContext(
                    **{"seek_" + self.seek_criteria: self.sk_frm},
                    mode=self.seek_mode
                )
                self.sk_frm = -1

                if not self.nv_dmx.Seek(seek_ctx, self.packet):
                    return _status

                logger.info("We are at frame with pts {str(seek_ctx.out_frame_pts)}")
            # Otherwise we just demux next packet.
            elif not self.nv_dmx.DemuxSinglePacket(self.packet):
                return _status

            # Send encoded packet to Nvdec.
            # Nvdec is async so it may not return decoded frame immediately.
            frame_ready = self.nv_dec.DecodeFrameFromPacket(
                self.frame_nv12, self.packet
            )
            if frame_ready:
                self.num_frames_decoded += 1
                _status = DecodeStatus.DEC_READY
            else:
                _status = DecodeStatus.DEC_SUBM

            # Get last demuxed packet data.
            # It stores info such as pts, duration etc.
            self.nv_dmx.LastPacketData(self.packet_data)

            if verbose:
                logger.info(f"frame pts (decode order)      :{self.packet_data.pts}")
                logger.info(f"frame dts (decode order)      :{self.packet_data.dts}")
                logger.info(f"frame pos (decode order)      :{self.packet_data.pos}")
                logger.info(
                    f"frame duration (decode order) :{self.packet_data.duration}"
                )
        except Exception as e:
            logger.info(f"{getattr(e, 'message', str(e))}")

        return _status

    def _decode_frame_builtin(self, verbose=False) -> DecodeStatus:
        _status = DecodeStatus.DEC_ERR

        try:
            frame_ready = False
            frame_cnt_inc = 0

            if self.sk_frm >= 0:
                logger.info("Seeking for the frame ", str(self.sk_frm))
                seek_ctx = nvc.SeekContext(
                    int(self.sk_frm), self.seek_mode, self.seek_criteria
                )
                self.sk_frm = -1

                frame_ready = self.nv_dec.DecodeSingleSurface() DecodeSingleFrame(
                    self.frame_nv12, seek_ctx, self.packet_data
                )
                frame_cnt_inc = seek_ctx.num_frames_decoded
            else:
                frame_ready = self.nv_dec.DecodeSingleFrame(
                    self.frame_nv12, self.packet_data
                )
                frame_cnt_inc = 1

            # Nvdec is sync in this mode so if frame isn't returned it means
            # EOF or error.
            if frame_ready:
                self.num_frames_decoded += 1
                _status = DecodeStatus.DEC_READY

                if verbose:
                    logger.info(f"Decoded {frame_cnt_inc} frames internally")
            else:
                return _status

            if verbose:
                logger.info(f"frame pts (display order)      :{self.packet_data.pts}")
                logger.info(f"frame dts (display order)      :{self.packet_data.dts}")
                logger.info(f"frame pos (display order)      :{self.packet_data.pos}")
                logger.info(
                    f"frame duration (display order) :{self.packet_data.duration}"
                )

        except Exception as e:
            logger.info(f"{getattr(e, 'message', str(e))}")

        return _status

    # Decode single video frame
    def decode_frame(self, verbose=False) -> DecodeStatus:
        if self.mode() == InitMode.STANDALONE:
            return self._decode_frame_standalone(verbose)
        else:
            return self._decode_frame_builtin(verbose)

    # Send empty packet to decoder to flush decoded frames queue.
    def _flush_frame(self) -> bool:
        ret = self.nv_dec.FlushSingleFrame(self.frame_nv12)
        if ret:
            self.num_frames_decoded += 1

        return ret

    # Write current video frame to output file.
    def _current_frame(self) -> np.ndarray:
        return self.frame_nv12

    # Decode all available video frames and write them to output file.
    def decode(self, verbose=False) -> (bool, np.ndarray):
        while True:
            _status = self.decode_frame(verbose)
            if _status == DecodeStatus.DEC_ERR:
                return False, None
            elif _status == DecodeStatus.DEC_READY:
                self.nv_dec.DecodeSingleSurface()
                # Crea un oggetto Surface con il formato NV12
                #nv12_surface = nvc.PySurfaceConverter(800, 600, nvc.PixelFormat.NV12, nvc.PixelFormat.RGB, 0)
                #nv12_surface. SetHostFrame(self._current_frame())

                # Converte il frame NV12 in formato RGBA
                #rgba_frame = nv12_surface.HostFrame()

                # Usa OpenCV per convertire RGBA a RGB
                rgb_frame = cv2.cvtColor(rgba_frame, cv2.COLOR_RGBA2RGB)

                return True, rgb_frame


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "This sample decodes input video to raw NV12 file on given GPU."
    )
    parser.add_argument(
        "-g",
        "--gpu-id",
        type=int,
        required=True,
        help="GPU id, check nvidia-smi",
    )
    parser.add_argument(
        "-e",
        "--encoded-file-path",
        type=Path,
        required=True,
        help="Encoded video file (read from)",
    )
    parser.add_argument(
        "-r",
        "--raw-file-path",
        type=Path,
        required=True,
        help="Raw NV12 video file (write to)",
    )
    parser.add_argument(
        "-v", "--verbose", default=False, action="store_true", help="Verbose"
    )

    args = parser.parse_args()

    dec = NvDecoder(
        args.gpu_id,
        args.encoded_file_path.as_posix(),
        args.raw_file_path.as_posix(),
    )


    print(f"{dec.width()} {dec.height()} {dec.dec_frames()}")

    frame_counter = 0
    status, frame = dec.decode()
    while status:
        frame_counter += 1
        status, frame = dec.decode()

    if frame is not None:
        print(f"frame counted: {frame_counter}, {dec.mode()} {frame.shape}")

    exit(0)
