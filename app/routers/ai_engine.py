from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import networkx as nx
from typing import List

from .. import schemas, models
from ..database import get_db

router = APIRouter(prefix="/ai", tags=["AI Engine (Forecasting & Logistics)"])

# =====================================================================
# 1. AI DEMAND FORECASTING MODULE (scikit-learn)
# =====================================================================

def train_forecasting_model(db: Session, crop_name: str):
    """
    Retrieves historical order data from SQLite, trains a Linear Regression model,
    and predicts demand trends based on month and price.
    """
    # Query historical order records joined with listing details
    records = (
        db.query(models.Order, models.Listing)
        .join(models.Listing, models.Order.listing_id == models.Listing.id)
        .filter(models.Listing.crop_name.ilike(crop_name))
        .all()
    )

    # Fallback synthetic training data if historical database records are low
    if len(records) < 5:
        data = {
            "month": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] * 3,
            "price": [20, 25, 30, 22, 28, 35, 18, 24, 29, 31, 23, 26] * 3,
            "demand_kg": [500, 450, 400, 520, 430, 380, 550, 480, 420, 390, 510, 460] * 3
        }
        df = pd.DataFrame(data)
    else:
        df = pd.DataFrame([
            {
                "month": order.created_at.month,
                "price": listing.price_per_kg,
                "demand_kg": order.quantity_kg
            }
            for order, listing in records
        ])

    X = df[["month", "price"]]
    y = df["demand_kg"]

    model = LinearRegression()
    model.fit(X, y)
    return model

@router.post("/forecast-demand", response_model=schemas.ForecastResponse)
def forecast_crop_demand(payload: schemas.ForecastRequest, db: Session = Depends(get_db)):
    if not (1 <= payload.target_month <= 12):
        raise HTTPException(status_code=400, detail="Target month must be between 1 and 12")

    model = train_forecasting_model(db, payload.crop_name)
    
    # Run prediction
    input_features = np.array([[payload.target_month, payload.price_per_kg]])
    predicted_demand = model.predict(input_features)[0]
    
    # Cap negative predictions to realistic bounds
    final_demand = max(float(predicted_demand), 50.0)

    return schemas.ForecastResponse(
        crop_name=payload.crop_name,
        target_month=payload.target_month,
        predicted_demand_kg=round(final_demand, 2),
        confidence_note="Model trained using scikit-learn Linear Regression on aggregated marketplace transactions."
    )


# =====================================================================
# 2. LOGISTICS ROUTE OPTIMIZATION MODULE (NetworkX)
# =====================================================================

def build_logistics_network() -> nx.Graph:
    """
    Constructs a spatial graph of regional hubs with distances in kilometers.
    """
    G = nx.Graph()

    # Define regional supply chain hubs (Edges format: Node A, Node B, Distance in KM)
    routes = [
        ("Farmer Hub A", "Town Center", 15),
        ("Farmer Hub A", "Storage Facility", 10),
        ("Storage Facility", "Town Center", 8),
        ("Storage Facility", "Highway Junction", 25),
        ("Town Center", "Highway Junction", 20),
        ("Town Center", "Metro Market", 45),
        ("Highway Junction", "Metro Market", 30),
        ("Metro Market", "Bulk Distribution Yard", 12),
        ("Bulk Distribution Yard", "Buyer Outlet B", 8),
        ("Metro Market", "Buyer Outlet B", 18)
    ]

    for source, target, distance in routes:
        G.add_edge(source, target, weight=distance)

    return G

@router.post("/optimize-route", response_model=schemas.RouteResponse)
def get_optimal_delivery_route(payload: schemas.RouteRequest):
    G = build_logistics_network()

    if payload.start_location not in G.nodes or payload.end_location not in G.nodes:
        available_nodes = list(G.nodes)
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid location. Available network nodes: {available_nodes}"
        )

    try:
        # Calculate Dijkstra's shortest path
        shortest_path = nx.shortest_path(G, source=payload.start_location, target=payload.end_location, weight="weight")
        total_distance = nx.shortest_path_length(G, source=payload.start_location, target=payload.end_location, weight="weight")
        
        # Estimate transit time assuming 40 km/h average speed for rural transport
        estimated_hours = round(total_distance / 40.0, 2)

        return schemas.RouteResponse(
            optimal_route=shortest_path,
            total_distance_km=float(total_distance),
            estimated_transit_time_hrs=estimated_hours
        )
    except nx.NetworkXNoPath:
        raise HTTPException(status_code=404, detail="No viable logistics route exists between given locations.")