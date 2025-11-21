# CPS510-A9UI - E-Commerce Database System

## Overview
A comprehensive web-based E-Commerce Database Management System built with **Django** and **Oracle 12c**. This application provides a complete e-commerce platform with role-based access control, enabling users to operate as either Customers or Sellers with distinct functionalities tailored to each role.


### Technologies Used
- **Backend Framework**: Django 4.x (Python web framework)
- **Database**: Oracle 12c (primary business data) + SQLite (session management)
- **Frontend**: HTML5, CSS3 with responsive design
- **Database Driver**: python-oracledb for Oracle connectivity
- **Authentication**: Session-based authentication with role management


## Quick Start
   ### First Time Setup (Run Once)
   ```bash
   # 1. Install dependencies
   pip install django oracledb

   # 2. Initialize database
   python manage.py migrate

   # 3. Start the server
   python manage.py runserver
   ```

   ### After First Setup (Every Time)
   ```bash
   # Just start the server - that's it!
   python manage.py runserver
   ```

Then open your browser and visit: **http://127.0.0.1:8000/**

### Prerequisites
- Python 3.8+ (download from python.org if needed)
- University Oracle account credentials
- School VPN connection

---

## How to Use

### Login
1. Open browser at **http://127.0.0.1:8000/**
2. Enter your Oracle username and password (e.g., d53liu)
3. First login automatically creates database tables and sample data

### Select Role
After login, choose your identity:
- **Customer**: Browse products, view orders, manage profile
- **Seller**: View statistics, manage products, view customers and orders

### Features
**Customers can:**
- Browse all products
- View order history
- View and edit personal profile

**Sellers can:**
- View store statistics
- Add/edit/delete products
- View customers who purchased their products
- View orders containing their products

---

## Project Structure

```
CPS510-A9UI/
├── manage.py                    # Django's command-line utility for administrative tasks
├── README.md                    # Project documentation
├── db.sqlite3                   # SQLite database (Django sessions only, not business data)
│
├── shop_project/                # Django project configuration directory
│   ├── __init__.py             # Python package initializer
│   ├── settings.py             # Project settings (database config, installed apps, middleware)
│   ├── urls.py                 # Main URL routing configuration
│   ├── wsgi.py                 # WSGI configuration for deployment
│   ├── asgi.py                 # ASGI configuration for async support
│   └── __pycache__/            # Python bytecode cache
│
├── shop_app/                    # Main application containing business logic
│   ├── __init__.py             # Python package initializer
│   ├── apps.py                 # App configuration
│   ├── urls.py                 # App-specific URL routing
│   ├── views.py                # All view functions and business logic
│   ├── migrations/             # Database migration files
│   │   ├── __init__.py
│   │   └── __pycache__/
│   └── __pycache__/            # Python bytecode cache
│
├── templates/                   # HTML template files (Django template language)
│   ├── login.html              # Login page - Oracle credential input
│   ├── select_role.html        # Role selection page - choose Customer or Seller
│   ├── dashboard.html          # Main dashboard (different views for each role)
│   ├── browse_products.html    # Product browsing page (Customer view)
│   ├── my_orders.html          # Order history page (Customer view)
│   ├── my_profile.html         # Profile view/edit page (Customer view)
│   ├── manage_products.html    # Product management page (Seller view)
│   ├── manage_customers.html   # Customer list page (Seller view)
│   └── manage_orders.html      # Order management page (Seller view)
│
└── static/                      # Static files (CSS, JavaScript, images)
    └── css/
        └── style.css           # Main stylesheet for the entire application
```
---

## Database Info
System uses 11 Oracle tables:
- Users: A3_USERS, UserName, USERS_ADMIN, USERS_SELLER, USERS_CUSTOMER
- Products: CATEGORY, PRODUCT, ORDER_PRICE
- Orders: ORDERS, ORDER_ITEM, PAYMENT

**Sample data included:**
- 4 customer accounts
- 3 seller accounts
- 6 products
- 8 orders