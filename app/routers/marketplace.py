from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/marketplace", tags=["Marketplace & Users"])

# --- USER ENDPOINTS ---
@router.post("/users/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# --- LISTING ENDPOINTS ---
@router.post("/listings/", response_model=schemas.ListingResponse, status_code=status.HTTP_201_CREATED)
def create_listing(listing: schemas.ListingCreate, db: Session = Depends(get_db)):
    # Verify farmer exists
    farmer = db.query(models.User).filter(models.User.id == listing.farmer_id).first()
    if not farmer or farmer.role.upper() != "FARMER":
        raise HTTPException(status_code=400, detail="Invalid farmer ID")
    
    db_listing = models.Listing(**listing.dict())
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing

@router.get("/listings/", response_model=List[schemas.ListingResponse])
def get_all_listings(crop_name: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Listing)
    if crop_name:
        query = query.filter(models.Listing.crop_name.ilike(f"%{crop_name}%"))
    return query.all()

@router.delete("/listings/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(models.Listing).filter(models.Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    db.delete(listing)
    db.commit()
    return None