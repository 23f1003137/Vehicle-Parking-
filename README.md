# SafeLot Parking Management System

A web-based parking lot management system built with Flask and SQLAlchemy. This project allows users to register, book parking spots, release them, and view their booking history. Admins can manage parking lots, spots, and users via a dashboard.

---

## Features

- User registration and login
- Admin and user dashboards
- Add, edit, and delete parking lots (admin)
- Book and release parking spots (user)
- View parking history and summary
- Responsive UI with Bootstrap

---

## Project Structure

```
mad-1 project/
│
├── app.py                # Main Flask application and routes
├── models.py             # SQLAlchemy models
├── requirement.txt       # Python dependencies
├── templates/            # HTML templates (Jinja2)
│   ├── admin_dashboard.html
│   ├── user_dashboard.html
│   ├── login.html
│   ├── register.html
│   ├── new_parking_lot.html
│   ├── edit_parking_lot.html
│   ├── book_spot.html
│   ├── release_spot.html
│   ├── occupied_parking_spot.html
│   ├── view_spot.html
│   └── view_deleting_spot.html
├── static/               # Static files (images, CSS, JS)
│   └── image/
│       └── parking-bg.webp
└── instance/
    └── example.db        # SQLite database file
```

---

## Setup Instructions

1. **Clone the repository**

2. **Install dependencies**

   ```sh
   pip install -r requirement.txt
   ```

3. **Run the application**

   ```sh
   python app.py
   ```

   The app will be available at [http://127.0.0.1:5000](http://127.0.0.1:5000).

4. **Default Admin**

   - Email: `admin@gmail.com`
   - Password: `12345678`

---

## Database

- SQLite is used by default (`instance/example.db`).
- Models are defined in [`models.py`](models.py).

---

## Main Files

- [`app.py`](app.py): Main Flask application and routes.
- [`models.py`](models.py): SQLAlchemy models.
- Templates: HTML files in the `templates/` directory.

---

## License

MIT License

---

**Note:** For development only. Do not use the provided secret key in production.