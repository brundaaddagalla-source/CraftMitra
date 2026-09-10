from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
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
    image_enhancement_service,
    product_image_service,
    storage_service
)

# Keep uploads reasonable - a phone camera photo is typically 2-8MB.
MAX_UPLOAD_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


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
# UPLOAD PRODUCT IMAGE (multipart file)
# =========================================
#
# Step 2/3 of the Add Product flow: the frontend sends the raw photo
# (captured or uploaded) here. We store it in Supabase and register
# the resulting URL as a ProductImage row in one call, instead of
# requiring the frontend to already have a hosted image_url.

@router.post(
    "/upload",
    response_model=ProductImageResponse,
    status_code=status.HTTP_201_CREATED
)
async def upload_new_product_image(
    product_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    is_primary: bool = Form(False),
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
    # VALIDATE FILE TYPE
    # -------------------------------------

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPG, PNG or WEBP images are supported"
        )

    # -------------------------------------
    # READ + VALIDATE SIZE
    # -------------------------------------

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty"
        )

    if len(file_bytes) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image is too large (max 15MB)"
        )

    # -------------------------------------
    # UPLOAD TO SUPABASE STORAGE
    # -------------------------------------

    try:
        image_url = storage_service.upload_file(
            file_bytes,
            file.filename or "photo.jpg",
            file.content_type
        )
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error)
        )

    # -------------------------------------
    # CREATE IMAGE RECORD
    # -------------------------------------

    try:
        image = product_image_service.create_product_image(
            db,
            product_id,
            ProductImageCreate(
                image_url=image_url,
                is_primary=is_primary
            )
        )

        # Nothing in this flow makes the artisan press a separate
        # "enhance" button - kick the AI enhancement pipeline off
        # automatically the moment the photo lands, so by the time
        # they reach the review screen it's likely already done.
        image = product_image_service.mark_image_as_processing(db, image)
        background_tasks.add_task(
            image_enhancement_service.run_enhancement_pipeline,
            image.id
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
    background_tasks: BackgroundTasks,
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

        # Kick off the actual AI enhancement pipeline in the
        # background - it can take several seconds, so the request
        # returns immediately with "processing" and the frontend
        # polls (see get_all_product_images / get one image) until
        # this flips the status to "completed" or "failed".
        background_tasks.add_task(
            image_enhancement_service.run_enhancement_pipeline,
            image_id
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