from app import db
from app.models.driver import Driver
from app.models.vehicle import Vehicle


def register_driver(
    user_id,
    license_number,
    aadhaar_number,
    vehicle_type,
    vehicle_number,
    brand,
    model,
    max_weight
):
    # Check if the user is already registered as a driver
    existing_driver = Driver.query.filter_by(user_id=user_id).first()

    if existing_driver:
        return None, "You are already registered as a driver."

    # Check if the vehicle number already exists
    existing_vehicle = Vehicle.query.filter_by(
        vehicle_number=vehicle_number
    ).first()

    if existing_vehicle:
        return None, "Vehicle number already exists."

    # Create Driver
    driver = Driver(
        user_id=user_id,
        license_number=license_number,
        aadhaar_number=aadhaar_number
    )

    db.session.add(driver)
    db.session.flush()

    # Create Vehicle
    vehicle = Vehicle(
        driver_id=driver.id,
        vehicle_type=vehicle_type,
        vehicle_number=vehicle_number,
        brand=brand,
        model=model,
        max_weight=max_weight
    )

    db.session.add(vehicle)
    db.session.commit()

    return {
        "driver_id": driver.id,
        "vehicle_id": vehicle.id
    }, None