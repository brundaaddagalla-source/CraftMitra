from sqlalchemy.orm import Session

from app.models.price_prediction import PricePrediction
from app.schemas.price_prediction import PricePredictionCreate


# =========================================
# GET PRICE PREDICTION BY ID
# =========================================

def get_price_prediction_by_id(
    db: Session,
    prediction_id: int
):
    return (
        db.query(PricePrediction)
        .filter(
            PricePrediction.id == prediction_id
        )
        .first()
    )


# =========================================
# GET ALL PREDICTIONS FOR A PRODUCT
# =========================================

def get_predictions_by_product_id(
    db: Session,
    product_id: int
):
    return (
        db.query(PricePrediction)
        .filter(
            PricePrediction.product_id == product_id
        )
        .order_by(
            PricePrediction.created_at.desc()
        )
        .all()
    )


# =========================================
# SAVE PRICE PREDICTION
# =========================================

def create_price_prediction(
    db: Session,
    prediction_data: PricePredictionCreate
):
    new_prediction = PricePrediction(
        product_id=prediction_data.product_id,
        predicted_price=prediction_data.predicted_price,
        confidence=prediction_data.confidence,
        model_name=prediction_data.model_name,
        model_version=prediction_data.model_version
    )

    db.add(new_prediction)

    db.commit()

    db.refresh(new_prediction)

    return new_prediction