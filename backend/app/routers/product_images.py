from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.core.dependencies import require_artisan
from app.models.user import User

from app.schemas.product_image import (
    ProductImageCreate,
    ProductImageUpdate,
    ProductImageResponse,
    ProductImageEnhancementResult
)

from app.services import (
    artisan_service,
    product_image_service
)


router = APIRouter(
    prefix="/products/{product_id}/images",
    tags=["Product Images"]
)


# =========================================
# CREATE PRODUCT IMAGE
# =========================================

@router.post(
    "",
    response_model=ProductImageResponse,
    status_code=status.HTTP_201_CREATED
)
def create_new_product_image(
    product_id: int,
    image_data: ProductImageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_artisan)
):
    # -------------------------------------
    # GET PRODUCT
    # -------------------------------------

    product = product_image_service.get_product_by_id(
        db,
        product_id
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # -------------------------------------
    # GET AUTHENTICATED ARTISAN PROFILE
    # -------------------------------------

    artisan = artisan_service.get_artisan_by_user_id(
        db,
        current_user.id
    )

    if not artisan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Artisan profile does not exist"
        )

    # -------------------------------------
    # VERIFY PRODUCT OWNERSHIP
    # -------------------------------------

    if product.artisan_id != artisan.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only add images to your own products"
        )

    # -------------------------------------
    # CREATE IMAGE
    # -------------------------------------

    try:
        image = product_image_service.create_product_image(
            db,
            product_id,
            image_data
        )

        return image

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


# =========================================
# GET ALL PRODUCT IMAGES
# =========================================

@router.get(
    "",
    response_model=list[ProductImageResponse]
)
def get_all_product_images(
    product_id: int,
    db: Session = Depends(get_db)
):
    # -------------------------------------
    # CHECK PRODUCT EXISTS
    # -------------------------------------

    product = product_image_service.get_product_by_id(
        db,
        product_id
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # -------------------------------------
    # GET PRODUCT IMAGES
    # -------------------------------------

    return product_image_service.get_product_images(
        db,
        product_id
    )


# =========================================
# UPDATE PRODUCT IMAGE
# =========================================

@router.patch(
    "/{image_id}",
    response_model=ProductImageResponse
)
def update_existing_product_image(
    product_id: int,
    image_id: int,
    image_data: ProductImageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_artisan)
):
    # -------------------------------------
    # GET PRODUCT
    # -------------------------------------

    product = product_image_service.get_product_by_id(
        db,
        product_id
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # -------------------------------------
    # GET IMAGE
    # -------------------------------------

    image = product_image_service.get_product_image_by_id(
        db,
        image_id
    )

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product image not found"
        )

    # -------------------------------------
    # VERIFY IMAGE BELONGS TO PRODUCT
    # -------------------------------------

    if image.product_id != product_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This image does not belong to the specified product"
        )

    # -------------------------------------
    # GET ARTISAN PROFILE
    # -------------------------------------

    artisan = artisan_service.get_artisan_by_user_id(
        db,
        current_user.id
    )

    if not artisan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Artisan profile does not exist"
        )

    # -------------------------------------
    # VERIFY PRODUCT OWNERSHIP
    # -------------------------------------

    if product.artisan_id != artisan.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update images of your own products"
        )

    # -------------------------------------
    # UPDATE IMAGE
    # -------------------------------------

    try:
        updated_image = (
            product_image_service.update_product_image(
                db,
                product_id,
                image,
                image_data
            )
        )

        return updated_image

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


# =========================================
# DELETE PRODUCT IMAGE
# =========================================

@router.delete(
    "/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_existing_product_image(
    product_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_artisan)
):
    # -------------------------------------
    # GET PRODUCT
    # -------------------------------------

    product = product_image_service.get_product_by_id(
        db,
        product_id
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # -------------------------------------
    # GET IMAGE
    # -------------------------------------

    image = product_image_service.get_product_image_by_id(
        db,
        image_id
    )

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product image not found"
        )

    # -------------------------------------
    # VERIFY IMAGE BELONGS TO PRODUCT
    # -------------------------------------

    if image.product_id != product_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This image does not belong to the specified product"
        )

    # -------------------------------------
    # GET ARTISAN PROFILE
    # -------------------------------------

    artisan = artisan_service.get_artisan_by_user_id(
        db,
        current_user.id
    )

    if not artisan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Artisan profile does not exist"
        )

    # -------------------------------------
    # VERIFY PRODUCT OWNERSHIP
    # -------------------------------------

    if product.artisan_id != artisan.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete images of your own products"
        )

    # -------------------------------------
    # DELETE IMAGE
    # -------------------------------------

    try:
        product_image_service.delete_product_image(
            db,
            product_id,
            image
        )

        return None

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


