import PyNvCodec as nvc
import numpy as np


class VideoReader:
    def __init__(self, video_path, gpu_id=0):
        """
        Inizializza il decodificatore VPF con il percorso del file video.

        Args:
            video_path (str): Percorso del file MP4.
            gpu_id (int, optional): ID della GPU. Default: 0.
        """
        self.video_path = video_path
        self.gpu_id = gpu_id
        self.nv_dec = nvc.PyNvDecoder(video_path, gpu_id)

    def read_frame(self):
        """
        Legge il prossimo frame dal video e lo restituisce come array NumPy in formato RGB.

        Returns:
            np.ndarray: Frame in formato RGB (altezza, larghezza, 3).
        """
        frame_nv12 = self.nv_dec.DecodeSingleFrame(format='nv12')  # Formato NV12
        if frame_nv12 is None:
            return None

        # Converti da NV12 a RGB
        frame_rgb = nvc.nv12_to_rgb(frame_nv12)

        return frame_rgb

    def close(self):
        """
        Chiude il decodificatore.
        """
        self.nv_dec.Close()


# Esempio di utilizzo
if __name__ == "__main__":
    video_path = '/app/assets/videos/strada_laterale1_800x600.mp4'  # Sostituisci con il percorso corretto
    video_reader = VideoReader(video_path)

    try:
        while True:
            frame = video_reader.read_frame()
            if frame is None:
                break  # Fine del video

            # Ora puoi lavorare con il frame RGB (ad esempio, visualizzarlo o elaborarlo)
            # frame è un array numpy con le dimensioni (altezza, larghezza, 3)
            print(f"Dimensioni del frame: {frame.shape}")

    finally:
        video_reader.close()
