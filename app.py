from flask import Flask, render_template, redirect, request, url_for, session,flash
from models import db, User, ParkingLot, ParkingSpot, Booking, datetime
from sqlalchemy.orm import joinedload



app = Flask(__name__)
app.secret_key = 'this_is_my_secret_key_123'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)



@app.route("/")
def default():
    return redirect("/login")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email_id = request.form.get('email_id')
        password = request.form.get('password')
        pincode = request.form.get('pincode')

        email_exists = User.query.filter_by(email_id=email_id).first()
        if email_exists:
            print('User already exists, please use a different email.')
            return redirect('/login')
        else:
            new_user = User(
                fullname=fullname,
                email_id=email_id,
                password=password,
                pincode=pincode,
            )
            db.session.add(new_user)
            db.session.commit()
            print('User created successfully.')
            return redirect('/login')            
            

@app.route("/login",methods=['GET','POST'])
def login():
    if request.method =='GET':
        return render_template("login.html")
    if request.method == 'POST':
        email_id = request.form.get('email_id')
        password = request.form.get('password')

        user = User.query.filter_by(email_id=email_id).first()

        if not user:
            return render_template("login.html")

        if user and user.email_id == "admin@gmail.com":
            return redirect('/admin_dashboard')


        if  user.password == password:
            session['user_id'] = user.id 
            print(f"Login successful for: {email_id}")
            return redirect('/user_dashboard')
        else:
            print("Invalid login credentials.")
            return render_template("login.html")


 

    
@app.route('/admin_dashboard')
def admin_dashboard():
    # Fetch all required data first
    users = User.query.all()
    lots = ParkingLot.query.options(joinedload(ParkingLot.spots)).all()
    bookings = Booking.query.all()

    total_occupied = 0  # Initialize count

    #  spot list and occupied count to each lot
    for lot in lots:
        lot.spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
        lot.occupied_count = sum(1 for spot in lot.spots if spot.status == 'O')
        total_occupied += lot.occupied_count  # Accumulate occupied count

    for spot in ParkingSpot.query.all():
        print(f"Spot ID: {spot.id}, Lot ID: {spot.lot_id}, Status: {spot.status}")

    return render_template(
        'admin_dashboard.html',
        users=users,
        lots=lots,
        bookings=bookings,
        total_users=len(users),
        total_lots=len(lots),
        total_spots=sum(len(lot.spots) for lot in lots),
        total_occupied=total_occupied
    )

        
@app.route('/user_dashboard', methods=['GET'])
def user_dashboard():
    # Ensure user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = User.query.get(user_id)
    query = request.args.get('query')

    # Filter parking lots by location (address or name) or pin code
    if query:
        lots = ParkingLot.query.filter(
            (ParkingLot.address.ilike(f"%{query}%")) |
            (ParkingLot.lot_name.ilike(f"%{query}%")) |
            (ParkingLot.pin_code.ilike(f"%{query}%"))
        ).all()
    else:
        lots = ParkingLot.query.all()

    # Get user's parking history (recent bookings)
    bookings = Booking.query.join(ParkingSpot).join(ParkingLot)\
        .filter(Booking.user_id == user_id)\
        .order_by(Booking.booking_time.desc()).all()

    return render_template('user_dashboard.html', bookings=bookings, lots=lots, user=user, id=id)


@app.route('/create-admin')
def create_admin():
    # Check if admin already exists
    existing_admin = User.query.filter_by(email_id='admin@gmail.com').first()
    if existing_admin:
        return "Admin already exists!"

    # Create admin user
    admin = User(fullname='admin', email_id='admin@gmail.com', password=12345678, pincode='282001')
    db.session.add(admin)
    db.session.commit()

    return "Admin user created successfully!"


@app.route('/new_parking_lot', methods=['GET', 'POST'])
def new_parking_lot():
    if request.method == 'GET':
        return render_template("new_parking_lot.html")
    
    if request.method == 'POST':
        id = request.form.get('id')
        lot_name = request.form.get('lot_name')
        address = request.form.get('address')
        pin_code = request.form.get('pin_code')
        total_spots = request.form.get('total_spots')
        price = request.form.get('price')

        parkinglot_exists = ParkingLot.query.filter_by(lot_name=lot_name).first()
        if parkinglot_exists:
            print('Lot Already exist')
            return redirect('/new_parking_lot')
        else:
            # Convert total_spots to int
            total_spots = int(total_spots)

            # Create parking lot
            parkinglot = ParkingLot(
                id=id,
                lot_name=lot_name,
                address=address,
                pin_code=pin_code,
                price=price,
                total_spots=total_spots
            )
            db.session.add(parkinglot)
            db.session.commit()  # Commit here so we can access parkinglot.id

            #  Insert spots after committing the lot
            for i in range(1, total_spots + 1):
                spot = ParkingSpot(
                    lot_id=parkinglot.id,
                    spot_number=f"S{i}",
                    status='A'  # Available
                )
                db.session.add(spot)

            db.session.commit()  # Commit the spots

            print('New lot and spots created')
            return redirect('/admin_dashboard')

    # return render_template('new_parking_lot.html')

