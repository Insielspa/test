import cv2
import numpy as np


def create_loading_image(width: int, height: int) -> np.ndarray:
    temp_img = cv2.imread("./assets/images/loading.png")
    h, w = temp_img.shape[:2]

    image = np.zeros((height, width, 3), dtype=np.uint8)

    # Calcola la posizione in cui posizionare l'immagine "loading.png" al centro del frame
    x = (width - w) // 2
    y = (height - h) // 2

    # Posiziona l'immagine "loading.png" all'interno del frame
    image[y:y + h, x:x + w] = temp_img

    return image

def create_error_no_connection(width: int, height: int) -> np.ndarray:
    temp_img = cv2.imread("./assets/images/no_connection.png")
    h, w = temp_img.shape[:2]

    image = np.zeros((height, width, 3), dtype=np.uint8)

    # Calcola la posizione in cui posizionare l'immagine "loading.png" al centro del frame
    x = (width - w) // 2
    y = (height - h) // 2

    # Posiziona l'immagine "loading.png" all'interno del frame
    image[y:y + h, x:x + w] = temp_img

    return image


def rotate_loading_image(loading_image, angle: int) -> np.ndarray:
    # Ruota l'immagine di caricamento di un determinato angolo
    rotated_image = cv2.warpAffine(loading_image,
                                   cv2.getRotationMatrix2D(
                                       (loading_image.shape[1] / 2, loading_image.shape[0] / 2),
                                       angle, 1),
                                   (loading_image.shape[1], loading_image.shape[0]))
    return rotated_image
