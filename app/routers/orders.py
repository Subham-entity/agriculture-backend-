from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/orders", tags=["Order Management"])

@router.post("/", response_model=schemas.OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order_data: schemas.OrderCreate, db: Session = Depends(get_db)):
    # Verify buyer
    buyer = db.query(models.User).filter(models.User.id == order_data.buyer_id).first()
    if not buyer or buyer.role.upper() != "BUYER":
        raise HTTPException(status_code=400, detail="Invalid buyer ID")

    # Verify stock availability
    listing = db.query(models.Listing).filter(models.Listing.id == order_data.listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    if listing.quantity_kg < order_data.quantity_kg:
        raise HTTPException(status_code=400, detail="Insufficient crop stock available")

    # Deduct stock and calculate total price
    listing.quantity_kg -= order_data.quantity_kg
    total_price = order_data.quantity_kg * listing.price_per_kg

    db_order = models.Order(
        listing_id=order_data.listing_id,
        buyer_id=order_data.buyer_id,
        quantity_kg=order_data.quantity_kg,
        total_price=total_price,
        status="CONFIRMED"
    )

    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("/user/{user_id}", response_model=List[schemas.OrderResponse])
def get_user_orders(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.Order).filter(models.Order.buyer_id == user_id).all()