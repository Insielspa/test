import threading

from common.triple_buffer import TripleBuffer
from common.video_observable import VideoObservable
from config.app_settings import AppSettings
from output.hls.ffmpeg_output_streamer import FFMpegOutputStreamer


# Funzione per eseguire il client RTMP in un thread separato
def run_hls_streamer_thread(video_observable: VideoObservable, buffer: TripleBuffer, app_settings: AppSettings,
                            exit_event: threading.Event) -> threading.Thread:
    frame_builder = FFMpegOutputStreamer(buffer, app_settings)
    #frame_builder = GStreamerOutputStreamer(buffer, app_settings)

    video_observable.add_video_observer(frame_builder)

    hls_streamer_thread = threading.Thread(target=frame_builder.build_frame,
                                           args=(exit_event,),
                                           name='OutputThread')
    hls_streamer_thread.daemon = True
    hls_streamer_thread.start()

    return hls_streamer_thread
