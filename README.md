# CPS510-A9UI - E-Commerce Database Management System
## Overview
This is a web-based E-Commerce Database Management System built with Flask and Oracle 12c. It provides both CLI and web interfaces for managing an online mall database with comprehensive CRUD operations, advanced querying, and data population features.

## Quick Start
1. **VPN Connection**: Connect to school VPN first
2. **Python Packages**: 
   Type the command in your terminal:
   ```
   pip3 install flask oracledb python-dotenv
   ```

### Running the Application
1. Start the Flask web server:
   Type the command in your terminal
   ```
   python3 web_app.py
   ```

2. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/menu
   ```


## Project Structure
```
CPS510-A9UI/
├── main.py                # Core database operations module
├── web_app.py             # Flask web application
├── README.md              # This file
├── run_web.sh             # Shell script to run web app
├── .env                   # Environment variables (credentials)
├── static/
│   └── css/
│       └── style.css      # CSS styling for web interface
└── templates/
    ├── login.html         # Login page
    ├── menu.html          # Main menu
    ├── create_menu.html   # Create tables submenu
    ├── drop_menu.html     # Drop tables submenu
    ├── populate_menu.html # Populate data submenu
    ├── tables.html        # View all tables
    ├── query_result.html  # Query results display
    └── custom_query.html  # Custom query input
```


## Features
### Database Management
- **Create Tables**: Create all 11 tables or individual tables
- **Drop Tables**: Delete all tables or specific tables
- **Populate Data**: Fill tables with sample data (all tables or individual ones)
- **View Tables**: Display all tables in the database

### Data Operations
- **Insert Data**: Manually insert records into any table
- **Delete Data**: Remove records by primary key
- **Update Data**: Modify existing records
- **Query Data**: 
  - Simple queries (display entire tables)
  - Advanced queries (complex joins and aggregations)
  - Custom SQL queries

### Query Examples (Query Menu)
1. Products with above-average prices grouped by category
2. Count products sharing the same name
3. Users who are sellers or buyers
4. Users who have both bought and sold
5. Users who are buyers but not sellers
6. Custom SQL query execution
