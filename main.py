# ==========================
# File: main.py
# E-Commerce Database Management System - Oracle Database Operations Module
# ==========================
# This program implements a database management system for an online mall
# Supports both CLI and Web usage modes

import oracledb
from dotenv import load_dotenv
import os

load_dotenv()

# ===== Global Variables =====
# Database connection object: Stores connection with Oracle database
connection = None
# Database cursor object: Used to execute SQL statements
cursor = None

def init_connection(user, pw,
                    host="oracle12c.scs.ryerson.ca",
                    port=1521,
                    sid="orcl12c"):
    """
    Initialize global database connection and cursor
    
    Parameters:
        user (str): Oracle database username
        pw (str): Oracle database password
        host (str): Database host address, default: oracle12c.scs.ryerson.ca
        port (int): Database port, default: 1521
        sid (str): Database SID, default: orcl12c
    
    Functionality: Establish connection with Oracle database and create cursor object
    Usage scenarios:
        - CLI mode: Call after getting user credentials from terminal
        - Web mode: Flask web_app.py calls this function to initialize connection
    """
    global connection, cursor

    # Establish connection with Oracle database using oracledb library
    connection = oracledb.connect(
        user=user,
        password=pw,
        host=host,
        port=port,
        sid=sid,
    )
    # Create cursor object for executing SQL statements
    cursor = connection.cursor()
    print("Successfully connected to Oracle Database:", connection.db_name)


def dropTables():
    """
    Drop all tables from the database
    
    Functionality description:
        1. Define list of all table names to delete (in reverse order of foreign key dependencies)
        2. Execute DROP TABLE statements one by one
        3. Use CASCADE CONSTRAINTS option to automatically delete related constraints
        4. If table doesn't exist, catch exception and continue without interrupting
        5. Commit transaction at the end
    
    Usage scenarios:
        - Re-initialize database
        - Clear all data and table structures
        - Prepare for creating new table structures
    
    Note: This operation is irreversible and deletes all data!
    """
    # Define all table names to delete (deletion order is important, start from tables with foreign keys)
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
        "DROP TABLE ORDER_PRICE CASCADE CONSTRAINTS",
    ]

    # Execute delete statements one by one
    for stmt in drop_stmts:
        try:
            cursor.execute(stmt)
        except Exception as e:
            # If table doesn't exist, catch exception and continue (don't interrupt program)
            print(e)

    # Commit transaction to ensure deletion takes effect
    connection.commit()
    print("Specified tables dropped.")


def createTables() -> any:
    """
    Create all table structures in the database
    
    Functionality description:
        1. Create 11 tables to organize online mall data
        2. Define primary keys, foreign keys, constraints and default values
        3. Use try-except to catch errors
        4. Commit transaction if successful, rollback if failed
    
    Table structure design:
        - A3_USERS: Main user table (stores all user information)
        - UserName: User name table (redundant data)
        - USERS_ADMIN: Administrator role table
        - USERS_SELLER: Seller role table
        - USERS_CUSTOMER: Buyer role table
        - CATEGORY: Product category table
        - PRODUCT: Product information table
        - ORDERS: Order table
        - PAYMENT: Payment information table
        - ORDER_ITEM: Order item table (specific products in orders)
        - ORDER_PRICE: Order price history table
    
    Design highlights:
        - Uses three role types (ADMIN/SELLER/CUSTOMER)
        - Order and payment status have check constraints
        - Prices and inventory have non-negative checks
        - Uses cascade delete to ensure data consistency
    """
    try:
        # ===== 1. Create A3_USERS table =====
        # This is the main user table in the system, containing all user information
        cursor.execute(
            '''
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
        '''
        )

        # ===== 2. Create UserName table =====
        # Stores user names and their combined full names, primary key is combination of (first_name, last_name)
        cursor.execute(
            '''
            CREATE TABLE UserName (
              first_name VARCHAR2(50) NOT NULL,
              last_name VARCHAR2(50) NOT NULL,
              fullname VARCHAR2(255) NOT NULL,
              CONSTRAINT pk_username PRIMARY KEY (first_name, last_name)
            )
        '''
        )

        # ===== 3. Create USERS_ADMIN table =====
        # Store administrator information, has a one-to-one relationship with A3_USERS table
        cursor.execute(
            '''
            CREATE TABLE USERS_ADMIN (
                admin_id VARCHAR2(20)
                    CONSTRAINT pk_users_admin PRIMARY KEY
                    CONSTRAINT fk_users_admin_user
                        REFERENCES A3_USERS (user_id) ON DELETE CASCADE,
                role_admin VARCHAR2(50)
                    CONSTRAINT nn_usersAdmin_role NOT NULL
            )
        '''
        )

        cursor.execute(
            '''
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
        '''
        )

        cursor.execute(
            '''
            CREATE TABLE USERS_CUSTOMER (
                customer_id VARCHAR2(20)
                    CONSTRAINT pk_users_customer PRIMARY KEY
                    CONSTRAINT fk_users_customer_user
                        REFERENCES A3_USERS (user_id) ON DELETE CASCADE,
                membership_id VARCHAR2(50) DEFAULT '-' ,
                date_of_birth DATE
            )
        '''
        )

        cursor.execute(
            '''
            CREATE TABLE CATEGORY (
                category_id   VARCHAR2(20)
                    CONSTRAINT pk_category PRIMARY KEY,
                name_category          VARCHAR2(100) NOT NULL,
                description_category   VARCHAR2(255)
            )
        '''
        )

        cursor.execute(
            '''
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
        '''
        )

        cursor.execute(
            '''
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
        '''
        )

        cursor.execute(
            '''
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
        '''
        )

        cursor.execute(
            '''
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
        '''
        )

        cursor.execute(
            '''
            CREATE TABLE ORDER_PRICE (
              product_id VARCHAR2(20) PRIMARY KEY,
              unit_price NUMBER(10,2) NOT NULL,
              CONSTRAINT fk_order_price_product
                FOREIGN KEY (product_id)
                REFERENCES PRODUCT(product_id)
                ON DELETE CASCADE
            )
        '''
        )

        connection.commit()
        print("All tables created successfully!")
    except Exception as e:
        print(e)
        connection.rollback()
        print("Creation unsuccessful, try again!")


