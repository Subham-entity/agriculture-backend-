from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# --- User Schemas ---
class UserCreate(BaseModel):
    name: str
    role: str  # "FARMER" or "BUYER"
    location: str

class UserResponse(UserCreate):
    id: int
    class Config:
        from_attributes = True

# --- Listing Schemas ---
class ListingCreate(BaseModel):
    farmer_id: int
    crop_name: str
    quantity_kg: float
    price_per_kg: float
    location: str

class ListingResponse(ListingCreate):
    id: int
    class Config:
        from_attributes = True

# --- Order Schemas ---
class OrderCreate(BaseModel):
    listing_id: int
    buyer_id: int
    quantity_kg: float

class OrderResponse(BaseModel):
    id: int
    listing_id: int
    buyer_id: int
    quantity_kg: float
    total_price: float
    status: str
    created_at: datetime
    class Config:
        from_attributes = True

# --- AI Engine Schemas ---
class ForecastRequest(BaseModel):
    crop_name: str
    target_month: int  # 1 to 12
    price_per_kg: float

class ForecastResponse(BaseModel):
    crop_name: str
    target_month: int
    predicted_demand_kg: float
    confidence_note: str

class RouteRequest(BaseModel):
    start_location: str
    end_location: str

class RouteResponse(BaseModel):
    optimal_route: List[str]
    total_distance_km: float
    estimated_transit_time_hrs: float