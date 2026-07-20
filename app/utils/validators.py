REQUIRED_BOOKING_FIELDS = [
    "pickup_address",
    "destination_address",
    "pickup_lat",
    "pickup_lng",
    "destination_lat",
    "destination_lng",
    "vehicle_type",
    "goods_type",
    "estimated_weight"
]


def validate_booking(data):
    missing = []

    for field in REQUIRED_BOOKING_FIELDS:
        if field not in data:
            missing.append(field)

    return missing