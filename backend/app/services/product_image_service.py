from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.product_image import ProductImage

from app.schemas.product_image import (
    ProductImageCreate,
    ProductImageUpdate
)


# =========================================
# GET PRODUCT BY ID
# =========================================

def get_product_by_id(
    db: Session,
    product_id: int
):
    return (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )


# =========================================
# GET IMAGE BY ID
# =========================================

def get_product_image_by_id(
    db: Session,
    image_id: int
):
    return (
        db.query(ProductImage)
        .filter(ProductImage.id == image_id)
        .first()
    )


# =========================================
# GET ALL IMAGES OF A PRODUCT
# =========================================

def get_product_images(
    db: Session,
    product_id: int
):
    return (
        db.query(ProductImage)
        .filter(ProductImage.product_id == product_id)
        .order_by(
            ProductImage.is_primary.desc(),
            ProductImage.created_at.asc()
        )
        .all()
    )


# =========================================
# CREATE PRODUCT IMAGE
# =========================================

def create_product_image(
    db: Session,
    product_id: int,
    image_data: ProductImageCreate
):
    # -------------------------------------
    # CHECK PRODUCT EXISTS
    # -------------------------------------

    product = get_product_by_id(
        db,
        product_id
    )

    if not product:
        raise ValueError(
            "Product not found"
        )

    # -------------------------------------
    # IF THIS IMAGE IS PRIMARY,
    # REMOVE PRIMARY STATUS FROM OTHERS
    # -------------------------------------

    if image_data.is_primary:
        (
            db.query(ProductImage)
            .filter(
                ProductImage.product_id == product_id
            )
            .update(
                {
                    ProductImage.is_primary: False
                },
                synchronize_session=False
            )
        )

    # -------------------------------------
    # CREATE IMAGE
    # -------------------------------------

    new_image = ProductImage(
        product_id=product_id,
        image_url=image_data.image_url,
        is_primary=image_data.is_primary
    )

    db.add(new_image)
    db.commit()
    db.refresh(new_image)

    return new_image


# =========================================
# UPDATE PRODUCT IMAGE
# =========================================

def update_product_image(
    db: Session,
    product_id: int,
    image: ProductImage,
    image_data: ProductImageUpdate
):
    # -------------------------------------
    # OWNERSHIP CHECK
    # -------------------------------------

    if image.product_id != product_id:
        raise ValueError(
            "This image does not belong to the specified product"
        )

    update_data = image_data.model_dump(
        exclude_unset=True
    )

    # -------------------------------------
    # UPDATE IMAGE URL
    # -------------------------------------

    if "image_url" in update_data:
        image.image_url = update_data["image_url"]

    # -------------------------------------
    # UPDATE PRIMARY STATUS
    # -------------------------------------

    if "is_primary" in update_data:

        is_primary = update_data["is_primary"]

        if is_primary:

            # Remove primary status
            # from all other images

            (
                db.query(ProductImage)
                .filter(
                    ProductImage.product_id == product_id,
                    ProductImage.id != image.id
                )
                .update(
                    {
                        ProductImage.is_primary: False
                    },
                    synchronize_session=False
                )
            )

            image.is_primary = True

        else:
            image.is_primary = False

    db.commit()
    db.refresh(image)

    return image


# =========================================
# DELETE PRODUCT IMAGE
# =========================================

def delete_product_image(
    db: Session,
    product_id: int,
    image: ProductImage
):
    # -------------------------------------
    # OWNERSHIP CHECK
    # -------------------------------------

    if image.product_id != product_id:
        raise ValueError(
            "This image does not belong to the specified product"
        )

    db.delete(image)
    db.commit()
# =========================================
# MARK IMAGE AS PROCESSING
# =========================================

def mark_image_as_processing(
    db: Session,
    image: ProductImage
):
    image.processing_status = "processing"

    db.commit()
    db.refresh(image)

    return image
# =========================================
# SAVE AI ENHANCED IMAGE
# =========================================
# =========================================
# SAVE AI ENHANCED IMAGE
# =========================================

def save_enhanced_image(
    db: Session,
    image: ProductImage,
    enhanced_image_url: str
):
    # Enhancement result should only be
    # accepted while processing is active

    if image.processing_status != "processing":
        raise ValueError(
            "Image enhancement is not currently in progress"
        )

    image.enhanced_image_url = enhanced_image_url

    image.processing_status = "completed"

    db.commit()
    db.refresh(image)

    return image
# =========================================
# MARK IMAGE PROCESSING AS FAILED
# =========================================

def mark_image_processing_failed(
    db: Session,
    image: ProductImage
):
    image.processing_status = "failed"

    db.commit()
    db.refresh(image)

    return image