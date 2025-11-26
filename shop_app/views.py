import oracledb
from django.shortcuts import render, redirect
from django.contrib import messages
import os
import json
import datetime


def get_db_connection(user=None, password=None):
    """Get Oracle database connection"""
    # If user and password are provided, use them; otherwise use environment variables
    if user is None:
        user = os.getenv('DB_USER')
    if password is None:
        password = os.getenv('DB_PASS')
    
    host = os.getenv('DB_HOST', 'oracle12c.scs.ryerson.ca')
    port = int(os.getenv('PORT', 1521))
    sid = os.getenv('SID', 'orcl12c')
    
    connection = oracledb.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        sid=sid
    )
    return connection


def drop_tables(cursor, connection):
    """Drop all tables"""
    drop_stmts = [
        "DROP TABLE users_customer CASCADE CONSTRAINTS",
        "DROP TABLE users_seller CASCADE CONSTRAINTS",
        "DROP TABLE users_admin CASCADE CONSTRAINTS",
        "DROP TABLE A3_USERS CASCADE CONSTRAINTS",
        "DROP TABLE UserName CASCADE CONSTRAINTS",
        "DROP TABLE PRODUCT CASCADE CONSTRAINTS",
        "DROP TABLE CATEGORY CASCADE CONSTRAINTS",
        "DROP TABLE ORDERS CASCADE CONSTRAINTS",
        "DROP TABLE PAYMENT CASCADE CONSTRAINTS",
        "DROP TABLE ORDER_ITEM CASCADE CONSTRAINTS",
        "DROP TABLE ORDER_PRICE CASCADE CONSTRAINTS"
    ]
    
    for stmt in drop_stmts:
        try:
            cursor.execute(stmt)
        except Exception:
            pass
    
    connection.commit()


def create_tables(cursor, connection):
    """Create all tables"""
    try:
        cursor.execute('''
            CREATE TABLE A3_USERS (
                user_id VARCHAR2(20) CONSTRAINT pk_a3_users PRIMARY KEY,
                first_name VARCHAR2(50) CONSTRAINT nn_a3_user_firstname NOT NULL,
                last_name VARCHAR2(50) CONSTRAINT nn_a3_user_lastname NOT NULL,
                status VARCHAR2(20) CONSTRAINT ck_a3_users_status CHECK (status IN ('Active','Inactive')),
                email VARCHAR2(100)  CONSTRAINT uq_a3_users_email UNIQUE,
                phone VARCHAR2(20) DEFAULT '-',
                street VARCHAR2(100) DEFAULT '-',
                city VARCHAR2(50) DEFAULT '-',
                province VARCHAR2(50) DEFAULT '-',
                postal_code VARCHAR2(20) DEFAULT '-',
                user_type VARCHAR2(20) CONSTRAINT ck_a3_users_user_type CHECK (user_type IN ('ADMIN','SELLER','CUSTOMER'))
            )
        ''')

        cursor.execute('''
            CREATE TABLE UserName (
              first_name VARCHAR2(50) NOT NULL,
              last_name VARCHAR2(50) NOT NULL,
              fullname VARCHAR2(255) NOT NULL,
              CONSTRAINT pk_username PRIMARY KEY (first_name, last_name)
            )
        ''')

        cursor.execute('''
            CREATE TABLE USERS_ADMIN (
                admin_id VARCHAR2(20)
                    CONSTRAINT pk_users_admin PRIMARY KEY
                    CONSTRAINT fk_users_admin_user
                        REFERENCES A3_USERS (user_id) ON DELETE CASCADE,
                role_admin VARCHAR2(50)
                    CONSTRAINT nn_usersAdmin_role NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE USERS_SELLER (
                seller_id VARCHAR2(20)
                    CONSTRAINT pk_users_seller PRIMARY KEY
                    CONSTRAINT fk_users_seller_user
                        REFERENCES A3_USERS (user_id) ON DELETE CASCADE,
                store_name VARCHAR2(100)
                    CONSTRAINT nn_usersseller_storename NOT NULL,
                admin_id VARCHAR2(20)
                    CONSTRAINT fk_users_seller_admin
                        REFERENCES USERS_ADMIN(admin_id)
                        ON DELETE SET NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE USERS_CUSTOMER (
                customer_id VARCHAR2(20)
                    CONSTRAINT pk_users_customer PRIMARY KEY
                    CONSTRAINT fk_users_customer_user
                        REFERENCES A3_USERS (user_id) ON DELETE CASCADE,
                membership_id VARCHAR2(50) DEFAULT '-' ,
                date_of_birth DATE
            )
        ''')

        cursor.execute('''
            CREATE TABLE CATEGORY (
                category_id   VARCHAR2(20)
                    CONSTRAINT pk_category PRIMARY KEY,
                name_category          VARCHAR2(100) NOT NULL,
                description_category   VARCHAR2(255)
            )
        ''')

        cursor.execute('''
            CREATE TABLE PRODUCT(
                product_id  VARCHAR2(20)
                    CONSTRAINT pk_product PRIMARY KEY,
                name_product         VARCHAR2(100) NOT NULL,
                description_product  VARCHAR2(255),
                price        NUMBER(10,2) NOT NULL
                    CONSTRAINT ck_product_price CHECK (price >= 0),
                stock        NUMBER NOT NULL
                    CONSTRAINT ck_product_stock CHECK (stock >= 0),
                seller_id     VARCHAR2(20) NOT NULL
                    CONSTRAINT fk_product_seller
                    REFERENCES USERS_SELLER(seller_id)
                    ON DELETE CASCADE,
                category_id   VARCHAR2(20)
                    CONSTRAINT fk_product_category
                    REFERENCES CATEGORY(category_id)
                    ON DELETE SET NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE ORDERS (
                order_id         VARCHAR2(20)
                    CONSTRAINT pk_orders PRIMARY KEY,
                customer_id      VARCHAR2(20) NOT NULL
                    CONSTRAINT fk_orders_customer
                    REFERENCES USERS_CUSTOMER(customer_id)
                    ON DELETE CASCADE,
                order_date       DATE NOT NULL,
                shipment_status  VARCHAR2(20) NOT NULL
                    CONSTRAINT ck_orders_shipment_status
                    CHECK (shipment_status IN ('Pending','Shipped','In Transit','Delivered'))
            )
        ''')

        cursor.execute('''
            CREATE TABLE PAYMENT (
                payment_id     VARCHAR2(20)
                    CONSTRAINT pk_payment PRIMARY KEY,
                order_id       VARCHAR2(20) NOT NULL
                    CONSTRAINT fk_payment_order
                    REFERENCES ORDERS(order_id)
                    ON DELETE CASCADE,
                payment_status VARCHAR2(20) NOT NULL
                    CONSTRAINT ck_payment_status
                    CHECK (payment_status IN ('Pending','Paid','Failed')),
                total_amount   NUMBER(10,2) NOT NULL
                    CONSTRAINT ck_payment_total CHECK (total_amount >= 0)
            )
        ''')

        cursor.execute('''
            CREATE TABLE ORDER_ITEM (
                order_id    VARCHAR2(20) NOT NULL,
                product_id  VARCHAR2(20) NOT NULL,
                quantity    NUMBER NOT NULL
                    CONSTRAINT ck_orderitem_quantity CHECK (quantity > 0),

                CONSTRAINT pk_order_item PRIMARY KEY (order_id, product_id),

                CONSTRAINT fk_orderitem_order FOREIGN KEY (order_id)
                    REFERENCES ORDERS(order_id) ON DELETE CASCADE,
                CONSTRAINT fk_orderitem_product FOREIGN KEY (product_id)
                    REFERENCES PRODUCT(product_id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE ORDER_PRICE (
              product_id VARCHAR2(20) PRIMARY KEY,
              unit_price NUMBER(10,2) NOT NULL,
              CONSTRAINT fk_order_price_product
                FOREIGN KEY (product_id)
                REFERENCES PRODUCT(product_id)
                ON DELETE CASCADE
            )
        ''')

        connection.commit()
        return True
    except Exception as e:
        connection.rollback()
        print(f"Error creating tables: {e}")
        return False


