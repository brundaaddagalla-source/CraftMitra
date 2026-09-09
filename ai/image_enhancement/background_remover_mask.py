"""
background_remover_mask.py

Generates a foreground mask using BackgroundRemover / U2-Net.

Responsibilities:
    - Accept image path or NumPy image
    - Generate foreground mask using U2-Net
    - Decode the returned mask
    - Normalize mask dimensions to match the input image
    - Return a grayscale uint8 mask

This module does NOT:
    - modify the original image
    - generate a background
    - composite the image
"""

from pathlib import Path
from typing import Union

import cv2
import numpy as np

from backgroundremover.bg import remove


ImageInput = Union[str, Path, np.ndarray]


class BackgroundRemoverMask:
    """
    Generate foreground masks using BackgroundRemover / U2-Net.
    """

    MODEL_NAME = "u2net"

    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name

    def generate_mask(self, image: ImageInput) -> np.ndarray:
        """
        Generate a foreground mask.

        Parameters
        ----------
        image:
            Image path or BGR NumPy image.

        Returns
        -------
        np.ndarray
            Grayscale uint8 mask with dimensions EXACTLY
            matching the input image.

        Mask meaning:
            0   = background
            255 = foreground
        """

        # ---------------------------------------------------------
        # 1. Load / validate input image
        # ---------------------------------------------------------
        image_array = self._load_image(image)

        if image_array is None:
            raise ValueError("Unable to load input image.")

        original_height, original_width = image_array.shape[:2]

        # ---------------------------------------------------------
        # 2. Convert image to bytes
        # ---------------------------------------------------------
        image_bytes = self._image_to_bytes(image_array)

        # ---------------------------------------------------------
        # 3. Generate mask using U2-Net
        # ---------------------------------------------------------
        mask_bytes = remove(
            image_bytes,
            model_name=self.model_name,
            only_mask=True,
        )

        # ---------------------------------------------------------
        # 4. Decode returned mask
        # ---------------------------------------------------------
        mask = self._decode_mask(mask_bytes)

        if mask is None:
            raise ValueError(
                "BackgroundRemover returned an invalid or empty mask."
            )

        # ---------------------------------------------------------
        # 5. Normalize mask
        # ---------------------------------------------------------
        mask = self._normalize_mask(mask)

        # ---------------------------------------------------------
        # 6. IMPORTANT:
        #    Make mask dimensions exactly equal to image dimensions.
        #
        #    This protects the rest of the pipeline from dimension
        #    differences caused by the segmentation model.
        # ---------------------------------------------------------
        mask_height, mask_width = mask.shape[:2]

        if mask_width != original_width or mask_height != original_height:

            mask = cv2.resize(
                mask,
                (original_width, original_height),
                interpolation=cv2.INTER_LINEAR,
            )

        # ---------------------------------------------------------
        # 7. Final validation
        # ---------------------------------------------------------
        if mask.shape[:2] != (original_height, original_width):
            raise ValueError(
                "Failed to normalize mask dimensions. "
                f"Image: {(original_height, original_width)}, "
                f"Mask: {mask.shape[:2]}"
            )

        return mask.astype(np.uint8)

    # =============================================================
    # Helper methods
    # =============================================================

    @staticmethod
    def _load_image(image: ImageInput) -> np.ndarray:
        """
        Load an image from a path or return a NumPy image.
        """

        if isinstance(image, (str, Path)):
            image_array = cv2.imread(str(image), cv2.IMREAD_COLOR)

            if image_array is None:
                raise ValueError(
                    f"Unable to read image: {image}"
                )

            return image_array

        if isinstance(image, np.ndarray):
            if image.size == 0:
                raise ValueError("Input image array is empty.")

            return image.copy()

        raise TypeError(
            "image must be a file path or NumPy array."
        )

    @staticmethod
    def _image_to_bytes(image: np.ndarray) -> bytes:
        """
        Encode a NumPy image as PNG bytes.
        """

        success, encoded = cv2.imencode(
            ".png",
            image,
        )

        if not success:
            raise ValueError(
                "Failed to encode image into PNG bytes."
            )

        return encoded.tobytes()

    @staticmethod
    def _decode_mask(mask_bytes: bytes) -> np.ndarray:
        """
        Decode mask bytes returned by BackgroundRemover.
        """

        if mask_bytes is None:
            raise ValueError(
                "BackgroundRemover returned None."
            )

        if isinstance(mask_bytes, memoryview):
           mask_bytes = mask_bytes.tobytes()
        elif isinstance(mask_bytes, bytearray):
            mask_bytes = bytes(mask_bytes)
        elif not isinstance(mask_bytes, bytes):
            raise TypeError(
                "BackgroundRemover returned an unexpected data type: "
                f"{type(mask_bytes)}"
            )

        buffer = np.frombuffer(
            mask_bytes,
            dtype=np.uint8,
        )

        mask = cv2.imdecode(
            buffer,
            cv2.IMREAD_GRAYSCALE,
        )

        if mask is None:
            raise ValueError(
                "Unable to decode BackgroundRemover mask."
            )

        return mask

    @staticmethod
    def _normalize_mask(mask: np.ndarray) -> np.ndarray:
        """
        Ensure mask is a valid grayscale uint8 image.
        """

        if mask.ndim == 3:
            mask = cv2.cvtColor(
                mask,
                cv2.COLOR_BGR2GRAY,
            )

        if mask.dtype != np.uint8:
            mask = cv2.normalize(
                mask,
                None,
                0,
                255,
                cv2.NORM_MINMAX,
            ).astype(np.uint8)

        return mask


# =================================================================
# Convenience function
# =================================================================

def generate_background_mask(image: ImageInput) -> np.ndarray:
    """
    Convenience function for generating a foreground mask.
    """

    remover = BackgroundRemoverMask()

    return remover.generate_mask(image)


# =================================================================
# CLI
# =================================================================

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        description="Generate foreground mask using U2-Net."
    )

    parser.add_argument(
        "input_image",
        help="Path to input image",
    )

    parser.add_argument(
        "output_mask",
        help="Path to save generated mask",
    )

    args = parser.parse_args()

    remover = BackgroundRemoverMask()

    mask = remover.generate_mask(
        args.input_image
    )

    success = cv2.imwrite(
        args.output_mask,
        mask,
    )

    if not success:
        raise RuntimeError(
            f"Failed to save mask: {args.output_mask}"
        )

    print(
        f"Mask generated successfully: {args.output_mask}"
    )

    print(
        f"Mask dimensions: "
        f"{mask.shape[1]} x {mask.shape[0]}"
    )