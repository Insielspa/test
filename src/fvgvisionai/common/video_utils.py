from numpy import ndarray


def draw_icon(frame: ndarray, x_offset, y_offset, icon_image):
    if y_offset + icon_image.shape[0] > frame.shape[0] or x_offset + icon_image.shape[1] > frame.shape[1]:
        return

    for c in range(0, 3):
        # Utilizza l'alpha dell'immagine da sovrapporre come maschera
        frame[y_offset:y_offset + icon_image.shape[0],
        x_offset:x_offset + icon_image.shape[1], c] = ((1.0 - icon_image[:, :, 3] / 255.0) *
                                                       frame[y_offset:y_offset + icon_image.shape[0],
                                                       x_offset:x_offset + icon_image.shape[1], c] +
                                                       (icon_image[:, :, 3] / 255.0) * icon_image[:, :, c])
