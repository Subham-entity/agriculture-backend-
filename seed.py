from datetime import datetime, timedelta
import random
from app.database import SessionLocal, engine, Base
from app.models import User, Listing, Order

def seed_database():
    # Recreate tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()

    print("🌱 Seeding Users...")
    farmers = [
        User(name="Ramesh Kumar (FPO Lead)", role="FARMER", location="Farmer Hub A"),
        User(name="Suresh Patel", role="FARMER", location="Farmer Hub A"),
        User(name="Anita Devi", role="FARMER", location="Town Center"),
    ]
    buyers = [
        User(name="FreshMart Supermarkets", role="BUYER", location="Buyer Outlet B"),
        User(name="GreenGrocer Co.", role="BUYER", location="Metro Market"),
    ]
    db.add_all(farmers + buyers)
    db.commit()

    print("🌾 Seeding Crop Listings...")
    listings = [
        Listing(farmer_id=1, crop_name="Tomatoes", quantity_kg=1200.0, price_per_kg=22.5, location="Farmer Hub A"),
        Listing(farmer_id=1, crop_name="Potatoes", quantity_kg=3000.0, price_per_kg=18.0, location="Farmer Hub A"),
        Listing(farmer_id=2, crop_name="Onions", quantity_kg=1500.0, price_per_kg=25.0, location="Farmer Hub A"),
        Listing(farmer_id=3, crop_name="Wheat", quantity_kg=5000.0, price_per_kg=30.0, location="Town Center"),
    ]
    db.add_all(listings)
    db.commit()

    print("📦 Seeding Historical Orders for AI Model Training...")
    orders = []
    crops = ["Tomatoes", "Potatoes", "Onions", "Wheat"]
    
    for i in range(25):
        random_month = random.randint(1, 12)
        random_day = random.randint(1, 28)
        created_date = datetime(2025, random_month, random_day)

        order = Order(
            listing_id=random.choice([1, 2, 3, 4]),
            buyer_id=random.choice([4, 5]),
            quantity_kg=float(random.randint(100, 800)),
            total_price=float(random.randint(2000, 20000)),
            status="CONFIRMED",
            created_at=created_date
        )
        orders.append(order)

    db.add_all(orders)
    db.commit()
    db.close()
    print("✅ Database successfully populated with realistic hackathon demo data!")

if __name__ == "__main__":
    seed_database()