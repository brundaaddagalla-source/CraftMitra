from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.ai.pricing_model import predict_product_price
from app.core.dependencies import require_artisan
from app.database import get_db
from app.models.user import User

from app.schemas.price_prediction import (
    PricePredictionCreate,
    PricePredictionResponse
)

from app.services import (
    artisan_service,
    pricing_service,
    product_service
)


router = APIRouter(
    prefix="/price-predictions",
    tags=["Price Predictions"]
)


# =========================================
# GENERATE PRICE PREDICTION
# =========================================

@router.post(
    "/product/{product_id}/predict",
    response_model=PricePredictionResponse,
    status_code=status.HTTP_201_CREATED
)
def predict_price(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_artisan)
):
    # -------------------------------------
    # GET PRODUCT
    # -------------------------------------

    product = product_service.get_product_by_id(
        db,
        product_id
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
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
            detail=(
                "You can only generate price predictions "
                "for your own products"
            )
        )

    # -------------------------------------
    # CALL PRICING ML MODEL
    # -------------------------------------

    try:
        prediction_result = predict_product_price(
            product
        )

    except NotImplementedError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error)
        )

    # -------------------------------------
    # PREPARE PREDICTION DATA
    # -------------------------------------

    prediction_data = PricePredictionCreate(
        product_id=product.id,
        predicted_price=prediction_result[
            "predicted_price"
        ],
        confidence=prediction_result.get(
            "confidence"
        ),
        model_name=prediction_result.get(
            "model_name"
        ),
        model_version=prediction_result.get(
            "model_version"
        )
    )

    # -------------------------------------
    # SAVE PREDICTION
    # -------------------------------------

    prediction = (
        pricing_service.create_price_prediction(
            db,
            prediction_data
        )
    )

    return prediction


# =========================================
# GET ALL PRICE PREDICTIONS FOR A PRODUCT
# =========================================

@router.get(
    "/product/{product_id}",
    response_model=list[PricePredictionResponse]
)
def get_product_price_predictions(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_artisan)
):
    # -------------------------------------
    # GET PRODUCT
    # -------------------------------------

    product = product_service.get_product_by_id(
        db,
        product_id
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
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
            detail=(
                "You can only access price predictions "
                "for your own products"
            )
        )

    # -------------------------------------
    # GET PREDICTIONS
    # -------------------------------------

    predictions = (
        pricing_service.get_predictions_by_product_id(
            db,
            product_id
        )
    )

    return predictions


# =========================================
# GET PRICE PREDICTION BY ID
# =========================================

@router.get(
    "/{prediction_id}",
    response_model=PricePredictionResponse
)
def get_price_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_artisan)
):
    # -------------------------------------
    # GET PREDICTION
    # -------------------------------------

    prediction = (
        pricing_service.get_price_prediction_by_id(
            db,
            prediction_id
        )
    )

    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Price prediction not found"
        )

    # -------------------------------------
    # GET PRODUCT
    # -------------------------------------

    product = product_service.get_product_by_id(
        db,
        prediction.product_id
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
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
            detail=(
                "You can only access price predictions "
                "for your own products"
            )
        )

    return prediction