def createSingleTable(table_name: str) -> bool:
    """
    Create a single table by name
    
    Parameters:
        table_name (str): Name of the table to create
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    # Define SQL statements for each table
    table_definitions = {
        'A3_USERS': '''
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
        ''',
        'UserName': '''
            CREATE TABLE UserName (
              first_name VARCHAR2(50) NOT NULL,
              last_name VARCHAR2(50) NOT NULL,
              fullname VARCHAR2(255) NOT NULL,
              CONSTRAINT pk_username PRIMARY KEY (first_name, last_name)
            )
        ''',
        'USERS_ADMIN': '''
            CREATE TABLE USERS_ADMIN (
                admin_id VARCHAR2(20)
                    CONSTRAINT pk_users_admin PRIMARY KEY
                    CONSTRAINT fk_users_admin_user
                        REFERENCES A3_USERS (user_id) ON DELETE CASCADE,
                role_admin VARCHAR2(50)
                    CONSTRAINT nn_usersAdmin_role NOT NULL
            )
        ''',
        'USERS_SELLER': '''
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
        ''',
        'USERS_CUSTOMER': '''
            CREATE TABLE USERS_CUSTOMER (
                customer_id VARCHAR2(20)
                    CONSTRAINT pk_users_customer PRIMARY KEY
                    CONSTRAINT fk_users_customer_user
                        REFERENCES A3_USERS (user_id) ON DELETE CASCADE,
                membership_id VARCHAR2(50) DEFAULT '-' ,
                date_of_birth DATE
            )
        ''',
        'CATEGORY': '''
            CREATE TABLE CATEGORY (
                category_id   VARCHAR2(20)
                    CONSTRAINT pk_category PRIMARY KEY,
                name_category          VARCHAR2(100) NOT NULL,
                description_category   VARCHAR2(255)
            )
        ''',
        'PRODUCT': '''
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
        ''',
        'ORDERS': '''
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
        ''',
        'PAYMENT': '''
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
        ''',
        'ORDER_ITEM': '''
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
        ''',
        'ORDER_PRICE': '''
            CREATE TABLE ORDER_PRICE (
              product_id VARCHAR2(20) PRIMARY KEY,
              unit_price NUMBER(10,2) NOT NULL,
              CONSTRAINT fk_order_price_product
                FOREIGN KEY (product_id)
                REFERENCES PRODUCT(product_id)
                ON DELETE CASCADE
            )
        '''
    }
    
    if table_name not in table_definitions:
        print(f"Error: Unknown table name: {table_name}")
        return False
    
    try:
        cursor.execute(table_definitions[table_name])
        connection.commit()
        print(f"Table {table_name} created successfully!")
        return True
    except Exception as e:
        print(f"Error creating table {table_name}: {e}")
        connection.rollback()
        return False


def populateSingleTable(table_name: str) -> bool:
    """
    Populate sample data for a single table
    
    Parameters:
        table_name (str): Name of the table to populate
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    try:
        if table_name == 'A3_USERS':
            # Insert all user data
            cursor.execute("""
                INSERT INTO A3_USERS (user_id, first_name, last_name, status, email, phone, street, city, province, postal_code, user_type)
                VALUES ('U1', 'John', 'Smith', 'Active', 'john.smith@example.com', '123-4567', '14 King St', 'Toronto', 'ON', 'M1A1A1', 'ADMIN')
            """)
            cursor.execute("""
                INSERT INTO A3_USERS (user_id, first_name, last_name, status, email, phone, street, city, province, postal_code, user_type)
                VALUES ('U2', 'Alice', 'Brown', 'Active', 'alice.brown@example.com', '234-5678', '22 Queen St', 'Toronto', 'ON', 'M2B2B2', 'SELLER')
            """)
            cursor.execute("""
                INSERT INTO A3_USERS (user_id, first_name, last_name, status, email, phone, street, city, province, postal_code, user_type)
                VALUES ('U3', 'Bob', 'Green', 'Active', 'bob.green@example.com', '345-6789', '33 King Ave', 'Ottawa', 'ON', 'K1C1C1', 'CUSTOMER')
            """)
            cursor.execute("""
                INSERT INTO A3_USERS (user_id, first_name, last_name, status, email, phone, street, city, province, postal_code, user_type)
                VALUES ('CUS1', 'Decor', 'Delights', 'Active', 'decor@gmail.com', '416-928-3812',
                        '327 George Street', 'Toronto', 'ON', 'M5A 2N2', 'CUSTOMER')
            """)
            cursor.execute("""
                INSERT INTO A3_USERS (user_id, first_name, last_name, status, email, user_type)
                VALUES ('CUS2', 'Bob', 'Li', 'Inactive', 'bob@gmail.com', 'CUSTOMER')
            """)
            cursor.execute("""
                INSERT INTO A3_USERS (user_id, first_name, last_name, status, email, phone, street, city, province, postal_code, user_type)
                VALUES ('CUS3', 'Hailey', 'Rockwood', 'Active', 'itshailey1999@gmail.com', '437-225-8927',
                        '256 Spadina Avenue', 'Toronto', 'ON', 'M5T 2C2', 'CUSTOMER')
            """)
            cursor.execute("""
                INSERT INTO A3_USERS (user_id, first_name, last_name, status, email, phone, street, city, province, postal_code, user_type)
                VALUES ('CUS4', 'Damon', 'Mist', 'Active', 'damist@gmail.com', '905-043-2080',
                        '94 Liberty Street', 'Toronto', 'ON', 'M8T 5C2', 'CUSTOMER')
            """)
            cursor.execute("""
                INSERT INTO A3_USERS (user_id, first_name, last_name, status, email, phone, street, city, province, postal_code, user_type)
                VALUES ('S1', 'Emily', 'Stone', 'Active', 'emily.stone@yahoo.com', '647-555-2389',
                        '120 Queen Street West', 'Toronto', 'ON', 'M5H 2N2', 'SELLER')
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
            
        elif table_name == 'UserName':
            cursor.execute("INSERT INTO UserName (first_name, last_name, fullname) VALUES ('John', 'Smith', 'John Smith')")
            cursor.execute("INSERT INTO UserName (first_name, last_name, fullname) VALUES ('Alice', 'Brown', 'Alice Brown')")
            cursor.execute("INSERT INTO UserName (first_name, last_name, fullname) VALUES ('Bob', 'Green', 'Bob Green')")
            
        elif table_name == 'USERS_ADMIN':
            cursor.execute("INSERT INTO USERS_ADMIN (admin_id, role_admin) VALUES ('U1', 'SuperAdmin')")
            cursor.execute("INSERT INTO USERS_ADMIN (admin_id, role_admin) VALUES ('A1', 'SECURITY_ADMIN')")
            cursor.execute("INSERT INTO USERS_ADMIN (admin_id, role_admin) VALUES ('A2', 'SECURITY_ADMIN')")
            cursor.execute("INSERT INTO USERS_ADMIN (admin_id, role_admin) VALUES ('A3', 'System_ADMIN')")
            
        elif table_name == 'USERS_SELLER':
            cursor.execute("INSERT INTO USERS_SELLER (seller_id, store_name, admin_id) VALUES ('U2', 'Alice Store', 'U1')")
            cursor.execute("INSERT INTO USERS_SELLER (seller_id, store_name, admin_id) VALUES ('S1', 'Toy Shop', 'A1')")
            cursor.execute("INSERT INTO USERS_SELLER (seller_id, store_name, admin_id) VALUES ('S2', 'Women Shop', 'A1')")
            cursor.execute("INSERT INTO USERS_SELLER (seller_id, store_name, admin_id) VALUES ('S4', 'Women Store', 'A3')")
            
        elif table_name == 'USERS_CUSTOMER':
            cursor.execute("""
                INSERT INTO USERS_CUSTOMER (customer_id, membership_id, date_of_birth)
                VALUES ('U3', 'M123', TO_DATE('1990-01-01','YYYY-MM-DD'))
            """)
            cursor.execute("INSERT INTO USERS_CUSTOMER (customer_id, membership_id, date_of_birth) VALUES ('CUS1', NULL, NULL)")
            cursor.execute("INSERT INTO USERS_CUSTOMER (customer_id, membership_id, date_of_birth) VALUES ('CUS2', '123456', DATE '2001-01-12')")
            cursor.execute("INSERT INTO USERS_CUSTOMER (customer_id, membership_id, date_of_birth) VALUES ('CUS3', '654321', NULL)")
            cursor.execute("INSERT INTO USERS_CUSTOMER (customer_id, membership_id, date_of_birth) VALUES ('CUS4', NULL, DATE '1994-08-16')")
            cursor.execute("INSERT INTO USERS_CUSTOMER (customer_id, membership_id, date_of_birth) VALUES ('S1', 'MEM999', DATE '1990-01-01')")
            
        elif table_name == 'CATEGORY':
            cursor.execute("""
                INSERT INTO CATEGORY (category_id, name_category, description_category)
                VALUES ('C1', 'Antiques', 'Antique and collectible items')
            """)
            cursor.execute("""
                INSERT INTO CATEGORY (category_id, name_category, description_category)
                VALUES ('C2', 'Electronics', 'Electronic devices and accessories')
            """)
            cursor.execute("""
                INSERT INTO CATEGORY (category_id, name_category, description_category)
                VALUES ('C1001', 'Sports toy', 'Toys for children to engage in sports activities')
            """)
            cursor.execute("""
                INSERT INTO CATEGORY (category_id, name_category, description_category)
                VALUES ('C1002', 'Women clothes', 'Tops, bottoms, coats and dresses')
            """)
            
        elif table_name == 'PRODUCT':
            cursor.execute("""
                INSERT INTO PRODUCT (product_id, name_product, description_product, price, stock, seller_id, category_id)
                VALUES ('P1', 'Antique Vase', 'A beautiful antique vase from the 19th century.', 150.00, 10, 'U2', 'C1')
            """)
            cursor.execute("""
                INSERT INTO PRODUCT (product_id, name_product, description_product, price, stock, seller_id, category_id)
                VALUES ('P2', 'Vintage Camera', 'A rare vintage camera in excellent condition.', 250.00, 5, 'U2', 'C2')
            """)
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
            cursor.execute("""
                INSERT INTO PRODUCT (product_id, name_product, description_product, price, stock, seller_id, category_id)
                VALUES ('P0006', 'Basketball', 'Alternate Basketball Item', 18.99, 50, 'S1', 'C1001')
            """)
            
        elif table_name == 'ORDER_PRICE':
            cursor.execute("INSERT INTO ORDER_PRICE (product_id, unit_price) VALUES ('P1', 150.00)")
            cursor.execute("INSERT INTO ORDER_PRICE (product_id, unit_price) VALUES ('P2', 250.00)")
            cursor.execute("INSERT INTO ORDER_PRICE (product_id, unit_price) VALUES ('P0001', 15.99)")
            cursor.execute("INSERT INTO ORDER_PRICE (product_id, unit_price) VALUES ('P0002', 36.99)")
            cursor.execute("INSERT INTO ORDER_PRICE (product_id, unit_price) VALUES ('P0003', 25.99)")
            cursor.execute("INSERT INTO ORDER_PRICE (product_id, unit_price) VALUES ('P0004', 120.00)")
            cursor.execute("INSERT INTO ORDER_PRICE (product_id, unit_price) VALUES ('P0005', 45.50)")
            cursor.execute("INSERT INTO ORDER_PRICE (product_id, unit_price) VALUES ('P0006', 18.99)")
            
        elif table_name == 'ORDERS':
            cursor.execute("""
                INSERT INTO ORDERS (order_id, customer_id, order_date, shipment_status)
                VALUES ('O1', 'U3', TO_DATE('2024-10-10','YYYY-MM-DD'), 'Pending')
            """)
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
            cursor.execute("""
                INSERT INTO ORDERS (order_id, customer_id, order_date, shipment_status)
                VALUES ('O007', 'CUS1', DATE '2025-10-01', 'Delivered')
            """)
            cursor.execute("""
                INSERT INTO ORDERS (order_id, customer_id, order_date, shipment_status)
                VALUES ('OBUY1', 'S1', DATE '2025-11-01', 'Pending')
            """)
            
        elif table_name == 'PAYMENT':
            cursor.execute("INSERT INTO PAYMENT (payment_id, order_id, payment_status, total_amount) VALUES ('PAY1', 'O1', 'Paid', 150.00)")
            cursor.execute("INSERT INTO PAYMENT (payment_id, order_id, payment_status, total_amount) VALUES ('EFT0001', 'O001', 'Paid', 31.98)")
            cursor.execute("INSERT INTO PAYMENT (payment_id, order_id, payment_status, total_amount) VALUES ('EFT0002', 'O002', 'Pending', 110.97)")
            cursor.execute("INSERT INTO PAYMENT (payment_id, order_id, payment_status, total_amount) VALUES ('EFT0003', 'O003', 'Paid', 25.99)")
            cursor.execute("INSERT INTO PAYMENT (payment_id, order_id, payment_status, total_amount) VALUES ('EFT0004', 'O004', 'Paid', 240.00)")
            cursor.execute("INSERT INTO PAYMENT (payment_id, order_id, payment_status, total_amount) VALUES ('EFT0005', 'O005', 'Pending', 182.00)")
            cursor.execute("INSERT INTO PAYMENT (payment_id, order_id, payment_status, total_amount) VALUES ('EFT0006', 'O006', 'Paid', 79.95)")
            cursor.execute("INSERT INTO PAYMENT (payment_id, order_id, payment_status, total_amount) VALUES ('PAYBUY1', 'OBUY1', 'Paid', 20.00)")
            
        elif table_name == 'ORDER_ITEM':
            cursor.execute("INSERT INTO ORDER_ITEM (order_id, product_id, quantity) VALUES ('O1', 'P1', 1)")
            cursor.execute("INSERT INTO ORDER_ITEM (order_id, product_id, quantity) VALUES ('O001', 'P0001', 2)")
            cursor.execute("INSERT INTO ORDER_ITEM (order_id, product_id, quantity) VALUES ('O002', 'P0002', 3)")
            cursor.execute("INSERT INTO ORDER_ITEM (order_id, product_id, quantity) VALUES ('O003', 'P0003', 1)")
            cursor.execute("INSERT INTO ORDER_ITEM (order_id, product_id, quantity) VALUES ('O004', 'P0004', 2)")
            cursor.execute("INSERT INTO ORDER_ITEM (order_id, product_id, quantity) VALUES ('O005', 'P0005', 4)")
            cursor.execute("INSERT INTO ORDER_ITEM (order_id, product_id, quantity) VALUES ('O006', 'P0001', 5)")
            cursor.execute("INSERT INTO ORDER_ITEM (order_id, product_id, quantity) VALUES ('OBUY1', 'P0001', 1)")
            
        else:
            print(f"Unknown table: {table_name}")
            return False
        
        connection.commit()
        print(f"Table {table_name} populated successfully with all sample data!")
        return True
        
    except Exception as e:
        print(f"Error populating table {table_name}: {e}")
        connection.rollback()
        return False


def populateTables() -> any:
    """
    Insert sample data into all created tables
    
    Functionality description:
        1. Insert multiple real user, product, order and payment data
        2. Data used for testing and demonstrating system functionality
        3. Includes different user roles (ADMIN, SELLER, CUSTOMER)
        4. Includes complete order flow (users -> products -> orders -> payments)
    
    Data design description:
        - 3 initial test users (ADMIN, SELLER, CUSTOMER)
        - 3 main users and 6 additional users (9 total)
        - 3 administrators
        - 3 sellers
        - 4 buyers
        - 2 product categories
        - 5 product items
        - 7 orders
        - 6 payment records
        - 7 order items
    
    Usage scenarios:
        - Fill test data when first setting up system
        - Perform functionality demonstrations and testing
        - Learn and understand database structure
    """
    try:
        # ===== Step 1: Insert initial user data =====
        # These three users are system's initial test users, representing three roles
        cursor.execute("""
            INSERT INTO A3_USERS (user_id, first_name, last_name, status, email, phone, street, city, province, postal_code, user_type)
            VALUES ('U1', 'John', 'Smith', 'Active', 'john.smith@example.com', '123-4567', '14 King St', 'Toronto', 'ON', 'M1A1A1', 'ADMIN')
        """)
        cursor.execute("""
            INSERT INTO A3_USERS (user_id, first_name, last_name, status, email, phone, street, city, province, postal_code, user_type)
            VALUES ('U2', 'Alice', 'Brown', 'Active', 'alice.brown@example.com', '234-5678', '22 Queen St', 'Toronto', 'ON', 'M2B2B2', 'SELLER')
        """)
        cursor.execute("""
            INSERT INTO A3_USERS (user_id, first_name, last_name, status, email, phone, street, city, province, postal_code, user_type)
            VALUES ('U3', 'Bob', 'Green', 'Active', 'bob.green@example.com', '345-6789', '33 King Ave', 'Ottawa', 'ON', 'K1C1C1', 'CUSTOMER')
        """)

        cursor.execute("INSERT INTO UserName (first_name, last_name, fullname) VALUES ('John', 'Smith', 'John Smith')")
        cursor.execute("INSERT INTO UserName (first_name, last_name, fullname) VALUES ('Alice', 'Brown', 'Alice Brown')")
        cursor.execute("INSERT INTO UserName (first_name, last_name, fullname) VALUES ('Bob', 'Green', 'Bob Green')")

        cursor.execute("INSERT INTO USERS_ADMIN (admin_id, role_admin) VALUES ('U1', 'SuperAdmin')")
        cursor.execute("INSERT INTO USERS_SELLER (seller_id, store_name, admin_id) VALUES ('U2', 'Alice Store', 'U1')")
        cursor.execute("""
            INSERT INTO USERS_CUSTOMER (customer_id, membership_id, date_of_birth)
            VALUES ('U3', 'M123', TO_DATE('1990-01-01','YYYY-MM-DD'))
        """)

        cursor.execute("""
            INSERT INTO CATEGORY (category_id, name_category, description_category)
            VALUES ('C1', 'Antiques', 'Antique and collectible items')
        """)
        cursor.execute("""
            INSERT INTO CATEGORY (category_id, name_category, description_category)
            VALUES ('C2', 'Electronics', 'Electronic devices and accessories')
        """)

        cursor.execute("""
            INSERT INTO PRODUCT (product_id, name_product, description_product, price, stock, seller_id, category_id)
            VALUES ('P1', 'Antique Vase', 'A beautiful antique vase from the 19th century.', 150.00, 10, 'U2', 'C1')
        """)
        cursor.execute("""
            INSERT INTO PRODUCT (product_id, name_product, description_product, price, stock, seller_id, category_id)
            VALUES ('P2', 'Vintage Camera', 'A rare vintage camera in excellent condition.', 250.00, 5, 'U2', 'C2')
        """)

        cursor.execute("""
            INSERT INTO ORDERS (order_id, customer_id, order_date, shipment_status)
            VALUES ('O1', 'U3', TO_DATE('2024-10-10','YYYY-MM-DD'), 'Pending')
        """)

        cursor.execute("""
            INSERT INTO PAYMENT (payment_id, order_id, payment_status, total_amount)
            VALUES ('PAY1', 'O1', 'Paid', 150.00)
        """)

        cursor.execute("""
            INSERT INTO ORDER_ITEM (order_id, product_id, quantity)
            VALUES ('O1', 'P1', 1)
        """)

        cursor.execute("INSERT INTO ORDER_PRICE (product_id, unit_price) VALUES ('P1', 150.00)")
        cursor.execute("INSERT INTO ORDER_PRICE (product_id, unit_price) VALUES ('P2', 250.00)")


        # A3_USERS
        cursor.execute("""
            INSERT INTO A3_USERS (user_id, first_name, last_name, status, email, phone, street, city, province, postal_code, user_type)
            VALUES ('CUS1', 'Decor', 'Delights', 'Active', 'decor@gmail.com', '416-928-3812',
                    '327 George Street', 'Toronto', 'ON', 'M5A 2N2', 'CUSTOMER')
        """)

        cursor.execute("""
            INSERT INTO A3_USERS (user_id, first_name, last_name, status, email, user_type)
            VALUES ('CUS2', 'Bob', 'Li', 'Inactive', 'bob@gmail.com', 'CUSTOMER')
        """)

        cursor.execute("""
            INSERT INTO A3_USERS (user_id, first_name, last_name, status, email, phone, street, city, province, postal_code, user_type)
            VALUES ('CUS3', 'Hailey', 'Rockwood', 'Active', 'itshailey1999@gmail.com', '437-225-8927',
                    '256 Spadina Avenue', 'Toronto', 'ON', 'M5T 2C2', 'CUSTOMER')
        """)

        cursor.execute("""
            INSERT INTO A3_USERS (user_id, first_name, last_name, status, email, phone, street, city, province, postal_code, user_type)
            VALUES ('CUS4', 'Damon', 'Mist', 'Active', 'damist@gmail.com', '905-043-2080',
                    '94 Liberty Street', 'Toronto', 'ON', 'M8T 5C2', 'CUSTOMER')
        """)

        cursor.execute("""
            INSERT INTO A3_USERS (user_id, first_name, last_name, status, email, phone, street, city, province, postal_code, user_type)
            VALUES ('S1', 'Emily', 'Stone', 'Active', 'emily.stone@yahoo.com', '647-555-2389',
                    '120 Queen Street West', 'Toronto', 'ON', 'M5H 2N2', 'SELLER')
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
        cursor.execute("""
            INSERT INTO ORDERS (order_id, customer_id, order_date, shipment_status)
            VALUES ('O007', 'CUS1', DATE '2025-10-01', 'Delivered')
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
        
        # S1 is also customer (query4)
        cursor.execute("INSERT INTO USERS_CUSTOMER (customer_id, membership_id, date_of_birth) "
               "VALUES ('S1', 'MEM999', DATE '1990-01-01')")

        cursor.execute("INSERT INTO ORDERS (order_id, customer_id, order_date, shipment_status) "
                    "VALUES ('OBUY1', 'S1', DATE '2025-11-01', 'Pending')")

        cursor.execute("INSERT INTO PAYMENT (payment_id, order_id, payment_status, total_amount) "
                    "VALUES ('PAYBUY1', 'OBUY1', 'Paid', 20.00)")

        cursor.execute("INSERT INTO ORDER_ITEM (order_id, product_id, quantity) "
                    "VALUES ('OBUY1', 'P0001', 1)")
        
        # duplicate name product (query 2)
        cursor.execute("INSERT INTO PRODUCT (product_id, name_product, description_product, price, stock, seller_id, category_id) "
                    "VALUES ('P0006', 'Basketball', 'Alternate Basketball Item', 18.99, 50, 'S1', 'C1001')")

        cursor.execute("INSERT INTO ORDER_PRICE (product_id, unit_price) "
                    "VALUES ('P0006', 18.99)")

        connection.commit()
        print("All tables populated successfully!")
    except Exception as e:
        print(e)
        print("Populating tables unsuccessful")


def executeQuery(command: str) -> any:
    """
    Execute SELECT query and display results in formatted table
    
    Parameter description:
        command (str): SQL SELECT statement to execute
    
    Functionality description:
        1. Execute the SELECT statement passed in
        2. Get all rows and column names from query results
        3. Calculate maximum width for each column (for table alignment)
        4. Generate formatted table output
        5. Include header row separator and data row separator
        6. Handle NULL values with special display
    
    Return value:
        str: Formatted table string, or None if query fails
    
    Error handling:
        - If SQL statement has errors, catch exception and print error message
    
    Example output:
        +-------+-------+
        | name  | price |
        +-------+-------+
        | apple | 5.99  |
        | banana| 3.50  |
        +-------+-------+
    """
    try:
        cursor.execute(command)
    except Exception as e:
        print(e)
        return None

    # Fetch all rows from query results
    rows = cursor.fetchall()
    # Get list of column names
    column_names = [desc[0] for desc in cursor.description] if cursor.description else []

    # ===== Calculate maximum width for each column =====
    # This ensures table alignment
    col_widths = []
    for i, col_name in enumerate(column_names):
        # Initialize maximum width as length of column name
        max_width = len(str(col_name))
        # Check all data rows to find maximum width for this column
        for row in rows:
            cell = row[i]
            cell_len = len("NULL") if cell is None else len(str(cell))
            if cell_len > max_width:
                max_width = cell_len
        col_widths.append(max_width)

    # ===== Generate table =====
    out_lines = []
    # Generate horizontal line (top)
    horizontal_line = "+"
    for width in col_widths:
        horizontal_line += "-" * (width + 2) + "+"
    out_lines.append(horizontal_line)

    # Generate header
    if column_names:
        header = "| "
        for col_name, width in zip(column_names, col_widths):
            header += f"{col_name:<{width}} | "
        out_lines.append(header)
        out_lines.append(horizontal_line)

    # Generate data rows
    for row in rows:
        row_data = "| "
        for cell, width in zip(row, col_widths):
            cell_text = "NULL" if cell is None else str(cell)
            row_data += f"{cell_text:<{width}} | "
        out_lines.append(row_data)

    # Generate bottom separator
    out_lines.append(horizontal_line)
    # Merge all rows into a single string
    output = "\n".join(out_lines)
    print(output)
    
    return output

def executeInsert(command: str) -> None:
    """
    Execute INSERT statement to insert data
    
    Parameter description：
        command (str): SQL INSERT statement to execute
    
    Functionality description：
        1. Execute INSERT statement
        2. Commit transaction to ensure data is saved
        3. Print "Insert successful!" message on success
        4. Print error message and display "Insert unsuccessful, try again!" on failure
    
    Error handling：
        - Catch exceptions and print error details
        - Will not rollback (because it's a single INSERT)
    """
    try: 
        cursor.execute(command)
        connection.commit()
        print("Insert successful!")
    except Exception as e:
        print(e)
        print("Insert unsuccessful, try again!")

def listTables():
    """
    Query and display all tables in the current database
    
    Functionality description:
        1. Query all tables from Oracle system table user_tables
        2. List all table names with numbers
    
    Usage scenarios:
        - View which tables exist in current database
        - Part of main menu to display database status
    """
    # Query all tables owned by current user
    cursor.execute("""
        SELECT table_name
        FROM user_tables
    """)
    
    # Fetch query results
    tables = cursor.fetchall()
    count = 1
    print("Tables in the schema:")
    # Display each table name one by one
    for table in tables:
        print(str(count) + ". " + table[0])
        count += 1
        
def insertData() -> None:
    """
    Interactive menu for manually inserting data
    
    Functionality description：
        1. Display a menu for users to select which table to insert data into
        2. Show appropriate input fields based on selection
        3. Collect user input and generate INSERT statement
        4. Execute insert operation
    
    Supported tables：
        1. A3_USERS - User table
        2. UserName - User name table
        3. USERS_ADMIN - Administrator table
        4. USERS_SELLER - Seller table
        5. USERS_CUSTOMER - Buyer table
        6. CATEGORY - Product category table
        7. PRODUCT - Product table
        8. ORDERS - Order table
        9. PAYMENT - Payment table
        10. ORDER_ITEM - Order item table
        11. ORDER_PRICE - Order price table
        12. Custom Query - Manually input SQL statement
        13. Back to Main Menu
        14. Exit - Exit program
    
    Features：
        - For optional fields, users can leave blank to use default values
        - For date fields, prompt users to enter YYYY-MM-DD format
        - Display generated SQL statement for user confirmation
    """
    while True:
        print("\n-- Insert Menu --")
        print("1. A3_USERS")
        print("2. UserName")
        print("3. USERS_ADMIN")
        print("4. USERS_SELLER")
        print("5. USERS_CUSTOMER")
        print("6. CATEGORY")
        print("7. PRODUCT")
        print("8. ORDERS")
        print("9. PAYMENT")
        print("10. ORDER_ITEM")
        print("11. ORDER_PRICE")
        print("12. Custom Query")
        print("13. Back to Main Menu")
        print("14. Exit")

        user_input = input("Enter: ").strip()

        if user_input == "1":
            user_id = input("user_id: ").strip()
            first_name = input("first_name: ").strip()
            last_name = input("last_name: ").strip()
            status = input("status (Active/Inactive): ").strip()
            email = input("email: ").strip()
            phone = input("phone (or leave blank): ").strip() or "-"
            street = input("street (or leave blank): ").strip() or "-"
            city = input("city (or leave blank): ").strip() or "-"
            province = input("province (or leave blank): ").strip() or "-"
            postal_code = input("postal_code (or leave blank): ").strip() or "-"
            user_type = input("user_type (ADMIN/SELLER/CUSTOMER): ").strip()
            command = ("INSERT INTO A3_USERS (user_id, first_name, last_name, status, email, phone, street, city, province, postal_code, user_type) "
                       f"VALUES ('{user_id}', '{first_name}', '{last_name}', '{status}', '{email}', '{phone}', '{street}', '{city}', '{province}', '{postal_code}', '{user_type}')")
            print(command)
            executeInsert(command)

        elif user_input == "2":
            first_name = input("first_name: ").strip()
            last_name = input("last_name: ").strip()
            fullname = input("fullname: ").strip()
            command = f"INSERT INTO UserName (first_name, last_name, fullname) VALUES ('{first_name}', '{last_name}', '{fullname}')"
            print(command)
            executeInsert(command)

        elif user_input == "3":
            admin_id = input("admin_id: ").strip()
            role_admin = input("role_admin: ").strip()
            command = f"INSERT INTO USERS_ADMIN (admin_id, role_admin) VALUES ('{admin_id}', '{role_admin}')"
            print(command)
            executeInsert(command)

        elif user_input == "4":
            seller_id = input("seller_id: ").strip()
            store_name = input("store_name: ").strip()
            admin_id = input("admin_id (leave blank for NULL): ").strip()
            admin_sql = "NULL" if admin_id == "" else f"'{admin_id}'"
            command = f"INSERT INTO USERS_SELLER (seller_id, store_name, admin_id) VALUES ('{seller_id}', '{store_name}', {admin_sql})"
            print(command)
            executeInsert(command)

        elif user_input == "5":
            customer_id = input("customer_id: ").strip()
            membership_id = input("membership_id (or leave blank for '-'): ").strip() or "-"
            dob = input("date_of_birth (YYYY-MM-DD) (leave blank for NULL): ").strip()
            if dob:
                command = f"INSERT INTO USERS_CUSTOMER (customer_id, membership_id, date_of_birth) VALUES ('{customer_id}', '{membership_id}', TO_DATE('{dob}','YYYY-MM-DD'))"
            else:
                command = f"INSERT INTO USERS_CUSTOMER (customer_id, membership_id) VALUES ('{customer_id}', '{membership_id}')"
            print(command)
            executeInsert(command)

        elif user_input == "6":
            category_id = input("category_id: ").strip()
            name_category = input("name_category: ").strip()
            description_category = input("description_category (or leave blank): ").strip()
            if description_category == "":
                command = f"INSERT INTO CATEGORY (category_id, name_category) VALUES ('{category_id}', '{name_category}')"
            else:
                command = f"INSERT INTO CATEGORY (category_id, name_category, description_category) VALUES ('{category_id}', '{name_category}', '{description_category}')"
            print(command)
            executeInsert(command)

        elif user_input == "7":
            product_id = input("product_id: ").strip()
            name_product = input("name_product: ").strip()
            description_product = input("description_product (or leave blank): ").strip()
            price = input("price (numeric): ").strip()
            stock = input("stock (integer): ").strip()
            seller_id = input("seller_id: ").strip()
            category_id = input("category_id (leave blank for NULL): ").strip()
            category_sql = "NULL" if category_id == "" else f"'{category_id}'"
            if description_product == "":
                command = (
                    "INSERT INTO PRODUCT (product_id, name_product, price, stock, seller_id, category_id) "
                    f"VALUES ('{product_id}', '{name_product}', {price}, {stock}, '{seller_id}', {category_sql})"
                )
            else:
                command = (
                    "INSERT INTO PRODUCT (product_id, name_product, description_product, price, stock, seller_id, category_id) "
                    f"VALUES ('{product_id}', '{name_product}', '{description_product}', {price}, {stock}, '{seller_id}', {category_sql})"
                )
            print(command)
            executeInsert(command)

        elif user_input == "8":
            order_id = input("order_id: ").strip()
            customer_id = input("customer_id: ").strip()
            order_date = input("order_date (YYYY-MM-DD): ").strip()
            shipment_status = input("shipment_status (Pending/Shipped/In Transit/Delivered): ").strip()
            command = f"INSERT INTO ORDERS (order_id, customer_id, order_date, shipment_status) VALUES ('{order_id}', '{customer_id}', TO_DATE('{order_date}','YYYY-MM-DD'), '{shipment_status}')"
            print(command)
            executeInsert(command)

        elif user_input == "9":
            payment_id = input("payment_id: ").strip()
            order_id = input("order_id: ").strip()
            payment_status = input("payment_status (Pending/Paid/Failed): ").strip()
            total_amount = input("total_amount (numeric): ").strip()
            command = f"INSERT INTO PAYMENT (payment_id, order_id, payment_status, total_amount) VALUES ('{payment_id}', '{order_id}', '{payment_status}', {total_amount})"
            print(command)
            executeInsert(command)

        elif user_input == "10":
            order_id = input("order_id: ").strip()
            product_id = input("product_id: ").strip()
            quantity = input("quantity (integer): ").strip()
            command = f"INSERT INTO ORDER_ITEM (order_id, product_id, quantity) VALUES ('{order_id}', '{product_id}', {quantity})"
            print(command)
            executeInsert(command)

        elif user_input == "11":
            product_id = input("product_id (e.g. P0001): ").strip()
            unit_price = input("unit_price (numeric): ").strip()
            command = f"INSERT INTO ORDER_PRICE (product_id, unit_price) VALUES ('{product_id}', {unit_price})"
            print(command)
            executeInsert(command)

        elif user_input == "12":
            custom = input("Enter SQL Insert Query (in one line):\n")
            executeInsert(custom)

        elif user_input == "13" or user_input.lower() == "back":
            break

        elif user_input in ("14", "exit", "quit"):
            exit()

        else:
            print("Invalid option. Please choose a number from the menu.")

def searchData():
    """
    Interactive menu for searching data by primary key
    
    Functionality description：
        1. Prompt user to select which table to search
        2. Get user input based on table's primary key structure
        3. Generate SELECT WHERE statement to query data
        4. Display query results
    
    Search flow：
        1. User selects table (1-11)
        2. Enter primary key value(s) for that table
        3. Program automatically generates SELECT statement
        4. Execute query and display results
    
    Features：
        - Support searching by single primary key and composite primary keys
        - ORDER_ITEM table has two primary keys (order_id and product_id)
        - UserName table has two primary keys (first_name and last_name)
        - User input will be automatically escaped to prevent SQL injection
    """
    while True:
        print("\n-- Search By Primary Key --")
        print("1. A3_USERS")
        print("2. UserName")
        print("3. USERS_ADMIN")
        print("4. USERS_SELLER")
        print("5. USERS_CUSTOMER")
        print("6. CATEGORY")
        print("7. PRODUCT")
        print("8. ORDERS")
        print("9. PAYMENT")
        print("10. ORDER_ITEM")
        print("11. ORDER_PRICE")
        print("12. Custom Query")
        print("13. Back to Main Menu")
        print("14. Exit")

        choice = input("Enter: ").strip()

        if choice == "1":
            user_id = input("user_id (PK): ").strip().replace("'", "''")
            command = f"SELECT * FROM A3_USERS WHERE user_id = '{user_id}'"
        elif choice == "2":
            first_name = input("first_name (PK): ").strip().replace("'", "''")
            last_name = input("last_name (PK): ").strip().replace("'", "''")
            command = f"SELECT * FROM UserName WHERE first_name = '{first_name}' AND last_name = '{last_name}'"
        elif choice == "3":
            admin_id = input("admin_id (PK): ").strip().replace("'", "''")
            command = f"SELECT * FROM USERS_ADMIN WHERE admin_id = '{admin_id}'"
        elif choice == "4":
            seller_id = input("seller_id (PK): ").strip().replace("'", "''")
            command = f"SELECT * FROM USERS_SELLER WHERE seller_id = '{seller_id}'"
        elif choice == "5":
            customer_id = input("customer_id (PK): ").strip().replace("'", "''")
            command = f"SELECT * FROM USERS_CUSTOMER WHERE customer_id = '{customer_id}'"
        elif choice == "6":
            category_id = input("category_id (PK): ").strip().replace("'", "''")
            command = f"SELECT * FROM CATEGORY WHERE category_id = '{category_id}'"
        elif choice == "7":
            product_id = input("product_id (PK): ").strip().replace("'", "''")
            command = f"SELECT * FROM PRODUCT WHERE product_id = '{product_id}'"
        elif choice == "8":
            order_id = input("order_id (PK): ").strip().replace("'", "''")
            command = f"SELECT * FROM ORDERS WHERE order_id = '{order_id}'"
        elif choice == "9":
            payment_id = input("payment_id (PK): ").strip().replace("'", "''")
            command = f"SELECT * FROM PAYMENT WHERE payment_id = '{payment_id}'"
        elif choice == "10":
            order_id = input("order_id (PK): ").strip().replace("'", "''")
            product_id = input("product_id (PK): ").strip().replace("'", "''")
            command = f"SELECT * FROM ORDER_ITEM WHERE order_id = '{order_id}' AND product_id = '{product_id}'"
        elif choice == "11":
            product_id = input("product_id (PK): ").strip().replace("'", "''")
            command = f"SELECT * FROM ORDER_PRICE WHERE product_id = '{product_id}'"
        elif choice == "12":
            command = input("Enter custom SELECT query: ").strip()
            if not command.lstrip().upper().startswith("SELECT"):
                print("Only SELECT statements are allowed. Try again.")
                continue
        elif choice == "13":
            break
        elif choice == "14":
            print("Exiting.")
            exit(0)
        else:
            print("Invalid choice. Try again.")
            continue

        print("\nGenerated SQL:")
        print(command)

        try:
            executeQuery(command)
        except Exception as e:
            print(f"Error executing query: {e}")

def updateRecord():
    while True:
        print("\n-- Update Menu --")
        print("1. A3_USERS")
        print("2. UserName")
        print("3. USERS_ADMIN")
        print("4. USERS_SELLER")
        print("5. USERS_CUSTOMER")
        print("6. CATEGORY")
        print("7. PRODUCT")
        print("8. ORDERS")
        print("9. PAYMENT")
        print("10. ORDER_ITEM")
        print("11. ORDER_PRICE")
        print("12. Custom Query")
        print("13. Back to Main Menu")
        print("14. Exit")

        choice = input("Enter: ").strip()

        if choice == "1":
            pk_col = "user_id"
            pk_val = input(f"{pk_col} (PK): ").strip().replace("'", "''")
            table = "A3_USERS"
            where = f"{pk_col} = '{pk_val}'"
        elif choice == "2":
            pk1 = input("first_name (PK): ").strip().replace("'", "''")
            pk2 = input("last_name (PK): ").strip().replace("'", "''")
            table = "UserName"
            where = f"first_name = '{pk1}' AND last_name = '{pk2}'"
        elif choice == "3":
            pk_col = "admin_id"
            pk_val = input(f"{pk_col} (PK): ").strip().replace("'", "''")
            table = "USERS_ADMIN"
            where = f"{pk_col} = '{pk_val}'"
        elif choice == "4":
            pk_col = "seller_id"
            pk_val = input(f"{pk_col} (PK): ").strip().replace("'", "''")
            table = "USERS_SELLER"
            where = f"{pk_col} = '{pk_val}'"
        elif choice == "5":
            pk_col = "customer_id"
            pk_val = input(f"{pk_col} (PK): ").strip().replace("'", "''")
            table = "USERS_CUSTOMER"
            where = f"{pk_col} = '{pk_val}'"
        elif choice == "6":
            pk_col = "category_id"
            pk_val = input(f"{pk_col} (PK): ").strip().replace("'", "''")
            table = "CATEGORY"
            where = f"{pk_col} = '{pk_val}'"
        elif choice == "7":
            pk_col = "product_id"
            pk_val = input(f"{pk_col} (PK): ").strip().replace("'", "''")
            table = "PRODUCT"
            where = f"{pk_col} = '{pk_val}'"
        elif choice == "8":
            pk_col = "order_id"
            pk_val = input(f"{pk_col} (PK): ").strip().replace("'", "''")
            table = "ORDERS"
            where = f"{pk_col} = '{pk_val}'"
        elif choice == "9":
            pk_col = "payment_id"
            pk_val = input(f"{pk_col} (PK): ").strip().replace("'", "''")
            table = "PAYMENT"
            where = f"{pk_col} = '{pk_val}'"
        elif choice == "10":
            pk1 = input("order_id (PK): ").strip().replace("'", "''")
            pk2 = input("product_id (PK): ").strip().replace("'", "''")
            table = "ORDER_ITEM"
            where = f"order_id = '{pk1}' AND product_id = '{pk2}'"
        elif choice == "11":
            pk_col = "product_id"
            pk_val = input(f"{pk_col} (PK): ").strip().replace("'", "''")
            table = "ORDER_PRICE"
            where = f"{pk_col} = '{pk_val}'"
        elif choice == "12":
            command = input("Enter custom UPDATE query (must start with UPDATE): ").strip()
            if not command.lstrip().upper().startswith("UPDATE"):
                print("Custom query must be an UPDATE statement. Try again.")
                continue
            print("\nGenerated SQL:")
            print(command)
            confirm = input("Execute this UPDATE? (yes/no): ").strip().lower()
            if confirm in ("y", "yes"):
                try:
                    executeUpdate(command)
                    print("Update executed.")
                except Exception as e:
                    print(f"Error executing update: {e}")
            else:
                print("Update cancelled.")
            continue
        elif choice == "13":
            break
        elif choice == "14":
            print("Exiting.")
            exit(0)
        else:
            print("Invalid choice. Try again.")
            continue

        print("\nEnter column assignments for SET clause.")
        print("For each column enter: column_name")
        print("Then enter the new value. Leave column_name blank to finish.")
        assignments = []
        while True:
            col = input("Column name (leave blank to finish): ").strip()
            if not col:
                break
            val = input(f"New value for {col} (enter NULL for SQL NULL): ").strip()
            if val.upper() == "NULL":
                assignments.append(f"{col} = NULL")
            else:
                val_escaped = val.replace("'", "''")
                assignments.append(f"{col} = '{val_escaped}'")

        if not assignments:
            print("No assignments provided. Update cancelled.")
            continue

        set_clause = ", ".join(assignments)
        command = f"UPDATE {table} SET {set_clause} WHERE {where}"

        print("\nGenerated SQL:")
        print(command)
        confirm = input("Are you sure you want to execute this UPDATE? (yes/no): ").strip().lower()
        if confirm not in ("y", "yes"):
            print("Update cancelled.")
            continue

        try:
            executeUpdate(command)
            print("Update executed.")
        except Exception as e:
            print(f"Error executing update: {e}")

def executeUpdate(command: str) -> int:
    if not isinstance(command, str) or not command.strip():
        raise ValueError("command must be a non-empty SQL string.")

    if not command.lstrip().upper().startswith("UPDATE"):
        raise ValueError("Only UPDATE statements are allowed by executeUpdate().")

    conn = globals().get("connection") or globals().get("conn") or globals().get("db_conn")
    if conn is None:
        raise ValueError("No DB connection found. Provide a global 'connection', 'conn', or 'db_conn' object.")

    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(command)
        affected = cursor.rowcount if cursor.rowcount is not None else -1
        conn.commit()
        return affected
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass

def simpleQuery():
    tables = {
        "1": "A3_USERS",
        "2": "UserName",
        "3": "USERS_ADMIN",
        "4": "USERS_SELLER",
        "5": "USERS_CUSTOMER",
        "6": "CATEGORY",
        "7": "PRODUCT",
        "8": "ORDERS",
        "9": "PAYMENT",
        "10": "ORDER_ITEM",
        "11": "ORDER_PRICE"
    }

    while True:
        print("\n-- Simple Query Menu --")
        for k in sorted(tables.keys(), key=lambda x: int(x)):
            print(f"{k}. {tables[k]}")
        print("12. Custom Query")
        print("13. Back to Main Menu")
        print("14. Exit")

        choice = input("Enter: ").strip()

        if choice in tables:
            table = tables[choice]
            command = f"SELECT * FROM {table}"
        elif choice == "12":
            command = input("Enter custom SELECT query: ").strip()
            if not command.lstrip().upper().startswith("SELECT"):
                print("Only SELECT statements are allowed. Try again.")
                continue
        elif choice == "13":
            break
        elif choice == "14":
            print("Exiting.")
            exit(0)
        else:
            print("Invalid choice. Try again.")
            continue

        print("\nGenerated SQL:")
        print(command)

        try:
            executeQuery(command)
        except Exception as e:
            print(f"Error executing query: {e}")

def deleteRecord() -> None:
    while True:
        print("\n-- Delete Menu --")
        print("1. A3_USERS")
        print("2. UserName")
        print("3. USERS_ADMIN")
        print("4. USERS_SELLER")
        print("5. USERS_CUSTOMER")
        print("6. CATEGORY")
        print("7. PRODUCT")
        print("8. ORDERS")
        print("9. PAYMENT")
        print("10. ORDER_ITEM")
        print("11. ORDER_PRICE")
        print("12. Custom Query")
        print("13. Back to Main Menu")
        print("14. Exit")

        choice = input("Enter: ").strip()

        if choice == "1":
            user_id = input("user_id (PK): ").strip()
            command = f"DELETE FROM A3_USERS WHERE user_id = '{user_id}'"
        elif choice == "2":
            first_name = input("first_name (PK): ").strip()
            last_name = input("last_name (PK): ").strip()
            command = f"DELETE FROM UserName WHERE first_name = '{first_name}' AND last_name = '{last_name}'"
        elif choice == "3":
            admin_id = input("admin_id (PK): ").strip()
            command = f"DELETE FROM USERS_ADMIN WHERE admin_id = '{admin_id}'"
        elif choice == "4":
            seller_id = input("seller_id (PK): ").strip()
            command = f"DELETE FROM USERS_SELLER WHERE seller_id = '{seller_id}'"
        elif choice == "5":
            customer_id = input("customer_id (PK): ").strip()
            command = f"DELETE FROM USERS_CUSTOMER WHERE customer_id = '{customer_id}'"
        elif choice == "6":
            category_id = input("category_id (PK): ").strip()
            command = f"DELETE FROM CATEGORY WHERE category_id = '{category_id}'"
        elif choice == "7":
            product_id = input("product_id (PK): ").strip()
            command = f"DELETE FROM PRODUCT WHERE product_id = '{product_id}'"
        elif choice == "8":
            order_id = input("order_id (PK): ").strip()
            command = f"DELETE FROM ORDERS WHERE order_id = '{order_id}'"
        elif choice == "9":
            payment_id = input("payment_id (PK): ").strip()
            command = f"DELETE FROM PAYMENT WHERE payment_id = '{payment_id}'"
        elif choice == "10":
            order_id = input("order_id (PK): ").strip()
            product_id = input("product_id (PK): ").strip()
            command = (f"DELETE FROM ORDER_ITEM WHERE order_id = '{order_id}' "
                       f"AND product_id = '{product_id}'")
        elif choice == "11":
            product_id = input("product_id (PK): ").strip()
            command = f"DELETE FROM ORDER_PRICE WHERE product_id = '{product_id}'"
        elif choice == "12":
            command = input("Enter custom DELETE query (must be a DELETE statement): ").strip()
            if not command.upper().lstrip().startswith("DELETE"):
                print("Custom query must be a DELETE statement. Skipping.")
                continue
        elif choice == "13":
            break
        elif choice == "14":
            print("Exiting.")
            exit(0)
        else:
            print("Invalid choice. Try again.")
            continue


        print("\nGenerated SQL:")
        print(command)
        confirm = input("Are you sure you want to execute this DELETE? (yes/no): ").strip().lower()
        if confirm in ("y", "yes"):
            try:
                executeDelete(command)
                print("Delete executed.")
            except Exception as e:
                print(f"Error executing delete: {e}")
        else:
            print("Delete cancelled.")

def executeDelete(command: str) -> int:
    if not isinstance(command, str) or not command.strip():
        raise ValueError("command must be a non-empty SQL string.")

    if not command.lstrip().upper().startswith("DELETE"):
        raise ValueError("Only DELETE statements are allowed by executeDelete")

    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(command)
        affected = cursor.rowcount if cursor.rowcount is not None else -1
        connection.commit()
        return affected
    except Exception:
        try:
            connection.rollback()
        except Exception:
            pass
        raise
    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass
        
def insert() -> None:
  print("\n-- Insert Menu -- ")
  listTables()
  print("9. Custom Query")
  print("10. Back to Main Menu")
  print("11. Exit") 
        
def query() -> None:
    import random
    while True:
        print("\n-- Query Menu -- ")
        print("1. Select product names and their average prices above overall average")
        print("2. Count distinct products that share the same name")
        print("3. Select users who are sellers or buyers")
        print("4. Select users who have both sold and bought")
        print("5. Select users who are buyers but not sellers")
        print("6. Custom Query")
        print("7. Back to Main Menu")
        print("8. Exit")

        user_input = input("Enter: ").strip()

        if user_input == "1":
            queries = [
                """
                SELECT name_product, AVG(price) AS avg_price
                FROM PRODUCT
                GROUP BY name_product
                HAVING AVG(price) > (SELECT AVG(price) FROM PRODUCT)
                """,
                """
                SELECT c.name_category, AVG(p.price) AS avg_price
                FROM PRODUCT p
                JOIN CATEGORY c ON p.category_id = c.category_id
                GROUP BY c.name_category
                HAVING AVG(p.price) > (SELECT AVG(price) FROM PRODUCT)
                """,
                """
                SELECT p.name_product, AVG(op.unit_price) AS avg_order_price
                FROM ORDER_ITEM oi
                JOIN ORDER_PRICE op ON oi.product_id = op.product_id
                JOIN PRODUCT p ON oi.product_id = p.product_id
                GROUP BY p.name_product
                HAVING AVG(op.unit_price) > (SELECT AVG(unit_price) FROM ORDER_PRICE)
                """
            ]
            query = random.choice(queries)
            print(query)
            executeQuery(query)

        elif user_input == "2":
            queries = [
                """
                SELECT name_product, COUNT(DISTINCT product_id) AS product_count
                FROM PRODUCT
                GROUP BY name_product
                HAVING COUNT(DISTINCT product_id) > 1
                """,
                """
                SELECT name_product, COUNT(*) AS rows_with_name
                FROM PRODUCT
                GROUP BY name_product
                HAVING COUNT(*) > 1
                """,
                """
                SELECT name_product, COUNT(DISTINCT product_id) AS distinct_products
                FROM PRODUCT
                GROUP BY name_product
                """
            ]
            query = random.choice(queries)
            print(query)
            executeQuery(query)

        elif user_input == "3":
            queries = [
                """
                SELECT a.user_id, a.first_name, a.last_name
                FROM A3_USERS a
                WHERE EXISTS (SELECT 1 FROM USERS_SELLER s WHERE s.seller_id = a.user_id)
                   OR EXISTS (SELECT 1 FROM ORDERS o WHERE o.customer_id = a.user_id)
                """,
                """
                SELECT DISTINCT a.user_id, a.first_name, a.last_name
                FROM A3_USERS a
                JOIN USERS_SELLER s ON a.user_id = s.seller_id
                UNION
                SELECT DISTINCT a2.user_id, a2.first_name, a2.last_name
                FROM A3_USERS a2
                JOIN ORDERS o2 ON a2.user_id = o2.customer_id
                """,
                """
                SELECT a.user_id, a.first_name, a.last_name
                FROM A3_USERS a
                WHERE a.user_type IN ('SELLER','CUSTOMER')
                AND (a.user_id IN (SELECT seller_id FROM USERS_SELLER) OR a.user_id IN (SELECT customer_id FROM ORDERS))
                """
            ]
            query = random.choice(queries)
            print(query)
            executeQuery(query)

        elif user_input == "4":
            queries = [
                """
                SELECT a.user_id, a.first_name, a.last_name
                FROM A3_USERS a
                WHERE EXISTS (SELECT 1 FROM USERS_SELLER s WHERE s.seller_id = a.user_id)
                  AND EXISTS (SELECT 1 FROM ORDERS o WHERE o.customer_id = a.user_id)
                """,
                """
                SELECT DISTINCT a.user_id, a.first_name, a.last_name
                FROM A3_USERS a
                JOIN USERS_SELLER s ON a.user_id = s.seller_id
                JOIN ORDERS o ON a.user_id = o.customer_id
                """,
                """
                SELECT a.user_id, a.first_name, a.last_name
                FROM A3_USERS a
                WHERE a.user_id IN (SELECT seller_id FROM USERS_SELLER)
                  AND a.user_id IN (SELECT customer_id FROM ORDERS)
                """
            ]
            query = random.choice(queries)
            print(query)
            executeQuery(query)

        elif user_input == "5":
            queries = [
                """
                SELECT a.user_id, a.first_name, a.last_name
                FROM A3_USERS a
                WHERE EXISTS (SELECT 1 FROM ORDERS o WHERE o.customer_id = a.user_id)
                  AND NOT EXISTS (SELECT 1 FROM USERS_SELLER s WHERE s.seller_id = a.user_id)
                """,
                """
                SELECT DISTINCT a.user_id, a.first_name, a.last_name
                FROM A3_USERS a
                JOIN ORDERS o ON a.user_id = o.customer_id
                WHERE a.user_id NOT IN (SELECT seller_id FROM USERS_SELLER)
                """,
                """
                SELECT a.user_id, a.first_name, a.last_name
                FROM A3_USERS a
                WHERE a.user_type = 'CUSTOMER'
                  AND a.user_id NOT IN (SELECT seller_id FROM USERS_SELLER)
                  AND a.user_id IN (SELECT customer_id FROM ORDERS)
                """
            ]
            query = random.choice(queries)
            print(query)
            executeQuery(query)

        elif user_input == "6":
            custom = input("Enter SQL Query (in one line):\n")
            executeQuery(custom)

        elif user_input == "7" or user_input.lower() == "back":
            break

        elif user_input in ("8", "exit", "quit"):
            exit()

        else:
            print("Invalid option. Please choose a number from the menu.")
        
def main() -> None:
    """
    Main menu - Command line interface entry point for database management system
    
    Functionality description:
        1. Display list of all existing tables
        2. Present a looping menu for users to select various operations
        3. Execute different functions based on user input
    
    Menu options:
        1. DROP ALL TABLES - Delete all tables (for re-initialization only)
        2. Create all Tables - Create table structures
        3. Populate all Tables - Fill in sample data
        4. Query Data (Advanced) - Execute advanced queries (such as querying users with two roles)
        5. Insert Data - Manually insert data
        6. Delete Data - Delete specified data records
        7. Query Data (Simple) - Simple query (display all data of entire table)
        8. Search Data using PK - Search data by primary key
        9. Update Data - Update existing data
        11. Exit - Exit program
    
    Process flow:
        1. First display all tables in current database
        2. Enter infinite loop until user chooses to exit
        3. Perform corresponding operation for each selection
    """
    # Display all tables in current database
    listTables()
    print("--")
    # Enter main menu loop
    while True: 
        print("\n-- Main Menu -- ")
        print("1. DROP ALL TABLES")
        print("2. Create all Tables")
        print("3. Populate all Tables with existing values")
        print("4. Query Data (Advanced)")
        print("5. Insert Data")
        print("6. Delete Data")
        print("7. Query Data (Simple)")
        print("8. Search Data using PK")
        print("9. Update Data")
        print("11. Exit")
        user_input = input("Enter: ")
    
        if (user_input == "1"):
            dropTables()
    
        elif (user_input == "2"):
            createTables()
        
        elif (user_input == "3"):
            populateTables()
        
        elif (user_input == "4"):
            query()
                   
        elif (user_input == "5"):
            insertData()

        elif (user_input == "6"):
            deleteRecord()

        elif (user_input == "7"):
            simpleQuery()
        
        elif (user_input == "8"):
            searchData()
      
        elif (user_input == "9"):
            updateRecord()
        
        elif (user_input == "10"):
          simpleQuery()
      
        elif (user_input == "11" or user_input == "exit" or user_input == "quit"):
            exit()


# ===== Program Entry Point =====
# This code ensures program only executes when run directly, not when imported as module
# Benefit of this design is Flask web_app.py can import this module without triggering menu
if __name__ == "__main__":
    """
    CLI mode program entry point
    
    Execution steps:
        1. Prompt user to enter Oracle database username
        2. Prompt user to enter Oracle database password
        3. Call init_connection() to establish database connection
        4. Enter main() menu to start interaction
    
    Note:
        - This code only executes when running this script directly (python main.py)
        - If imported from other modules (like web_app.py), this code will not execute
        - This ensures compatibility between CLI and Web usage modes
    """
    # Prompt user to enter database credentials
    user = input("Enter Oracle DB username: ")
    pw = input("Enter Oracle DB password: ")
    # Initialize global database connection
    init_connection(user, pw)
    # Enter main menu
    main()