def populate_tables(cursor, connection):
    """Populate sample data"""
    try:
        # A3_USERS table
        cursor.execute("""
            INSERT INTO A3_USERS (user_id, first_name, last_name, status, email, phone, street, city, province, postal_code, user_type)
            VALUES ('CUS1', 'Decor', 'Delights', 'Active', 'Decor@hotmail.com', '416-789-5678',
                    '890 King Street West', 'Toronto', 'ON', 'M5V 1N8', 'CUSTOMER')
        """)
        cursor.execute("""
            INSERT INTO A3_USERS (user_id, first_name, last_name, status, email, phone, street, city, province, postal_code, user_type)
            VALUES ('CUS2', 'Emily', 'Brown', 'Active', 'emily.brown@gmail.com', '416-123-4567',
                    '123 Queen Street East', 'Toronto', 'ON', 'M5A 1S2', 'CUSTOMER')
        """)
        cursor.execute("""
            INSERT INTO A3_USERS (user_id, first_name, last_name, status, email, phone, street, city, province, postal_code, user_type)
            VALUES ('CUS3', 'Alexander', 'Garcia', 'Inactive', 'alex.garcia@yahoo.com', '647-555-7890',
                    '456 Bay Street', 'Toronto', 'ON', 'M5H 2Y4', 'CUSTOMER')
        """)
        cursor.execute("""
            INSERT INTO A3_USERS (user_id, first_name, last_name, status, email, phone, street, city, province, postal_code, user_type)
            VALUES ('CUS4', 'Bella', 'Jones', 'Active', 'bella.jones@hotmail.com', '647-987-6543',
                    '789 Dundas Street West', 'Toronto', 'ON', 'M5T 1H3', 'CUSTOMER')
        """)
        cursor.execute("""
            INSERT INTO A3_USERS (user_id, first_name, last_name, status, email, phone, street, city, province, postal_code, user_type)
            VALUES ('S1', 'John', 'Smith', 'Active', 'John@hotmail.com', '416-234-5342',
                    '20 Bloor Street East', 'Toronto', 'ON', 'M4W 1A8', 'SELLER')
        """)
        cursor.execute("""
            INSERT INTO A3_USERS (user_id, first_name, last_name, status, email, phone, street, city, province, postal_code, user_type)
            VALUES ('S2', 'Amy', 'Smith', 'Active', 'Amy@yahoo.com', '347-555-2198',
                    '360 Queen Street West', 'Toronto', 'ON', 'M5D 8N1', 'SELLER')
        """)
        cursor.execute("""
            INSERT INTO A3_USERS (user_id, first_name, last_name, status, email, phone, street, city, province, postal_code, user_type)
            VALUES ('S4', 'James', 'F', 'Inactive', 'jmf@yahoo.com', '347-534-2876',
                    '920 Queen Street West', 'Toronto', 'ON', 'M5C 2D4', 'SELLER')
        """)
        cursor.execute("""
            INSERT INTO A3_USERS (user_id, first_name, last_name, status, email, phone, street, city, province, postal_code, user_type)
            VALUES ('A1', 'Daniel', 'Lee', 'Inactive', 'daniel.lee@hotmail.com', '416-777-4821',
                    '88 Bloor Street East', 'Toronto', 'ON', 'M4W 3G9', 'ADMIN')
        """)
        cursor.execute("""
            INSERT INTO A3_USERS (user_id, first_name, last_name, status, email, phone, street, city, province, postal_code, user_type)
            VALUES ('A2', 'Sophia', 'Wang', 'Active', 'sophia.wang@gmail.com', '647-882-3157',
                    '12 King Street West', 'Toronto', 'ON', 'M5H 1A1', 'ADMIN')
        """)
        cursor.execute("""
            INSERT INTO A3_USERS (user_id, first_name, last_name, status, email, phone, street, city, province, postal_code, user_type)
            VALUES ('A3', 'Michael', 'Brown', 'Active', 'michael.brown@yahoo.com', '416-331-9042',
                    '205 Yonge Street', 'Toronto', 'ON', 'M5B 2H1', 'ADMIN')
        """)

        # UserName table
        cursor.execute("INSERT INTO UserName (first_name, last_name, fullname) VALUES ('Decor', 'Delights', 'Decor Delights')")
        cursor.execute("INSERT INTO UserName (first_name, last_name, fullname) VALUES ('Emily', 'Brown', 'Emily Brown')")
        cursor.execute("INSERT INTO UserName (first_name, last_name, fullname) VALUES ('Alexander', 'Garcia', 'Alexander Garcia')")
        cursor.execute("INSERT INTO UserName (first_name, last_name, fullname) VALUES ('Bella', 'Jones', 'Bella Jones')")
        cursor.execute("INSERT INTO UserName (first_name, last_name, fullname) VALUES ('John', 'Smith', 'John Smith')")
        cursor.execute("INSERT INTO UserName (first_name, last_name, fullname) VALUES ('Amy', 'Smith', 'Amy Smith')")
        cursor.execute("INSERT INTO UserName (first_name, last_name, fullname) VALUES ('James', 'F', 'James F')")
        cursor.execute("INSERT INTO UserName (first_name, last_name, fullname) VALUES ('Daniel', 'Lee', 'Daniel Lee')")
        cursor.execute("INSERT INTO UserName (first_name, last_name, fullname) VALUES ('Sophia', 'Wang', 'Sophia Wang')")
        cursor.execute("INSERT INTO UserName (first_name, last_name, fullname) VALUES ('Michael', 'Brown', 'Michael Brown')")

        # USERS_CUSTOMER
        cursor.execute("INSERT INTO USERS_CUSTOMER (customer_id, membership_id, date_of_birth) VALUES ('CUS1', NULL, NULL)")
        cursor.execute("INSERT INTO USERS_CUSTOMER (customer_id, membership_id, date_of_birth) VALUES ('CUS2', '123456', DATE '2001-01-12')")
        cursor.execute("INSERT INTO USERS_CUSTOMER (customer_id, membership_id, date_of_birth) VALUES ('CUS3', '654321', NULL)")
        cursor.execute("INSERT INTO USERS_CUSTOMER (customer_id, membership_id, date_of_birth) VALUES ('CUS4', NULL, DATE '1994-08-16')")

        # USERS_ADMIN
        cursor.execute("INSERT INTO USERS_ADMIN (admin_id, role_admin) VALUES ('A1', 'SECURITY_ADMIN')")
        cursor.execute("INSERT INTO USERS_ADMIN (admin_id, role_admin) VALUES ('A2', 'SECURITY_ADMIN')")
        cursor.execute("INSERT INTO USERS_ADMIN (admin_id, role_admin) VALUES ('A3', 'System_ADMIN')")

        # USERS_SELLER
        cursor.execute("INSERT INTO USERS_SELLER (seller_id, store_name, admin_id) VALUES ('S1', 'Toy Shop', 'A1')")
        cursor.execute("INSERT INTO USERS_SELLER (seller_id, store_name, admin_id) VALUES ('S2', 'Women Shop', 'A1')")
        cursor.execute("INSERT INTO USERS_SELLER (seller_id, store_name, admin_id) VALUES ('S4', 'Women Store', 'A3')")

        # CATEGORY
        cursor.execute("""
            INSERT INTO CATEGORY (category_id, name_category, description_category)
            VALUES ('C1001', 'Sports toy', 'Toys for children to engage in sports activities')
        """)
        cursor.execute("""
            INSERT INTO CATEGORY (category_id, name_category, description_category)
            VALUES ('C1002', 'Women clothes', 'Tops, bottoms, coats and dresses')
        """)

        # PRODUCT
        cursor.execute("""
            INSERT INTO PRODUCT (product_id, name_product, description_product, price, stock, seller_id, category_id)
            VALUES ('P0001', 'Basketball', 'Authentic Indoor Outdoor Basketball', 15.99, 380, 'S1', 'C1001')
        """)
        cursor.execute("""
            INSERT INTO PRODUCT (product_id, name_product, description_product, price, stock, seller_id, category_id)
            VALUES ('P0002', 'Summer Dress', 'V Neck Ruffle Short Sleeve Casual Dress', 36.99, 210, 'S2', 'C1002')
        """)
        cursor.execute("""
            INSERT INTO PRODUCT (product_id, name_product, description_product, price, stock, seller_id, category_id)
            VALUES ('P0003', 'Soccer Ball', 'Professional Soccer Ball', 25.99, 150, 'S1', 'C1001')
        """)
        cursor.execute("""
            INSERT INTO PRODUCT (product_id, name_product, description_product, price, stock, seller_id, category_id)
            VALUES ('P0004', 'Winter Coat', 'Short Insulated Puffer Jacket', 120.00, 75, 'S2', 'C1002')
        """)
        cursor.execute("""
            INSERT INTO PRODUCT (product_id, name_product, description_product, price, stock, seller_id, category_id)
            VALUES ('P0005', 'Yoga Mat', 'Anti-Tear Pilates Yoga Mat', 45.50, 90, 'S4', 'C1002')
        """)

        # ORDER_PRICE
        cursor.execute("INSERT INTO ORDER_PRICE (product_id, unit_price) VALUES ('P0001', 15.99)")
        cursor.execute("INSERT INTO ORDER_PRICE (product_id, unit_price) VALUES ('P0002', 36.99)")
        cursor.execute("INSERT INTO ORDER_PRICE (product_id, unit_price) VALUES ('P0003', 25.99)")
        cursor.execute("INSERT INTO ORDER_PRICE (product_id, unit_price) VALUES ('P0004', 120.00)")
        cursor.execute("INSERT INTO ORDER_PRICE (product_id, unit_price) VALUES ('P0005', 45.50)")

        # ORDERS
        cursor.execute("""
            INSERT INTO ORDERS (order_id, customer_id, order_date, shipment_status)
            VALUES ('O001', 'CUS2', DATE '2025-05-03', 'In Transit')
        """)
        cursor.execute("""
            INSERT INTO ORDERS (order_id, customer_id, order_date, shipment_status)
            VALUES ('O002', 'CUS1', DATE '2025-07-30', 'Delivered')
        """)
        cursor.execute("""
            INSERT INTO ORDERS (order_id, customer_id, order_date, shipment_status)
            VALUES ('O003', 'CUS2', DATE '2025-05-29', 'Shipped')
        """)
        cursor.execute("""
            INSERT INTO ORDERS (order_id, customer_id, order_date, shipment_status)
            VALUES ('O004', 'CUS1', DATE '2025-01-16', 'Delivered')
        """)
        cursor.execute("""
            INSERT INTO ORDERS (order_id, customer_id, order_date, shipment_status)
            VALUES ('O005', 'CUS3', DATE '2025-09-08', 'In Transit')
        """)
        cursor.execute("""
            INSERT INTO ORDERS (order_id, customer_id, order_date, shipment_status)
            VALUES ('O006', 'CUS1', DATE '2025-05-03', 'Delivered')
        """)

        # PAYMENT
        cursor.execute("INSERT INTO PAYMENT (payment_id, order_id, payment_status, total_amount) VALUES ('EFT0001', 'O001', 'Paid', 31.98)")
        cursor.execute("INSERT INTO PAYMENT (payment_id, order_id, payment_status, total_amount) VALUES ('EFT0002', 'O002', 'Pending', 110.97)")
        cursor.execute("INSERT INTO PAYMENT (payment_id, order_id, payment_status, total_amount) VALUES ('EFT0003', 'O003', 'Paid', 25.99)")
        cursor.execute("INSERT INTO PAYMENT (payment_id, order_id, payment_status, total_amount) VALUES ('EFT0004', 'O004', 'Paid', 240.00)")
        cursor.execute("INSERT INTO PAYMENT (payment_id, order_id, payment_status, total_amount) VALUES ('EFT0005', 'O005', 'Pending', 182.00)")
        cursor.execute("INSERT INTO PAYMENT (payment_id, order_id, payment_status, total_amount) VALUES ('EFT0006', 'O006', 'Paid', 79.95)")

        # ORDER_ITEM 
        cursor.execute("INSERT INTO ORDER_ITEM (order_id, product_id, quantity) VALUES ('O001', 'P0001', 2)")
        cursor.execute("INSERT INTO ORDER_ITEM (order_id, product_id, quantity) VALUES ('O002', 'P0002', 3)")
        cursor.execute("INSERT INTO ORDER_ITEM (order_id, product_id, quantity) VALUES ('O003', 'P0003', 1)")
        cursor.execute("INSERT INTO ORDER_ITEM (order_id, product_id, quantity) VALUES ('O004', 'P0004', 2)")
        cursor.execute("INSERT INTO ORDER_ITEM (order_id, product_id, quantity) VALUES ('O005', 'P0005', 4)")
        cursor.execute("INSERT INTO ORDER_ITEM (order_id, product_id, quantity) VALUES ('O006', 'P0001', 5)")
        
        # duplicate name product (query 2)
        cursor.execute("INSERT INTO PRODUCT (product_id, name_product, description_product, price, stock, seller_id, category_id) "
                    "VALUES ('P0006', 'Basketball', 'Alternate Basketball Item', 18.99, 50, 'S1', 'C1001')")

        cursor.execute("INSERT INTO ORDER_PRICE (product_id, unit_price) "
                    "VALUES ('P0006', 18.99)")

        connection.commit()
        return True
    except Exception as e:
        connection.rollback()
        print(f"Error populating tables: {e}")
        return False


