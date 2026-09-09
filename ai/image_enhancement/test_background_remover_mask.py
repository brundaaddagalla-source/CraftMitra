import cv2

from background_remover_mask import (
    BackgroundRemoverMask
)


# =========================================================
# INPUT
# =========================================================

image_path = (
    "data/sampleImages/BlendBGImage.png"
)


# =========================================================
# OUTPUT
# =========================================================

output_path = (
    "data/sampleImages/"
    "craftmitra_blend_mask.png"
)


# =========================================================
# GENERATE MASK
# =========================================================

remover = BackgroundRemoverMask()

mask = remover.generate_mask(
    image_path
)


# =========================================================
# SAVE
# =========================================================

remover.save_mask(
    mask,
    output_path
)


# =========================================================
# INFORMATION
# =========================================================

print()
print("==========================================")
print("BACKGROUND MASK GENERATION SUCCESSFUL")
print("==========================================")

print("Input :", image_path)
print("Output:", output_path)

print("Shape :", mask.shape)
print("Type  :", mask.dtype)
print("Min   :", mask.min())
print("Max   :", mask.max())

print("==========================================")