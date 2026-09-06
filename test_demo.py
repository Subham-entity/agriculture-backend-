import httpx
import sys

BASE_URL = "http://127.0.0.1:8000"

def run_automated_tests():
    print("🚀 Starting Automated API Diagnostics...\n")
    client = httpx.Client(base_url=BASE_URL)

    try:
        # 1. Health Check
        res = client.get("/")
        assert res.status_code == 200, "Health check failed"
        print("✅ [1/5] Health Check Endpoint: PASS")

        # 2. Get Listings
        res = client.get("/marketplace/listings/")
        assert res.status_code == 200 and len(res.json()) > 0, "Fetch listings failed"
        print(f"✅ [2/5] Fetch Listings API ({len(res.json())} items found): PASS")

        # 3. Create Order
        order_payload = {"listing_id": 1, "buyer_id": 4, "quantity_kg": 100.0}
        res = client.post("/orders/", json=order_payload)
        assert res.status_code == 201, f"Create order failed: {res.text}"
        print(f"✅ [3/5] Create Order & Stock Deduction API: PASS (Order ID: {res.json()['id']})")

        # 4. AI Demand Forecast
        forecast_payload = {"crop_name": "Tomatoes", "target_month": 11, "price_per_kg": 24.0}
        res = client.post("/ai/forecast-demand", json=forecast_payload)
        assert res.status_code == 200, "AI Demand Forecast failed"
        prediction = res.json()["predicted_demand_kg"]
        print(f"✅ [4/5] AI Demand Forecasting API: PASS (Predicted: {prediction} kg)")

        # 5. Route Optimization
        route_payload = {"start_location": "Farmer Hub A", "end_location": "Buyer Outlet B"}
        res = client.post("/ai/optimize-route", json=route_payload)
        assert res.status_code == 200, "Route Optimization failed"
        route = res.json()["optimal_route"]
        print(f"✅ [5/5] Route Optimization API: PASS (Path: {' -> '.join(route)})")

        print("\n🎉 ALL SYSTEM ENDPOINTS FUNCTIONAL! READY FOR JUDGES.")

    except httpx.ConnectError:
        print("❌ Error: FastAPI server is not running! Start it using 'uvicorn app.main:app --reload'")
        sys.exit(1)
    except AssertionError as e:
        print(f"❌ Test Failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_automated_tests()