from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()

class User(db.Model):
    __tablename__ ='user'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(80), nullable=False)
    email_id = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False) 
    pincode = db.Column(db.String(10))

    bookings = db.relationship('Booking', back_populates='user', lazy=True)

    

# Parking Lot Model

class ParkingLot(db.Model):
    __tablename__ = 'parkinglot'
    id = db.Column(db.Integer, primary_key=True)
    lot_name = db.Column(db.String(100),unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pin_code = db.Column(db.Integer(), nullable=False)
    total_spots = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10,2))

    spots = db.relationship('ParkingSpot',back_populates='lot', lazy='joined')
    bookings = db.relationship('Booking', back_populates='lot', lazy=True)


# Parking Spot Model

class ParkingSpot(db.Model):
    __tablename__ = 'parkingspot'
    id = db.Column(db.Integer, primary_key=True)
    # spot_name = db.Column(db.String(40), unique=True, nullable=False)
    spot_number = db.Column(db.String(50), nullable=False)
    lot_id = db.Column(db.Integer, db.ForeignKey('parkinglot.id'), nullable=False)
    status = db.Column(db.String(1), nullable=False, default='A')

    lot = db.relationship('ParkingLot', back_populates='spots')
    bookings = db.relationship('Booking', back_populates='spot', lazy=True)
   

# Booking Model (Active/Released spot info)

class Booking(db.Model):
    __tablename__ = 'booking'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lot_id = db.Column(db.Integer, db.ForeignKey('parkinglot.id'), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('parkingspot.id'), nullable=False)

    vehicle_number = db.Column(db.String(20), nullable=False)
    booking_time = db.Column(db.DateTime, default=datetime.now)
    release_time = db.Column(db.DateTime, nullable=True)

    status = db.Column(db.String(20), default="Parked")  # Parked, Released


    user = db.relationship("User", back_populates="bookings")
    lot = db.relationship("ParkingLot", back_populates="bookings")
    spot = db.relationship("ParkingSpot", back_populates="bookings")
    
   