from decimal import Decimal

@app.route('/edit_parking_lot/<int:lot_id>', methods=['GET', 'POST'])
def edit_parking_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    old_spot_count = lot.total_spots

    if request.method == 'POST':
        # Get form data
        lot.lot_name = request.form.get('lot_name')
        lot.address = request.form.get('address')
        lot.pin_code = int(request.form.get('pin_code'))
        new_total_spots = int(request.form.get('total_spots'))
        lot.price = Decimal(request.form.get('price'))

        # Sync parking spots
        difference = new_total_spots - old_spot_count

        if difference > 0:
            # Add new spots
            for i in range(difference):
                new_spot_number = f"S{old_spot_count + i + 1}"
                new_spot = ParkingSpot(spot_number=new_spot_number, lot_id=lot.id, status='A')
                db.session.add(new_spot)
        elif difference < 0:
            # Delete extra available spots (not occupied)
            available_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').order_by(ParkingSpot.id.desc()).limit(abs(difference)).all()
            for spot in available_spots:
                db.session.delete(spot)

        lot.total_spots = new_total_spots

        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_parking_lot.html', lot=lot)




@app.route('/delete_parking_lot/<int:lot_id>', methods=['POST', 'GET'])
def delete_parking_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)

    for spot in lot.spots:
        db.session.delete(spot)

    db.session.delete(lot)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/book/<int:lot_id>/<int:spot_id>', methods=['GET', 'POST'])
def book_spot(lot_id, spot_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    lot = ParkingLot.query.get_or_404(lot_id)
    spot = ParkingSpot.query.get_or_404(spot_id)

    if request.method == 'POST':
        vehicle_number = request.form['vehicle_number']

        new_booking = Booking(
            user_id=user_id,
            lot_id=lot_id,
            spot_id=spot_id,
            vehicle_number=vehicle_number,
            status="Parked"
        )
        spot.status = 'O'  # Mark as occupied
        db.session.add(new_booking)
        db.session.commit()
        return redirect(url_for('user_dashboard'))

    return render_template('book_spot.html', lot=lot, spot=spot, user_id=user_id)



@app.route('/occupied_parking_spot/<int:spot_id>', methods=['GET'])
def occupied_parking_spot(spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)
    booking = Booking.query.filter_by(spot_id=spot_id).order_by(Booking.booking_time.desc()).first()

    return render_template('occupied_parking_spot.html', spot=spot, booking=booking)




@app.route('/release_spot/<int:spot_id>', methods=['GET', 'POST'])
def release_spot(spot_id):
    booking = Booking.query.filter_by(spot_id=spot_id, status='Parked').first()
    now = datetime.now()

    if request.method == 'POST':
        if booking:
            spot = ParkingSpot.query.get(spot_id)
            spot.status = 'A'  # Mark spot as Available

            booking.release_time = now
            duration = (booking.release_time - booking.booking_time).total_seconds() / 3600    # for minute 3600*60
            duration = round(duration, 2)

            # Get the price from related lot
            price_per_hour = float(spot.lot.price)

            # Apply condition: minimum 1-hour charge
            if duration < 1:
                total_cost = price_per_hour
            else:
                total_cost = round(price_per_hour * duration, 2)

            booking.total_cost = total_cost
            booking.status = 'released'

            db.session.commit()

            return render_template('release_spot.html', booking=booking, now=now)

        return redirect(url_for('user_dashboard'))

    # For GET requests, just show the release confirmation page
    return render_template('release_spot.html', booking=booking, now=now)



#@app.context_processor
# def inject_now():
#     return {'now': datetime.now()}
 


@app.route('/view_spot/<int:lot_id>')
def view_spot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    return render_template('view_spot.html', lot=lot, spots=spots)


@app.route('/view_deleting_spot/<int:spot_id>', methods=['GET', 'POST'])
def view_deleting_spot(spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)

    if request.method == 'POST':
        if spot.status == 'A':
            # Decrement total spots
            lot = ParkingLot.query.get(spot.lot_id)
            if lot.total_spots > 0:
                lot.total_spots -= 1

            # Delete the spot
            db.session.delete(spot)
            db.session.commit()
            flash("Spot deleted successfully.")
        else:
            flash("Only available spots can be deleted.")
        return redirect(url_for('admin_dashboard'))

    return render_template('view_deleting_spot.html', spot=spot)



@app.route('/logout')
def logout():
    session.clear()  
    return redirect(url_for('login'))  





if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        create_admin()
    
    app.run(debug=True)