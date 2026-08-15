from app.models.driver import Driver
from app.models.vehicle import Vehicle
from app.models.booking import Booking
from app.utils.distance import haversine_distance
from extensions import db


def register_driver(
    user_id,
    license_number,
    aadhaar_number,
    pan_number,
    vehicle_type,
    vehicle_number,
    brand,
    model,
    max_weight,
    rc_number
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
        aadhaar_number=aadhaar_number,
        pan_number=pan_number
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
        max_weight=max_weight,
        rc_number=rc_number
    )

    db.session.add(vehicle)
    db.session.commit()

    return {
        "driver_id": driver.id,
        "vehicle_id": vehicle.id
    }, None


# =====================================
# Driver Availability Services
# =====================================

def go_online(user_id):
    """
    Set driver status to ONLINE.
    """

    driver = Driver.query.filter_by(user_id=user_id).first()

    if not driver:
        return None, "Driver not found."

    driver.is_online = True

    db.session.commit()

    return {
        "driver_id": driver.id,
        "is_online": driver.is_online
    }, None


def go_offline(user_id):
    """
    Set driver status to OFFLINE.
    """

    driver = Driver.query.filter_by(user_id=user_id).first()

    if not driver:
        return None, "Driver not found."

    driver.is_online = False

    db.session.commit()

    return {
        "driver_id": driver.id,
        "is_online": driver.is_online
    }, None


def get_driver_status(user_id):
    """
    Get current driver availability.
    """

    driver = Driver.query.filter_by(user_id=user_id).first()

    if not driver:
        return None, "Driver not found."

    return {
        "driver_id": driver.id,
        "is_online": driver.is_online,
        "status": driver.status
    }, None

# =====================================
# Driver Location Services
# =====================================

def update_driver_location(user_id, latitude, longitude):
    """
    Update driver's current GPS location.
    """

    driver = Driver.query.filter_by(user_id=user_id).first()

    if not driver:
        return None, "Driver not found."

    driver.latitude = latitude
    driver.longitude = longitude

    db.session.commit()

    return {
        "driver_id": driver.id,
        "latitude": driver.latitude,
        "longitude": driver.longitude
    }, None


def get_driver_location(user_id):
    """
    Get driver's current GPS location.
    """

    driver = Driver.query.filter_by(user_id=user_id).first()

    if not driver:
        return None, "Driver not found."

    return {
        "driver_id": driver.id,
        "latitude": driver.latitude,
        "longitude": driver.longitude
    }, None

# =====================================
# Find Available Drivers
# =====================================

def get_available_drivers():

    drivers = Driver.query.all()

    print("Total Drivers:", len(drivers))

    available_drivers = []

    for driver in drivers:

        print(
            driver.id,
            driver.is_online,
            driver.status,
            driver.latitude,
            driver.longitude
        )

        if driver.latitude is None or driver.longitude is None:
            continue

        if not driver.is_online:
            continue

        if driver.status not in ["Pending", "Approved"]:
            continue

        vehicle = Vehicle.query.filter_by(driver_id=driver.id).first()

        available_drivers.append({
            "driver_id": driver.id,
            "user_id": driver.user_id,
            "vehicle_id": vehicle.id if vehicle else None,
            "latitude": driver.latitude,
            "longitude": driver.longitude,
            "status": driver.status
        })

    return available_drivers

# =====================================
# Find Nearest Driver
# =====================================

def find_nearest_driver(pickup_latitude, pickup_longitude):
    """
    Find the nearest available driver.
    """

    drivers = get_available_drivers()

    if not drivers:
        return None

    for driver in drivers:

        driver["distance_km"] = haversine_distance(
            pickup_latitude,
            pickup_longitude,
            driver["latitude"],
            driver["longitude"]
        )

    drivers.sort(key=lambda driver: driver["distance_km"])

    return drivers[0]

# =====================================
# Driver Jobs
# =====================================

def get_driver_jobs(user_id):
    """
    Return all bookings assigned to the logged-in driver.
    """

    driver = Driver.query.filter_by(user_id=user_id).first()

    if not driver:
        return None, "Driver not found."

    bookings = (
        Booking.query
        .filter_by(driver_id=driver.id)
        .order_by(Booking.created_at.desc())
        .all()
    )

    jobs = []

    for booking in bookings:

        jobs.append({
            "booking_id": booking.booking_id,
            "pickup_address": booking.pickup_address,
            "destination_address": booking.destination_address,
            "pickup_lat": booking.pickup_lat,
            "pickup_lng": booking.pickup_lng,
            "destination_lat": booking.destination_lat,
            "destination_lng": booking.destination_lng,
            "vehicle_type": booking.vehicle_type,
            "goods_type": booking.goods_type,
            "estimated_weight": booking.estimated_weight,
            "status": booking.status,
            "created_at": booking.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return jobs, None