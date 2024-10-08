from flask import Flask, redirect, render_template, request, session, after_this_request, url_for
from flask_session import Session
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import asyncio
import random
import string
from datetime import timedelta

app = Flask(__name__)

#session in to a file
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_REFRESH_EACH_REQUEST"] = False
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=30)
app.jinja_env.lstrip_blocks = True
app.jinja_env.trim_blocks = True

Session(app)

conn = sqlite3.connect('store.db', check_same_thread=False)

cursor = conn.cursor()

@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    return response

@app.route("/")
def layout():
    return render_template("layout.html")

@app.route("/home")
def home():
    user_id = session.get('user_id')
    return render_template("home.html", userState = user_id)


@app.route("/login", methods=["POST", "GET"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("login"):
            return ("You must provide login", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return ("You must provide password", 403)

        # Query database for login
        cursor.execute("SELECT * FROM users WHERE login = ?", (request.form.get("login"),))

        rows = cursor.fetchone()
        
        # Ensure login exists and password is correct
        if rows[0] != 1 and check_password_hash(rows[2], request.form.get("password")) == False:
            return("Invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]
        session.permanent = True
        # Redirect user to home page
        return redirect("/home")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""
    user_id = session.get('user_id')
    cursor.execute("DELETE FROM cart where user_id = ?", (user_id,))
    conn.commit()
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/home")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()

    if request.method == "POST":

        if not request.form.get("login"):
            return ("Please provide the username", 400)
        elif not request.form.get("password"):
            return ("Please provide the password", 400)
        elif not request.form.get("confirmation"):
            return ("Please confirm the password", 400)
        elif request.form.get("password") != request.form.get("confirmation"):
            return ("Provided passwords do not match", 400)

        get_Login = cursor.execute("SELECT count(*) FROM users where login = ?", (request.form.get("login"),))

        rows = get_Login.fetchone()

        if rows[0] == 1:
            return ("Provided username already exists", 400)
        
        cursor.execute("INSERT INTO users (login, password) VALUES(?, ?)", (request.form.get("login"), generate_password_hash(request.form.get("password"))))

        conn.commit()
        
        get_Login = cursor.execute("SELECT * FROM users where login = ?", (request.form.get("login"),))
        
        session["user_id"] = get_Login.fetchone()[0]
        
        return redirect("/")

    else:
        return render_template("register.html")
    

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


#store user_id in session
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        conn.user = None
    else:
        conn.user = cursor.execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@app.route("/panel", methods=["GET", "POST"])
@login_required
def panel():
    user_id = session.get('user_id')

    if request.method == "GET":

        get_Login = cursor.execute("SELECT * FROM users where id = ?", ((user_id),)).fetchone()[1]

        get_OrdersCount = cursor.execute("SELECT COUNT(*) FROM orders WHERE user_id = ? GROUP BY order_id", ((user_id),)).fetchall()
        
        get_OrdersID = cursor.execute("SELECT order_id FROM orders WHERE user_id = ? GROUP BY order_id", ((user_id),)).fetchall()

        get_OrderDetails = cursor.execute("select order_id, timestamp, GROUP_CONCAT(products.name, ', '), GROUP_CONCAT(cart_quantity, ', '), GROUP_CONCAT(cart_price, ', '), total from orders LEFT JOIN products ON products.id = orders.product_id WHERE orders.user_id = ? GROUP BY order_id", ((user_id),)).fetchall()

        print(get_OrderDetails)

    return render_template("panel.html", username = get_Login, orders = get_OrderDetails, count=get_OrdersCount)


@app.route("/products", methods=["GET", "POST"])
@login_required
def products():
    get_Products = cursor.execute("SELECT products.*, SUM(cart.product_quantity) FROM products LEFT JOIN cart ON cart.product_id = products.id GROUP BY products.id").fetchall()
    get_Count = cursor.execute("SELECT COUNT(*) FROM products").fetchone()

    return render_template("products.html", products = get_Products, count = get_Count)

@login_required
@app.route("/add_to_cart/<int:productId>", methods=["GET", "POST"])
async def add_to_cart(productId):

    if request.method == "POST":

        user_id = session.get('user_id')

        async def get_data():
            
            datajson = request.get_json()

            return datajson
        
        data = await get_data()

        productid = data.get("productId")

        productname = data.get("productName")

        productprice = data.get("productPrice")

        productquantity = data.get("productStock")


        async def cart_data():
            get_Cart_Data = cursor.execute("SELECT * FROM cart where user_id = ?", (user_id, )).fetchall()
            return get_Cart_Data
        
        async def cart_data_count():
            get_Cart_Data_Count = cursor.execute("SELECT COUNT(*) FROM cart where user_id = ? and product_id = ?", (user_id, productid)).fetchall()
            
            return get_Cart_Data_Count

        get_Cart_Data = await cart_data()

        get_Cart_Data_Count = await cart_data_count()


        async def cart_update():
            if get_Cart_Data_Count[0][0] == 0:
                cursor.execute("INSERT INTO cart (user_id, product_id, product_name, product_quantity, product_price) VALUES(?, ?, ?, ?, ?)", (user_id, productid, productname, productquantity, productprice))
                conn.commit()
            elif get_Cart_Data_Count[0][0] > 0:
                for i in get_Cart_Data:
                    if i[1] == user_id and i[3] == int(productid):
                        cursor.execute("UPDATE cart SET product_quantity = ? where user_id = ? and product_id = ? and id = ?", (int(i[5]) + 1, user_id, int(productid), i[0]))
                        conn.commit()

        async def chain(*functions):
            return [await f for f in functions]
        
        await chain(get_data(), cart_data(), cart_data_count(), cart_update())

    return render_template('products.html')
    


@login_required
@app.route("/cart", methods=["GET", "POST", "DELETE"])
async def cart():
    user_id = session.get('user_id')

    get_Cart_Data = cursor.execute("SELECT cart.*, products.image, products.stock FROM cart INNER JOIN products on products.id = cart.product_id where user_id = ?", (user_id, )).fetchall()


    if request.method == "POST":
        async def get_data():
            
            datajson = request.get_json()

            return datajson
        
        data = await get_data()

        productid = data.get("productId")

        productquantity = data.get("productQuantity")

        async def cart_data():
            get_Cart_Data_Current = cursor.execute("SELECT * FROM cart where user_id = ?", (user_id, )).fetchall()
            return get_Cart_Data_Current
        

        get_Cart_Data_Current = await cart_data()

        async def stock_update():
            for i in get_Cart_Data_Current:
                if i[1] == user_id and i[3] == int(productid):
                    cursor.execute("UPDATE cart SET product_quantity = ? where user_id = ? and product_id = ? and id = ?", (productquantity, user_id, int(productid), i[0]))
                    conn.commit()

        async def chain(*functions):
            return [await f for f in functions]
        
        await chain(get_data(), cart_data(), stock_update())


    elif request.method == "DELETE":
        cursor.execute("DELETE FROM cart where user_id = ?", (user_id,))
        conn.commit()
        return render_template('cart.html')
   

    return render_template('cart.html', cart = get_Cart_Data)

@login_required
@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    
    user_id = session.get('user_id')
    cursor = conn.cursor()
    get_Cart_Short_Data = cursor.execute("SELECT product_name, ROUND((product_quantity*product_price), 2) FROM cart where user_id = ?", (user_id, )).fetchall()

    get_Cart_Data = cursor.execute("SELECT * FROM cart where user_id = ?", (user_id, )).fetchall()

    get_Cart_Data_Count = cursor.execute("SELECT COUNT(*) FROM cart where user_id = ?", (user_id,)).fetchall()

    get_Cart_Total = cursor.execute("SELECT ROUND((SUM(product_quantity*product_price)), 2) FROM cart where user_id = ?", (user_id,)).fetchall()

    get_orderid = cursor.execute("SELECT order_id FROM ORDERS").fetchall()

    print(get_Cart_Data)

    the_Total = get_Cart_Total[0][0]

    if request.method == "POST":

        data = request.get_json()

        firstName = data.get("firstName")
        lastName = data.get("lastName")
        email = data.get("email")
        address = data.get("address")
        country = data.get("country")
        voivodeship = data.get("voivodeship")

        def generate_orderid():
            numbers = string.digits
            order_number = ''.join(random.choice(numbers) for i in range(10))

            order_id = '#'+ order_number

            return order_id
        
        order_id = generate_orderid()

        if order_id in get_orderid:
            new_orderid = generate_orderid()
        else:
            new_orderid = order_id
        
        for i in get_Cart_Data:
            cursor.execute("INSERT INTO orders (user_id, order_id, product_id, cart_quantity, cart_price, total, firstname, lastname, email, address, country, voivodeship) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (user_id, new_orderid, i[3], i[5], i[6], the_Total, firstName, lastName, email, address, country, voivodeship))
            conn.commit()

        cursor.execute("DELETE FROM cart where user_id = ?", (user_id,))
        conn.commit()
    
    return render_template('checkout.html', cart = get_Cart_Short_Data, cartcount = get_Cart_Data_Count, total = the_Total)
    
@login_required
@app.route("/thankyou", methods=["GET", "POST"])
def thankyou():

    return render_template('thankyou.html')