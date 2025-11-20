# ==========================
# File: web_app.py
# E-Commerce DBMS - Flask Web Application
# ==========================

from flask import Flask, render_template, request, redirect, url_for, session, flash
import oracledb
import main  # import the backend logic from main.py

app = Flask(__name__)
app.secret_key = "change_me_to_random_string"  # needed for session

ORACLE_HOST = "oracle12c.scs.ryerson.ca"
ORACLE_PORT = 1521
ORACLE_SID = "orcl12c"


def ensure_connection():
    """Use credentials stored in session to initialize main.connection.
    Returns a live connection object or None if not logged in.
    """
    user = session.get("db_user")
    pw = session.get("db_pass")
    if not user or not pw:
        return None

    # Initialize global connection/cursor in main.py
    main.init_connection(user, pw, host=ORACLE_HOST, port=ORACLE_PORT, sid=ORACLE_SID)
    return main.connection


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Simple login page that tests Oracle credentials
    and stores them in the session on success.
    """
    if request.method == "POST":
        user = request.form.get("username")
        pw = request.form.get("password")

        try:
            test_conn = oracledb.connect(
                user=user,
                password=pw,
                host=ORACLE_HOST,
                port=ORACLE_PORT,
                sid=ORACLE_SID,
            )
            test_conn.close()
        except Exception as e:
            flash(f"Login failed: {e}")
            return render_template("login.html")

        session["db_user"] = user
        session["db_pass"] = pw
        flash("Login successful.")
        return redirect(url_for("menu"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.")
    return redirect(url_for("login"))


@app.route("/menu")
def menu():
    if "db_user" not in session:
        return redirect(url_for("login"))
    return render_template("menu.html")


@app.route("/drop_menu")
def drop_menu():
    """Display drop tables submenu"""
    if "db_user" not in session:
        return redirect(url_for("login"))
    return render_template("drop_menu.html")


@app.route("/create_menu")
def create_menu():
    """Display create tables submenu"""
    if "db_user" not in session:
        return redirect(url_for("login"))
    return render_template("create_menu.html")


@app.route("/populate_menu")
def populate_menu():
    """Display populate tables submenu"""
    if "db_user" not in session:
        return redirect(url_for("login"))
    return render_template("populate_menu.html")


@app.route("/drop_all")
def drop_all_tables():
    """Drop all tables at once"""
    if "db_user" not in session:
        return redirect(url_for("login"))

    ensure_connection()
    try:
        main.dropTables()
        flash("All tables dropped successfully.")
    except Exception as e:
        flash(f"Error dropping tables: {e}")
    return redirect(url_for("drop_menu"))


@app.route("/drop/<table_name>")
def drop_single_table(table_name):
    """Drop a single table"""
    if "db_user" not in session:
        return redirect(url_for("login"))

    # Validate table name to prevent SQL injection
    allowed_tables = ['A3_USERS', 'UserName', 'USERS_ADMIN', 'USERS_SELLER', 'USERS_CUSTOMER',
                     'CATEGORY', 'PRODUCT', 'ORDERS', 'PAYMENT', 'ORDER_ITEM', 'ORDER_PRICE']
    
    if table_name not in allowed_tables:
        flash(f"Invalid table name: {table_name}")
        return redirect(url_for("drop_menu"))

    conn = ensure_connection()
    try:
        cur = conn.cursor()
        cur.execute(f"DROP TABLE {table_name} CASCADE CONSTRAINTS")
        conn.commit()
        cur.close()
        flash(f"Table {table_name} dropped successfully.")
    except Exception as e:
        flash(f"Error dropping table {table_name}: {e}")
    
    return redirect(url_for("drop_menu"))


@app.route("/create_all")
def create_all_tables():
    """Create all tables at once"""
    if "db_user" not in session:
        return redirect(url_for("login"))

    ensure_connection()
    try:
        main.createTables()
        flash("All tables created successfully.")
    except Exception as e:
        flash(f"Error creating tables: {e}")
    return redirect(url_for("create_menu"))


@app.route("/create/<table_name>")
def create_single_table(table_name):
    """Create a single table"""
    if "db_user" not in session:
        return redirect(url_for("login"))

    # Validate table name to prevent SQL injection
    allowed_tables = ['A3_USERS', 'UserName', 'USERS_ADMIN', 'USERS_SELLER', 'USERS_CUSTOMER',
                     'CATEGORY', 'PRODUCT', 'ORDERS', 'PAYMENT', 'ORDER_ITEM', 'ORDER_PRICE']
    
    if table_name not in allowed_tables:
        flash(f"Invalid table name: {table_name}")
        return redirect(url_for("create_menu"))

    conn = ensure_connection()
    try:
        main.createSingleTable(table_name)
        flash(f"Table {table_name} created successfully.")
    except Exception as e:
        flash(f"Error creating table {table_name}: {e}")
    
    return redirect(url_for("create_menu"))


@app.route("/populate_all")
def populate_all_tables():
    """Populate all tables with sample data at once"""
    if "db_user" not in session:
        return redirect(url_for("login"))

    ensure_connection()
    try:
        main.populateTables()
        flash("All tables populated with sample data successfully.")
    except Exception as e:
        flash(f"Error populating tables: {e}")
    return redirect(url_for("populate_menu"))


@app.route("/populate/<table_name>")
def populate_single_table(table_name):
    """Populate a single table with sample data"""
    if "db_user" not in session:
        return redirect(url_for("login"))

    # Validate table name to prevent SQL injection
    allowed_tables = ['A3_USERS', 'UserName', 'USERS_ADMIN', 'USERS_SELLER', 'USERS_CUSTOMER',
                     'CATEGORY', 'PRODUCT', 'ORDERS', 'PAYMENT', 'ORDER_ITEM', 'ORDER_PRICE']
    
    if table_name not in allowed_tables:
        flash(f"Invalid table name: {table_name}")
        return redirect(url_for("populate_menu"))

    conn = ensure_connection()
    try:
        main.populateSingleTable(table_name)
        flash(f"Table {table_name} populated successfully.")
    except Exception as e:
        flash(f"Error populating table {table_name}: {e}")
    
    return redirect(url_for("populate_menu"))


@app.route("/drop")
def drop_tables():
    if "db_user" not in session:
        return redirect(url_for("login"))

    ensure_connection()
    try:
        main.dropTables()
        flash("All tables dropped.")
    except Exception as e:
        flash(f"Error dropping tables: {e}")
    return redirect(url_for("menu"))


@app.route("/create")
def create_tables():
    if "db_user" not in session:
        return redirect(url_for("login"))

    ensure_connection()
    try:
        main.createTables()
        flash("All tables created.")
    except Exception as e:
        flash(f"Error creating tables: {e}")
    return redirect(url_for("menu"))


@app.route("/populate")
def populate_tables():
    if "db_user" not in session:
        return redirect(url_for("login"))

    ensure_connection()
    try:
        main.populateTables()
        flash("All tables populated with sample data.")
    except Exception as e:
        flash(f"Error populating tables: {e}")
    return redirect(url_for("menu"))


@app.route("/tables")
def tables():
    if "db_user" not in session:
        return redirect(url_for("login"))

    conn = ensure_connection()
    table_names = []
    try:
        cur = conn.cursor()
        cur.execute("SELECT table_name FROM user_tables ORDER BY table_name")
        rows = cur.fetchall()
        table_names = [r[0] for r in rows]
        cur.close()
    except Exception as e:
        flash(f"Error fetching tables: {e}")

    return render_template("tables.html", tables=table_names)


@app.route("/table/<name>")
def view_table(name):
    if "db_user" not in session:
        return redirect(url_for("login"))

    conn = ensure_connection()
    columns = []
    rows = []
    try:
        cur = conn.cursor()
        sql = f"SELECT * FROM {name}"
        cur.execute(sql)
        rows = cur.fetchall()
        columns = [d[0] for d in cur.description] if cur.description else []
        cur.close()
    except Exception as e:
        flash(f"Error fetching data from {name}: {e}")

    return render_template(
        "query_result.html",
        title=f"Table: {name}",
        columns=columns,
        rows=rows,
    )


@app.route("/advanced")
def advanced_query():
    """Query: users who are both sellers and buyers."""
    if "db_user" not in session:
        return redirect(url_for("login"))

    conn = ensure_connection()
    sql = """
    SELECT a.user_id, a.first_name, a.last_name
    FROM A3_USERS a
    WHERE EXISTS (SELECT 1 FROM USERS_SELLER s WHERE s.seller_id = a.user_id)
      AND EXISTS (SELECT 1 FROM ORDERS o WHERE o.customer_id = a.user_id)
    """

    columns = []
    rows = []
    try:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        columns = [d[0] for d in cur.description] if cur.description else []
        cur.close()
    except Exception as e:
        flash(f"Error executing advanced query: {e}")

    return render_template(
        "query_result.html",
        title="Query 1: Product names and their average prices above overall average",
        columns=columns,
        rows=rows,
    )


@app.route("/query1")
def query1():
    """Query 1: Product names and their average prices above overall average"""
    if "db_user" not in session:
        return redirect(url_for("login"))

    conn = ensure_connection()
    sql = """
    SELECT name_product, AVG(price) AS avg_price
    FROM PRODUCT
    GROUP BY name_product
    HAVING AVG(price) > (SELECT AVG(price) FROM PRODUCT)
    """

    columns = []
    rows = []
    try:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        columns = [d[0] for d in cur.description] if cur.description else []
        cur.close()
    except Exception as e:
        flash(f"Error executing query: {e}")

    return render_template(
        "query_result.html",
        title="Query 1: Product names and their average prices above overall average",
        columns=columns,
        rows=rows,
    )


@app.route("/query2")
def query2():
    """Query 2: Count distinct products that share the same name"""
    if "db_user" not in session:
        return redirect(url_for("login"))

    conn = ensure_connection()
    sql = """
    SELECT name_product, COUNT(DISTINCT product_id) AS product_count
    FROM PRODUCT
    GROUP BY name_product
    HAVING COUNT(DISTINCT product_id) > 1
    """

    columns = []
    rows = []
    try:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        columns = [d[0] for d in cur.description] if cur.description else []
        cur.close()
    except Exception as e:
        flash(f"Error executing query: {e}")

    return render_template(
        "query_result.html",
        title="Query 2: Count distinct products that share the same name",
        columns=columns,
        rows=rows,
    )


@app.route("/query3")
def query3():
    """Query 3: Users who are sellers or buyers"""
    if "db_user" not in session:
        return redirect(url_for("login"))

    conn = ensure_connection()
    sql = """
    SELECT a.user_id, a.first_name, a.last_name
    FROM A3_USERS a
    WHERE EXISTS (SELECT 1 FROM USERS_SELLER s WHERE s.seller_id = a.user_id)
       OR EXISTS (SELECT 1 FROM ORDERS o WHERE o.customer_id = a.user_id)
    """

    columns = []
    rows = []
    try:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        columns = [d[0] for d in cur.description] if cur.description else []
        cur.close()
    except Exception as e:
        flash(f"Error executing query: {e}")

    return render_template(
        "query_result.html",
        title="Query 3: Users who are sellers or buyers",
        columns=columns,
        rows=rows,
    )


@app.route("/query4")
def query4():
    """Query 4: Users who have both sold and bought"""
    if "db_user" not in session:
        return redirect(url_for("login"))

    conn = ensure_connection()
    sql = """
    SELECT a.user_id, a.first_name, a.last_name
    FROM A3_USERS a
    WHERE EXISTS (SELECT 1 FROM USERS_SELLER s WHERE s.seller_id = a.user_id)
      AND EXISTS (SELECT 1 FROM ORDERS o WHERE o.customer_id = a.user_id)
    """

    columns = []
    rows = []
    try:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        columns = [d[0] for d in cur.description] if cur.description else []
        cur.close()
    except Exception as e:
        flash(f"Error executing query: {e}")

    return render_template(
        "query_result.html",
        title="Query 4: Users who are both sellers and buyers",
        columns=columns,
        rows=rows,
    )


@app.route("/query5")
def query5():
    """Query 5: Users who are buyers but not sellers"""
    if "db_user" not in session:
        return redirect(url_for("login"))

    conn = ensure_connection()
    sql = """
    SELECT a.user_id, a.first_name, a.last_name
    FROM A3_USERS a
    WHERE EXISTS (SELECT 1 FROM ORDERS o WHERE o.customer_id = a.user_id)
      AND NOT EXISTS (SELECT 1 FROM USERS_SELLER s WHERE s.seller_id = a.user_id)
    """

    columns = []
    rows = []
    try:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        columns = [d[0] for d in cur.description] if cur.description else []
        cur.close()
    except Exception as e:
        flash(f"Error executing query: {e}")

    return render_template(
        "query_result.html",
        title="Query 5: Users who are buyers but not sellers",
        columns=columns,
        rows=rows,
    )


@app.route("/query6", methods=["GET", "POST"])
def query6():
    """Query 6: Custom query - user enters their own SQL SELECT statement"""
    if "db_user" not in session:
        return redirect(url_for("login"))

    if request.method == "GET":
        # Show the custom query form
        return render_template("custom_query.html")

    # Handle POST - execute the custom query
    sql = request.form.get("sql_query", "").strip()
    
    if not sql:
        flash("Please enter a SQL query")
        return render_template("custom_query.html")
    
    # Validate that it's a SELECT statement
    if not sql.lstrip().upper().startswith("SELECT"):
        flash("Only SELECT statements are allowed")
        return render_template("custom_query.html")

    conn = ensure_connection()
    columns = []
    rows = []
    try:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        columns = [d[0] for d in cur.description] if cur.description else []
        cur.close()
    except Exception as e:
        flash(f"Error executing query: {e}")
        return render_template("custom_query.html")

    return render_template(
        "query_result.html",
        title="Query 6: Custom Query",
        columns=columns,
        rows=rows,
    )


if __name__ == "__main__":
    app.run(debug=True)