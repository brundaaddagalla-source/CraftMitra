from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse
)

from app.core.dependencies import require_artisan
from app.models.user import User
from app.services import artisan_service

from app.services import product_service


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


# =========================================
# CREATE PRODUCT
# =========================================
@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED
)
def create_new_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_artisan)
):
    # Get the artisan profile belonging
    # to the authenticated user
    artisan = artisan_service.get_artisan_by_user_id(
        db,
        current_user.id
    )

    if not artisan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Artisan profile does not exist"
        )

    # Ensure the product belongs to
    # the authenticated artisan
    if product_data.artisan_id != artisan.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create products for your own artisan profile"
        )

    try:
        product = product_service.create_product(
            db,
            product_data
        )

        return product_service.product_to_response(
            product
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )
# =========================================
# GET PRODUCT BY ID
# =========================================

@router.get(
    "/{product_id}",
    response_model=ProductResponse
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = product_service.get_product_by_id(
        db,
        product_id
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return product_service.product_to_response(
        product
    )


# =========================================
# GET PRODUCTS BY ARTISAN
# =========================================

@router.get(
    "/artisan/{artisan_id}",
    response_model=list[ProductResponse]
)
def get_artisan_products(
    artisan_id: int,
    db: Session = Depends(get_db)
):
    # Verify artisan exists
    artisan = product_service.get_artisan_by_id(
        db,
        artisan_id
    )

    if not artisan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artisan not found"
        )

    products = product_service.get_products_by_artisan_id(
        db,
        artisan_id
    )

    return [
        product_service.product_to_response(product)
        for product in products
    ]


# =========================================
# UPDATE PRODUCT
# =========================================
@router.patch(
    "/{product_id}",
    response_model=ProductResponse
)
def update_existing_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_artisan)
):
    product = product_service.get_product_by_id(
        db,
        product_id
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Get authenticated user's artisan profile
    artisan = artisan_service.get_artisan_by_user_id(
        db,
        current_user.id
    )

    if not artisan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Artisan profile does not exist"
        )

    # Ownership check
    if product.artisan_id != artisan.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own products"
        )

    updated_product = product_service.update_product(
        db,
        product,
        product_data
    )

    return product_service.product_to_response(
        updated_product
    )

# =========================================
# DELETE PRODUCT
# =========================================
@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_existing_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_artisan)
):
    product = product_service.get_product_by_id(
        db,
        product_id
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Get authenticated user's artisan profile
    artisan = artisan_service.get_artisan_by_user_id(
        db,
        current_user.id
    )

    if not artisan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Artisan profile does not exist"
        )

    # Ownership check
    if product.artisan_id != artisan.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own products"
        )

    product_service.delete_product(
        db,
        product
    )

    return None