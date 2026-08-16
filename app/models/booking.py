from extensions import db
from datetime import datetime
from bson import ObjectId

class BookingHelper:
    @staticmethod
    def create(customer_id, data, nearest_driver=None):
        booking_doc = {
            "booking_id": f"MM{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "customer_id": customer_id,
            "pickup_address": data['pickup_address'],
            "destination_address": data['destination_address'],
            "pickup_lat": data['pickup_lat'],
            "pickup_lng": data['pickup_lng'],
            "destination_lat": data['destination_lat'],
            "destination_lng": data['destination_lng'],
            "vehicle_type": data['vehicle_type'],
            "goods_type": data.get('goods_type', 'General'),
            "estimated_weight": data.get('estimated_weight', 0),
            "status": "Driver Assigned" if nearest_driver else "Waiting for Driver",
            "driver_id": nearest_driver['driver_id'] if nearest_driver else None,
            "vehicle_id": nearest_driver['vehicle_id'] if nearest_driver else None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = db.bookings.insert_one(booking_doc)
        booking_doc['_id'] = str(result.inserted_id)
        return booking_doc

    @staticmethod
    def get_customer_bookings(customer_id):
        bookings = list(db.bookings.find({"customer_id": customer_id}).sort("created_at", -1))
        for b in bookings:
            b['_id'] = str(b['_id'])
            b['created_at'] = b['created_at'].strftime("%Y-%m-%d %H:%M:%S")
        return bookings
