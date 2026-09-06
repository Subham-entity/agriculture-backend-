from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "FARMER" or "BUYER"
    location = Column(String, nullable=False)

    listings = relationship("Listing", back_populates="farmer")
    orders = relationship("Order", back_populates="buyer")

class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    crop_name = Column(String, index=True, nullable=False)
    quantity_kg = Column(Float, nullable=False)
    price_per_kg = Column(Float, nullable=False)
    location = Column(String, nullable=False)

    farmer = relationship("User", back_populates="listings")
    orders = relationship("Order", back_populates="listing")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quantity_kg = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(String, default="PENDING")  # "PENDING", "CONFIRMED", "SHIPPED"
    created_at = Column(DateTime, default=datetime.utcnow)

    listing = relationship("Listing", back_populates="orders")
    buyer = relationship("User", back_populates="orders")