def login_view(request):
    """Login view - Login with Oracle account and create tables and data"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Validate username and password are not empty
        if username and password:
            try:
                # Use input Oracle account credentials to connect to database
                connection = get_db_connection(user=username, password=password)
                cursor = connection.cursor()
                
                # Drop old tables if they exist
                drop_tables(cursor, connection)
                
                # Create tables
                if create_tables(cursor, connection):
                    # Populate data
                    if populate_tables(cursor, connection):
                        cursor.close()
                        connection.close()
                        
                        # Set session, save Oracle account information
                        request.session['logged_in'] = True
                        request.session['db_user'] = username
                        request.session['db_pass'] = password
                        messages.success(request, 'Database initialized successfully!')
                        return redirect('select_role')
                    else:
                        messages.error(request, 'Failed to populate data')
                else:
                    messages.error(request, 'Failed to create tables')
                    
                cursor.close()
                connection.close()
            except oracledb.DatabaseError as e:
                error_obj, = e.args
                messages.error(request, f'Oracle Database Error: {error_obj.message}')
            except Exception as e:
                messages.error(request, f'Connection failed. Please check your Oracle username and password.')
        else:
            messages.error(request, 'Please enter both Oracle username and password')
    
    return render(request, 'login.html')


def select_role_view(request):
    """User role selection page"""
    if not request.session.get('logged_in'):
        return redirect('login')
    
    db_user = request.session.get('db_user')
    db_pass = request.session.get('db_pass')
    
    try:
        connection = get_db_connection(user=db_user, password=db_pass)
        cursor = connection.cursor()
        
        # Get all Customer information
        cursor.execute("""
            SELECT u.user_id, u.first_name || ' ' || u.last_name as full_name, 
                   u.email, u.city, u.province
            FROM A3_USERS u
            JOIN USERS_CUSTOMER uc ON u.user_id = uc.customer_id
            ORDER BY u.user_id
        """)
        
        customers = []
        for row in cursor.fetchall():
            customers.append({
                'user_id': row[0],
                'full_name': row[1],
                'email': row[2],
                'city': row[3] or 'N/A',
                'province': row[4] or 'N/A'
            })
        
        # Get all Seller information
        cursor.execute("""
            SELECT u.user_id, u.first_name || ' ' || u.last_name as full_name, 
                   u.email, us.store_name, u.city, u.province
            FROM A3_USERS u
            JOIN USERS_SELLER us ON u.user_id = us.seller_id
            ORDER BY u.user_id
        """)
        
        sellers = []
        for row in cursor.fetchall():
            sellers.append({
                'user_id': row[0],
                'full_name': row[1],
                'email': row[2],
                'store_name': row[3],
                'city': row[4] or 'N/A',
                'province': row[5] or 'N/A'
            })
        
        cursor.close()
        connection.close()
        
        context = {
            'customers': customers,
            'sellers': sellers
        }
        
    except Exception as e:
        context = {
            'customers': [],
            'sellers': [],
            'error': str(e)
        }
    
    return render(request, 'select_role.html', context)


def set_role_view(request):
    """Handle role selection and set session"""
    if not request.session.get('logged_in'):
        return redirect('login')
    
    if request.method == 'POST':
        role = request.POST.get('role')
        
        if role:
            # Parse role information: "CUSTOMER:CUS1" or "SELLER:S1"
            parts = role.split(':')
            if len(parts) == 2:
                user_type = parts[0]  # CUSTOMER or SELLER
                user_id = parts[1]     # CUS1, CUS2, ... or S1, S2, S4
                
                # Save to session
                request.session['user_type'] = user_type
                request.session['user_id'] = user_id  # Now Seller also has user_id
                request.session['is_admin'] = False  # No more global admin mode
                
                return redirect('dashboard')
        
        messages.error(request, 'Please select a valid role')
    
    return redirect('select_role')


def dashboard_view(request):
    """Dashboard view"""
    if not request.session.get('logged_in'):
        return redirect('login')
    
    # Check if role is selected
    if not request.session.get('user_type'):
        return redirect('select_role')
    
    # Get Oracle account info and user role from session
    db_user = request.session.get('db_user')
    db_pass = request.session.get('db_pass')
    user_type = request.session.get('user_type')
    user_id = request.session.get('user_id')
    is_admin = request.session.get('is_admin', False)
    
    try:
        connection = get_db_connection(user=db_user, password=db_pass)
        cursor = connection.cursor()
        
        # Display different statistics based on role
        if user_type == 'CUSTOMER':
            # Customer only sees their own statistics
            cursor.execute("SELECT COUNT(*) FROM ORDERS WHERE customer_id = :user_id", {'user_id': user_id})
            orders_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM PRODUCT")
            total_products = cursor.fetchone()[0]
            
            context = {
                'user_type': user_type,
                'user_id': user_id,
                'orders_count': orders_count,
                'total_products': total_products,
                'db_user': db_user,
            }
        else:
            # Seller only sees their own store statistics
            # Get store name
            cursor.execute("""
                SELECT us.store_name, u.first_name || ' ' || u.last_name as full_name
                FROM USERS_SELLER us
                JOIN A3_USERS u ON us.seller_id = u.user_id
                WHERE us.seller_id = :seller_id
            """, {'seller_id': user_id})
            seller_info = cursor.fetchone()
            store_name = seller_info[0] if seller_info else 'Unknown Store'
            seller_name = seller_info[1] if seller_info else 'Unknown Seller'
            
            # Only count this Seller's products
            cursor.execute("SELECT COUNT(*) FROM PRODUCT WHERE seller_id = :seller_id", {'seller_id': user_id})
            products_count = cursor.fetchone()[0]
            
            # Count customers who purchased this Seller's products
            cursor.execute("""
                SELECT COUNT(DISTINCT o.customer_id)
                FROM ORDERS o
                JOIN ORDER_ITEM oi ON o.order_id = oi.order_id
                JOIN PRODUCT p ON oi.product_id = p.product_id
                WHERE p.seller_id = :seller_id
            """, {'seller_id': user_id})
            customers_count = cursor.fetchone()[0]
            
            # Count orders containing this Seller's products
            cursor.execute("""
                SELECT COUNT(DISTINCT o.order_id)
                FROM ORDERS o
                JOIN ORDER_ITEM oi ON o.order_id = oi.order_id
                JOIN PRODUCT p ON oi.product_id = p.product_id
                WHERE p.seller_id = :seller_id
            """, {'seller_id': user_id})
            orders_count = cursor.fetchone()[0]
            
            # Count this Seller's product categories
            cursor.execute("""
                SELECT COUNT(DISTINCT category_id) 
                FROM PRODUCT 
                WHERE seller_id = :seller_id AND category_id IS NOT NULL
            """, {'seller_id': user_id})
            categories_count = cursor.fetchone()[0]
            
            # Calculate total revenue
            cursor.execute("""
                SELECT COALESCE(SUM(oi.quantity * op.unit_price), 0)
                FROM ORDER_ITEM oi
                JOIN PRODUCT p ON oi.product_id = p.product_id
                JOIN ORDER_PRICE op ON oi.product_id = op.product_id
                WHERE p.seller_id = :seller_id
            """, {'seller_id': user_id})
            total_revenue = cursor.fetchone()[0]
            
            context = {
                'user_type': user_type,
                'user_id': user_id,
                'store_name': store_name,
                'seller_name': seller_name,
                'products_count': products_count,
                'customers_count': customers_count,
                'orders_count': orders_count,
                'categories_count': categories_count,
                'total_revenue': float(total_revenue) if total_revenue else 0,
                'db_user': db_user,
            }
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        context = {
            'user_type': user_type,
            'db_user': db_user,
            'error': str(e)
        }
    
    return render(request, 'dashboard.html', context)


def manage_products_view(request):
    """Manage products view - Display product list"""
    if not request.session.get('logged_in'):
        return redirect('login')
    
    if not request.session.get('user_type'):
        return redirect('select_role')
    
    db_user = request.session.get('db_user')
    db_pass = request.session.get('db_pass')
    user_type = request.session.get('user_type')
    user_id = request.session.get('user_id')
    
    if user_type != 'SELLER':
        return redirect('dashboard')
    
    try:
        connection = get_db_connection(user=db_user, password=db_pass)
        cursor = connection.cursor()
        
        # Get store information
        cursor.execute("""
            SELECT us.store_name
            FROM USERS_SELLER us
            WHERE us.seller_id = :seller_id
        """, {'seller_id': user_id})
        seller_info = cursor.fetchone()
        store_name = seller_info[0] if seller_info else 'Unknown Store'
        
        # Only query this Seller's products
        cursor.execute("""
            SELECT p.product_id, p.name_product, p.description_product, 
                   p.price, p.stock, p.seller_id, 
                   u.first_name || ' ' || u.last_name as seller_name,
                   c.name_category
            FROM PRODUCT p
            LEFT JOIN USERS_SELLER s ON p.seller_id = s.seller_id
            LEFT JOIN A3_USERS u ON s.seller_id = u.user_id
            LEFT JOIN CATEGORY c ON p.category_id = c.category_id
            WHERE p.seller_id = :seller_id
            ORDER BY p.product_id
        """, {'seller_id': user_id})
        
        products = []
        for row in cursor.fetchall():
            products.append({
                'product_id': row[0],
                'name': row[1],
                'description': row[2] or '',
                'price': row[3],
                'stock': row[4],
                'seller_id': row[5],
                'seller_name': row[6] or 'Unknown',
                'category': row[7] or 'No Category'
            })
        
        # Get all categories
        cursor.execute("SELECT category_id, name_category FROM CATEGORY ORDER BY name_category")
        categories = [{'category_id': row[0], 'name': row[1]} for row in cursor.fetchall()]
        
        cursor.close()
        connection.close()
        
        context = {
            'products': products,
            'categories': categories,
            'user_type': user_type,
            'user_id': user_id,
            'store_name': store_name,
            'db_user': db_user,
        }
        
    except Exception as e:
        messages.error(request, f'Database error: {str(e)}')
        context = {
            'products': [],
            'categories': [],
            'user_type': user_type,
            'user_id': user_id,
            'db_user': db_user,
        }
    
    return render(request, 'manage_products.html', context)


def manage_customers_view(request):
    """Manage customers view - Seller feature"""
    if not request.session.get('logged_in'):
        return redirect('login')
    
    if not request.session.get('user_type'):
        return redirect('select_role')
    
    db_user = request.session.get('db_user')
    db_pass = request.session.get('db_pass')
    user_type = request.session.get('user_type')
    user_id = request.session.get('user_id')
    
    if user_type != 'SELLER':
        return redirect('dashboard')
    
    try:
        connection = get_db_connection(user=db_user, password=db_pass)
        cursor = connection.cursor()
        
        # Get store information
        cursor.execute("""
            SELECT us.store_name
            FROM USERS_SELLER us
            WHERE us.seller_id = :seller_id
        """, {'seller_id': user_id})
        seller_info = cursor.fetchone()
        store_name = seller_info[0] if seller_info else 'Unknown Store'
        
        # Only query customers who purchased this Seller's products and their statistics (exclude Seller themselves)
        cursor.execute("""
            SELECT 
                u.user_id,
                u.first_name || ' ' || u.last_name as full_name,
                u.email,
                u.phone,
                u.city,
                u.province,
                u.status,
                uc.membership_id,
                uc.date_of_birth,
                COUNT(DISTINCT o.order_id) as total_orders,
                COALESCE(SUM(oi.quantity * op.unit_price), 0) as total_spent
            FROM A3_USERS u
            JOIN USERS_CUSTOMER uc ON u.user_id = uc.customer_id
            JOIN ORDERS o ON u.user_id = o.customer_id
            JOIN ORDER_ITEM oi ON o.order_id = oi.order_id
            JOIN PRODUCT p ON oi.product_id = p.product_id
            JOIN ORDER_PRICE op ON oi.product_id = op.product_id
            WHERE p.seller_id = :seller_id AND u.user_id != :seller_id
            GROUP BY u.user_id, u.first_name, u.last_name, u.email, u.phone, 
                     u.city, u.province, u.status, uc.membership_id, uc.date_of_birth
            ORDER BY u.user_id
        """, {'seller_id': user_id})
        
        customers = []
        for row in cursor.fetchall():
            # Handle date format
            date_of_birth = row[8]
            if date_of_birth:
                if isinstance(date_of_birth, datetime.datetime):
                    date_of_birth = date_of_birth.strftime('%Y-%m-%d')
                else:
                    date_of_birth = str(date_of_birth)
            
            customers.append({
                'user_id': row[0],
                'full_name': row[1],
                'email': row[2],
                'phone': row[3] or 'N/A',
                'city': row[4] or 'N/A',
                'province': row[5] or 'N/A',
                'status': row[6],
                'membership_id': row[7] or 'No Membership',
                'date_of_birth': date_of_birth or 'N/A',
                'total_orders': row[9],
                'total_spent': float(row[10]) if row[10] else 0
            })
        
        cursor.close()
        connection.close()
        
        # Serialize customer data to JSON
        customers_json = json.dumps(customers)
        
        context = {
            'customers': customers,
            'customers_json': customers_json,
            'user_type': user_type,
            'user_id': user_id,
            'store_name': store_name,
            'db_user': db_user,
        }
        
    except Exception as e:
        context = {
            'customers': [],
            'error': str(e),
            'user_type': user_type,
            'user_id': user_id,
            'db_user': db_user,
        }
    
    return render(request, 'manage_customers.html', context)


def manage_orders_view(request):
    """Manage orders view"""
    if not request.session.get('logged_in'):
        return redirect('login')
    
    if not request.session.get('user_type'):
        return redirect('select_role')
    
    db_user = request.session.get('db_user')
    db_pass = request.session.get('db_pass')
    user_type = request.session.get('user_type')
    user_id = request.session.get('user_id')
    
    if user_type != 'SELLER':
        return redirect('dashboard')
    
    try:
        connection = get_db_connection(user=db_user, password=db_pass)
        cursor = connection.cursor()
        
        # Get store information
        cursor.execute("""
            SELECT us.store_name
            FROM USERS_SELLER us
            WHERE us.seller_id = :seller_id
        """, {'seller_id': user_id})
        seller_info = cursor.fetchone()
        store_name = seller_info[0] if seller_info else 'Unknown Store'
        
        # Query orders containing this Seller's products
        cursor.execute("""
            SELECT DISTINCT
                o.order_id,
                o.customer_id,
                u.first_name || ' ' || u.last_name as customer_name,
                o.order_date,
                o.shipment_status,
                py.payment_status,
                py.total_amount
            FROM ORDERS o
            JOIN ORDER_ITEM oi ON o.order_id = oi.order_id
            JOIN PRODUCT p ON oi.product_id = p.product_id
            JOIN A3_USERS u ON o.customer_id = u.user_id
            LEFT JOIN PAYMENT py ON o.order_id = py.order_id
            WHERE p.seller_id = :seller_id
            ORDER BY o.order_date DESC, o.order_id
        """, {'seller_id': user_id})
        
        orders = []
        for row in cursor.fetchall():
            order_date = row[3]
            if order_date:
                if isinstance(order_date, datetime.datetime):
                    order_date = order_date.strftime('%Y-%m-%d')
                else:
                    order_date = str(order_date)
            
            orders.append({
                'order_id': row[0],
                'customer_id': row[1],
                'customer_name': row[2],
                'order_date': order_date,
                'shipment_status': row[4],
                'payment_status': row[5] or 'N/A',
                'total_amount': float(row[6]) if row[6] else 0
            })
        
        # For each order, get this Seller's product items
        for order in orders:
            cursor.execute("""
                SELECT 
                    p.product_id,
                    p.name_product,
                    oi.quantity,
                    op.unit_price,
                    oi.quantity * op.unit_price as subtotal
                FROM ORDER_ITEM oi
                JOIN PRODUCT p ON oi.product_id = p.product_id
                JOIN ORDER_PRICE op ON oi.product_id = op.product_id
                WHERE oi.order_id = :order_id AND p.seller_id = :seller_id
            """, {'order_id': order['order_id'], 'seller_id': user_id})
            
            order['items'] = []
            seller_subtotal = 0
            for item_row in cursor.fetchall():
                item = {
                    'product_id': item_row[0],
                    'product_name': item_row[1],
                    'quantity': item_row[2],
                    'unit_price': float(item_row[3]),
                    'subtotal': float(item_row[4])
                }
                order['items'].append(item)
                seller_subtotal += item['subtotal']
            
            order['seller_subtotal'] = seller_subtotal
        
        # Serialize to JSON for frontend use
        orders_json = json.dumps(orders)
        
        cursor.close()
        connection.close()
        
        context = {
            'orders': orders,
            'orders_json': orders_json,
            'db_user': db_user,
            'user_type': user_type,
            'user_id': user_id,
            'store_name': store_name,
        }
    except Exception as e:
        context = {
            'orders': [],
            'error': str(e),
            'db_user': db_user,
            'user_type': user_type,
            'user_id': user_id,
        }
    
    return render(request, 'manage_orders.html', context)


def logout_view(request):
    """Logout view"""
    request.session.flush()
    return redirect('login')


def switch_role_view(request):
    """Switch role - Clear role information only, keep Oracle login status"""
    if not request.session.get('logged_in'):
        return redirect('login')
    
    # Only clear role-related session data, keep db_user and db_pass
    if 'user_type' in request.session:
        del request.session['user_type']
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'is_admin' in request.session:
        del request.session['is_admin']
    
    return redirect('select_role')


def browse_products_view(request):
    """Browse products - Customer feature"""
    if not request.session.get('logged_in'):
        return redirect('login')
    
    if not request.session.get('user_type'):
        return redirect('select_role')
    
    db_user = request.session.get('db_user')
    db_pass = request.session.get('db_pass')
    user_type = request.session.get('user_type')
    user_id = request.session.get('user_id')
    
    try:
        connection = get_db_connection(user=db_user, password=db_pass)
        cursor = connection.cursor()
        
        # Query all available products
        cursor.execute("""
            SELECT p.product_id, p.name_product, p.description_product, 
                   p.price, p.stock, 
                   u.first_name || ' ' || u.last_name as seller_name,
                   us.store_name,
                   c.name_category
            FROM PRODUCT p
            LEFT JOIN USERS_SELLER us ON p.seller_id = us.seller_id
            LEFT JOIN A3_USERS u ON p.seller_id = u.user_id
            LEFT JOIN CATEGORY c ON p.category_id = c.category_id
            WHERE p.stock > 0
            ORDER BY p.product_id
        """)
        
        products = []
        for row in cursor.fetchall():
            products.append({
                'product_id': row[0],
                'name': row[1],
                'description': row[2] or 'No description',
                'price': row[3],
                'stock': row[4],
                'seller_name': row[5] or 'Unknown',
                'store_name': row[6] or 'Unknown Store',
                'category': row[7] or 'Uncategorized'
            })
        
        cursor.close()
        connection.close()
        
        context = {
            'products': products,
            'user_type': user_type,
            'user_id': user_id,
            'db_user': db_user,
        }
        
    except Exception as e:
        context = {
            'products': [],
            'error': str(e),
            'user_type': user_type,
            'user_id': user_id,
            'db_user': db_user,
        }
    
    return render(request, 'browse_products.html', context)


def my_orders_view(request):
    """My orders - Customer feature"""
    if not request.session.get('logged_in'):
        return redirect('login')
    
    if not request.session.get('user_type'):
        return redirect('select_role')
    
    db_user = request.session.get('db_user')
    db_pass = request.session.get('db_pass')
    user_type = request.session.get('user_type')
    user_id = request.session.get('user_id')
    
    if user_type != 'CUSTOMER':
        return redirect('dashboard')
    
    try:
        connection = get_db_connection(user=db_user, password=db_pass)
        cursor = connection.cursor()
        
        # Query all orders for this customer
        cursor.execute("""
            SELECT o.order_id, o.order_date, o.shipment_status,
                   p.payment_status, p.total_amount
            FROM ORDERS o
            LEFT JOIN PAYMENT p ON o.order_id = p.order_id
            WHERE o.customer_id = :user_id
            ORDER BY o.order_date DESC
        """, {'user_id': user_id})
        
        orders = []
        for row in cursor.fetchall():
            order_id = row[0]
            
            # Query order details
            cursor.execute("""
                SELECT oi.product_id, pr.name_product, oi.quantity, 
                       op.unit_price, (oi.quantity * op.unit_price) as subtotal
                FROM ORDER_ITEM oi
                JOIN PRODUCT pr ON oi.product_id = pr.product_id
                LEFT JOIN ORDER_PRICE op ON oi.product_id = op.product_id
                WHERE oi.order_id = :order_id
            """, {'order_id': order_id})
            
            items = []
            for item_row in cursor.fetchall():
                items.append({
                    'product_id': item_row[0],
                    'product_name': item_row[1],
                    'quantity': item_row[2],
                    'unit_price': item_row[3],
                    'subtotal': item_row[4]
                })
            
            orders.append({
                'order_id': row[0],
                'order_date': row[1],
                'shipment_status': row[2],
                'payment_status': row[3] or 'Pending',
                'total_amount': row[4] or 0,
                'items': items
            })
        
        cursor.close()
        connection.close()
        
        context = {
            'orders': orders,
            'user_type': user_type,
            'user_id': user_id,
            'db_user': db_user,
        }
        
    except Exception as e:
        context = {
            'orders': [],
            'error': str(e),
            'user_type': user_type,
            'user_id': user_id,
            'db_user': db_user,
        }
    
    return render(request, 'my_orders.html', context)


def my_profile_view(request):
    """My profile - Customer feature"""
    if not request.session.get('logged_in'):
        return redirect('login')
    
    if not request.session.get('user_type'):
        return redirect('select_role')
    
    db_user = request.session.get('db_user')
    db_pass = request.session.get('db_pass')
    user_type = request.session.get('user_type')
    user_id = request.session.get('user_id')
    
    if user_type != 'CUSTOMER':
        return redirect('dashboard')
    
    try:
        connection = get_db_connection(user=db_user, password=db_pass)
        cursor = connection.cursor()
        
        # Query user basic information
        cursor.execute("""
            SELECT u.user_id, u.first_name, u.last_name, u.status, u.email, 
                   u.phone, u.street, u.city, u.province, u.postal_code,
                   uc.membership_id, uc.date_of_birth
            FROM A3_USERS u
            JOIN USERS_CUSTOMER uc ON u.user_id = uc.customer_id
            WHERE u.user_id = :user_id
        """, {'user_id': user_id})
        
        row = cursor.fetchone()
        if row:
            profile = {
                'user_id': row[0],
                'first_name': row[1],
                'last_name': row[2],
                'full_name': f"{row[1]} {row[2]}",
                'status': row[3],
                'email': row[4],
                'phone': row[5] or 'N/A',
                'street': row[6] or 'N/A',
                'city': row[7] or 'N/A',
                'province': row[8] or 'N/A',
                'postal_code': row[9] or 'N/A',
                'membership_id': row[10] or 'No Membership',
                'date_of_birth': row[11] or 'N/A'
            }
        else:
            profile = None
        
        cursor.close()
        connection.close()
        
        context = {
            'profile': profile,
            'user_type': user_type,
            'user_id': user_id,
            'db_user': db_user,
        }
        
    except Exception as e:
        context = {
            'profile': None,
            'error': str(e),
            'user_type': user_type,
            'user_id': user_id,
            'db_user': db_user,
        }
    
    return render(request, 'my_profile.html', context)


def edit_profile_view(request):
    """Edit profile - Customer feature"""
    if not request.session.get('logged_in'):
        return redirect('login')
    
    if not request.session.get('user_type'):
        return redirect('select_role')
    
    db_user = request.session.get('db_user')
    db_pass = request.session.get('db_pass')
    user_type = request.session.get('user_type')
    user_id = request.session.get('user_id')
    
    if user_type != 'CUSTOMER':
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            connection = get_db_connection(user=db_user, password=db_pass)
            cursor = connection.cursor()
            
            # Get data from form
            full_name = request.POST.get('full_name', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            street = request.POST.get('street', '').strip()
            city = request.POST.get('city', '').strip()
            province = request.POST.get('province', '').strip()
            postal_code = request.POST.get('postal_code', '').strip()
            date_of_birth = request.POST.get('date_of_birth', '').strip()
            
            # Split name
            name_parts = full_name.split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            # Handle empty values - convert empty strings to '-' to match default values
            phone = phone if phone else '-'
            street = street if street else '-'
            city = city if city else '-'
            province = province if province else '-'
            postal_code = postal_code if postal_code else '-'
            
            # Update A3_USERS table
            cursor.execute("""
                UPDATE A3_USERS 
                SET first_name = :first_name,
                    last_name = :last_name,
                    email = :email,
                    phone = :phone,
                    street = :street,
                    city = :city,
                    province = :province,
                    postal_code = :postal_code
                WHERE user_id = :user_id
            """, {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone': phone,
                'street': street,
                'city': city,
                'province': province,
                'postal_code': postal_code,
                'user_id': user_id
            })
            
            # Update USERS_CUSTOMER table (date)
            if date_of_birth:
                cursor.execute("""
                    UPDATE USERS_CUSTOMER 
                    SET date_of_birth = TO_DATE(:dob, 'YYYY-MM-DD')
                    WHERE customer_id = :user_id
                """, {
                    'dob': date_of_birth,
                    'user_id': user_id
                })
            
            connection.commit()
            cursor.close()
            connection.close()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('my_profile')
            
        except Exception as e:
            connection.rollback()
            cursor.close()
            connection.close()
            messages.error(request, f'Error updating profile: {str(e)}')
            return redirect('my_profile')
    
    return redirect('my_profile')


def add_product_view(request):
    """Add product"""
    if not request.session.get('logged_in'):
        return redirect('login')
    
    if request.method == 'POST':
        db_user = request.session.get('db_user')
        db_pass = request.session.get('db_pass')
        user_id = request.session.get('user_id')  # Current Seller's ID
        
        product_id = request.POST.get('product_id')
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        category_id = request.POST.get('category_id')
        
        try:
            connection = get_db_connection(user=db_user, password=db_pass)
            cursor = connection.cursor()
            
            # Insert product, using current Seller's user_id
            if category_id:
                cursor.execute("""
                    INSERT INTO PRODUCT (product_id, name_product, description_product, 
                                        price, stock, seller_id, category_id)
                    VALUES (:1, :2, :3, :4, :5, :6, :7)
                """, (product_id, name, description, float(price), int(stock), user_id, category_id))
            else:
                cursor.execute("""
                    INSERT INTO PRODUCT (product_id, name_product, description_product, 
                                        price, stock, seller_id)
                    VALUES (:1, :2, :3, :4, :5, :6)
                """, (product_id, name, description, float(price), int(stock), user_id))
            
            # Also insert into ORDER_PRICE table
            cursor.execute("""
                INSERT INTO ORDER_PRICE (product_id, unit_price)
                VALUES (:1, :2)
            """, (product_id, float(price)))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            messages.success(request, f'Product "{name}" added successfully!')
            
        except Exception as e:
            messages.error(request, f'Failed to add product: {str(e)}')
    
    return redirect('manage_products')


def edit_product_view(request, product_id):
    """Edit product"""
    if not request.session.get('logged_in'):
        return redirect('login')
    
    if request.method == 'POST':
        db_user = request.session.get('db_user')
        db_pass = request.session.get('db_pass')
        
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        category_id = request.POST.get('category_id')
        
        try:
            connection = get_db_connection(user=db_user, password=db_pass)
            cursor = connection.cursor()
            
            # Update product
            if category_id:
                cursor.execute("""
                    UPDATE PRODUCT 
                    SET name_product = :1, description_product = :2, 
                        price = :3, stock = :4, category_id = :5
                    WHERE product_id = :6
                """, (name, description, float(price), int(stock), category_id, product_id))
            else:
                cursor.execute("""
                    UPDATE PRODUCT 
                    SET name_product = :1, description_product = :2, 
                        price = :3, stock = :4, category_id = NULL
                    WHERE product_id = :6
                """, (name, description, float(price), int(stock), product_id))
            
            # Update ORDER_PRICE table
            cursor.execute("""
                UPDATE ORDER_PRICE 
                SET unit_price = :1
                WHERE product_id = :2
            """, (float(price), product_id))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            messages.success(request, f'Product "{name}" updated successfully!')
            
        except Exception as e:
            messages.error(request, f'Failed to update product: {str(e)}')
    
    return redirect('manage_products')


def delete_product_view(request, product_id):
    """Delete product"""
    if not request.session.get('logged_in'):
        return redirect('login')
    
    db_user = request.session.get('db_user')
    db_pass = request.session.get('db_pass')
    
    try:
        connection = get_db_connection(user=db_user, password=db_pass)
        cursor = connection.cursor()
        
        # Get product name for message
        cursor.execute("SELECT name_product FROM PRODUCT WHERE product_id = :1", (product_id,))
        result = cursor.fetchone()
        product_name = result[0] if result else product_id
        
        # Delete product (will cascade delete related records)
        cursor.execute("DELETE FROM PRODUCT WHERE product_id = :1", (product_id,))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        
    except Exception as e:
        messages.error(request, f'Failed to delete product: {str(e)}')
    
    return redirect('manage_products')