# =========================================
# START AI IMAGE ENHANCEMENT
# =========================================

@router.post(
    "/{image_id}/enhance",
    response_model=ProductImageResponse
)
def enhance_product_image(
    product_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_artisan)
):
    # -------------------------------------
    # GET ARTISAN PROFILE
    # -------------------------------------

    artisan = artisan_service.get_artisan_by_user_id(
        db,
        current_user.id
    )

    if not artisan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Artisan profile does not exist"
        )

    # -------------------------------------
    # GET PRODUCT
    # -------------------------------------

    product = product_image_service.get_product_by_id(
        db,
        product_id
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # -------------------------------------
    # VERIFY PRODUCT OWNERSHIP
    # -------------------------------------

    if product.artisan_id != artisan.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only enhance images of your own products"
        )

    # -------------------------------------
    # GET IMAGE
    # -------------------------------------

    image = product_image_service.get_product_image_by_id(
        db,
        image_id
    )

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product image not found"
        )

    # -------------------------------------
    # VERIFY IMAGE BELONGS TO PRODUCT
    # -------------------------------------

    if image.product_id != product_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This image does not belong to the specified product"
        )

    # -------------------------------------
    # PREVENT DUPLICATE PROCESSING
    # -------------------------------------

    if image.processing_status == "processing":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image enhancement is already in progress"
        )

    # -------------------------------------
    # PREVENT ENHANCING COMPLETED IMAGE
    # -------------------------------------

    if image.processing_status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image enhancement has already been completed"
        )

    # -------------------------------------
    # MARK IMAGE AS PROCESSING
    # -------------------------------------

    try:
        updated_image = (
            product_image_service.mark_image_as_processing(
                db,
                image
            )
        )

        return updated_image

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


# =========================================
# SAVE AI IMAGE ENHANCEMENT RESULT
# =========================================

@router.post(
    "/{image_id}/enhancement-result",
    response_model=ProductImageResponse
)
def save_product_image_enhancement_result(
    product_id: int,
    image_id: int,
    result_data: ProductImageEnhancementResult,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_artisan)
):
    # -------------------------------------
    # GET ARTISAN PROFILE
    # -------------------------------------

    artisan = artisan_service.get_artisan_by_user_id(
        db,
        current_user.id
    )

    if not artisan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Artisan profile does not exist"
        )

    # -------------------------------------
    # GET PRODUCT
    # -------------------------------------

    product = product_image_service.get_product_by_id(
        db,
        product_id
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # -------------------------------------
    # VERIFY PRODUCT OWNERSHIP
    # -------------------------------------

    if product.artisan_id != artisan.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You can only update enhancement results "
                "for your own products"
            )
        )

    # -------------------------------------
    # GET IMAGE
    # -------------------------------------

    image = product_image_service.get_product_image_by_id(
        db,
        image_id
    )

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product image not found"
        )

    # -------------------------------------
    # VERIFY IMAGE BELONGS TO PRODUCT
    # -------------------------------------

    if image.product_id != product_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This image does not belong to the specified product"
        )

    # -------------------------------------
    # SAVE AI RESULT
    # -------------------------------------

    try:
        updated_image = (
            product_image_service.save_enhanced_image(
                db,
                image,
                result_data.enhanced_image_url
            )
        )

        return updated_image

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


# =========================================
# MARK AI IMAGE ENHANCEMENT AS FAILED
# =========================================

@router.post(
    "/{image_id}/enhancement-failed",
    response_model=ProductImageResponse
)
def mark_product_image_enhancement_failed(
    product_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_artisan)
):
    # -------------------------------------
    # GET ARTISAN PROFILE
    # -------------------------------------

    artisan = artisan_service.get_artisan_by_user_id(
        db,
        current_user.id
    )

    if not artisan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Artisan profile does not exist"
        )

    # -------------------------------------
    # GET PRODUCT
    # -------------------------------------

    product = product_image_service.get_product_by_id(
        db,
        product_id
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # -------------------------------------
    # VERIFY PRODUCT OWNERSHIP
    # -------------------------------------

    if product.artisan_id != artisan.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You can only update enhancement status "
                "for your own products"
            )
        )

    # -------------------------------------
    # GET IMAGE
    # -------------------------------------

    image = product_image_service.get_product_image_by_id(
        db,
        image_id
    )

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product image not found"
        )

    # -------------------------------------
    # VERIFY IMAGE BELONGS TO PRODUCT
    # -------------------------------------

    if image.product_id != product_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This image does not belong to the specified product"
        )

    # -------------------------------------
    # MARK PROCESSING AS FAILED
    # -------------------------------------

    try:
        updated_image = (
            product_image_service.mark_image_processing_failed(
                db,
                image
            )
        )

        return updated_image

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )