from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
from helpers import login_required
from cs50 import SQL
import pandas as pd
import re
import csv

app = Flask(__name__, static_url_path='/static', static_folder='static')

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///greenlink.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":

        if not request.form.get("Name"):
            return render_template("index.html", js_file=url_for("static", filename="js/script.js"), error="Message Not Sent!")

        if not request.form.get("Email"):
            return render_template("index.html", js_file=url_for("static", filename="js/script.js"), error="Message Not Sent!")

        if not request.form.get("Message"):
            return render_template("index.html", js_file=url_for("static", filename="js/script.js"), error="Message Not Sent!")

        if not request.form.get("Subject"):
            return render_template("index.html", js_file=url_for("static", filename="js/script.js"), error="Message Not Sent!")

        def is_valid_email(email):
            # Regular expression pattern for email validation
            pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
            return re.match(pattern, request.form.get("Email")) is not None
        
        if is_valid_email(request.form.get("Email")) == 0:
            return render_template("index.html", js_file=url_for("static", filename="js/script.js"), error="Message Not Sent!")

        db.execute("INSERT INTO messages (user_id, username, user_email, subject, message) VALUES (?, ?, ?, ?, ?);", session["user_id"], request.form.get("Name"), request.form.get("Email"), request.form.get("Subject"), request.form.get("Message"))

        return render_template("index.html", js_file=url_for("static", filename="js/script.js"), error="Message Sent :)")

    else:
        return render_template('index.html')


@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        if not request.form.get("email"):
            return render_template("login.html", js_file=url_for("static", filename="js/script.js"), error="Invalid Email!")

        if not request.form.get("password"):
            return render_template("login.html", js_file=url_for("static", filename="js/script.js"), error="Invalid Password!")
        
        data = db.execute("SELECT * FROM users WHERE email=?;", request.form.get("email"))

        try:
            email_count = data[0]["email"]
        except IndexError:
            return render_template("login.html", error="User not Found, Not Registered Yet!", js_file=url_for("static", filename="js/script.js"))

        password = data[0]["hash"]
        if not check_password_hash(password, request.form.get("password")):
            return render_template("login.html", js_file=url_for("static", filename="js/script.js"), error="Invalid Password!")

        session["user_id"] = data[0]["id"]

        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        if not request.form.get("email"):
            return render_template("register.html", js_file=url_for("static", filename="js/script.js"), error="Invalid Email!")

        if not request.form.get("password"):
            return render_template("register.html", js_file=url_for("static", filename="js/script.js"), error="Invalid Password!")
        
        if not request.form.get("confirm"):
            return render_template("register.html", js_file=url_for("static", filename="js/script.js"), error="Invalid confirmation")
        
        if request.form.get("password") != request.form.get("confirm"):
            return render_template("register.html", js_file=url_for("static", filename="js/script.js"), error="password and confirmation don't match!")

        def is_valid_email(email):
            # Regular expression pattern for email validation
            pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
            return re.match(pattern, request.form.get("email")) is not None

        if is_valid_email(request.form.get("email")) == 0:
            return render_template("register.html", js_file=url_for("static", filename="js/script.js"), error="Invalid Email!")
        
        
        data = db.execute("SELECT COUNT(email) FROM users WHERE email=?;", request.form.get("email"))
        email_count = data[0]["COUNT(email)"]

        if email_count != 0:
            return render_template("register.html", js_file=url_for("static", filename="js/script.js"), error="Email already Exists!, try another one!")

        hash = generate_password_hash(request.form.get("password"), 'sha256')     
        db.execute("INSERT INTO users (email, hash) VALUES (?, ?);", request.form.get("email"), hash)

        return redirect("/")

    else:
        return render_template("register.html") 
       

@app.route("/products", methods=["GET", "POST"])
@login_required
def products():
    if request.method == "POST":

        products = db.execute('SELECT * FROM products;')
        if not request.form.get("search"):
            return jsonify(render_template('products_data.html', products=products))
        
        products_search = db.execute("SELECT * FROM products WHERE product_name LIKE ? OR company_name LIKE ?;", ('%' + request.form.get('search') + '%'), ('%' + request.form.get('search') + '%'))
        
        if (len(products_search) == 0):
            no_products = 'Products not Found!'
            return jsonify(render_template('products_data.html', products=products_search, no_products=no_products))
                
        return jsonify(render_template('products_data.html', products=products_search))

    else:

        # Use only to update the products database
        # f = open('products.csv')
        # file = csv.DictReader(f)
        # for d in file:
        #     db.execute('INSERT INTO products(image, company_name, product_name, rating, price, link) VALUES (?, ?, ?, ?, ?, ?);', d['image'], d['company_name'], d['product_name'], d['rating'], d['price'], d['link'])

        products = db.execute('SELECT * FROM products;')
        return render_template('products.html', products=products)


@app.route("/sort_products", methods=["POST"])
@login_required
def sort_products():
    sort_by = request.form.get("sort_by")
    products = []

    if sort_by == "product_name":
        # Sort products by product_name
        products = db.execute("SELECT * FROM products ORDER BY product_name;")
    elif sort_by == "company_name":
        # Sort products by company_name
        products = db.execute("SELECT * FROM products ORDER BY company_name;")

    # Render the template with the sorted products
    return render_template('products_data.html', products=products)


@app.route("/services", methods=["GET", "POST"])
@login_required
def services():
    if request.method == "POST":

        services = db.execute('SELECT * FROM services;')
        if not request.form.get("search"):
            return jsonify(render_template('services_data.html', services=services))
        
        services_search = db.execute("SELECT * FROM services WHERE service LIKE ? OR company_name LIKE ?;", ('%' + request.form.get('search') + '%'), ('%' + request.form.get('search') + '%'))
        
        if (len(services_search) == 0):
            no_services = 'Services not Found!'
            return jsonify(render_template('services_data.html', services=services_search, no_services=no_services))
                
        return jsonify(render_template('services_data.html', services=services_search))

    else:

        # Use only to update the services database
        # df = pd.read_csv('services.csv', delimiter=';')
        # file = df.to_dict(orient='records')
        # for s in file:
        #     db.execute('INSERT INTO services(image, company_name, service, service_desc, contact_link, website_link) VALUES (?, ?, ?, ?, ?, ?);', s['image'], s['company_name'], s['service'], s['service_desc'], s['contact_link'], s['website_link'])

        services = db.execute('SELECT * FROM services;')
        return render_template('services.html', services=services)


@app.route("/sort_services", methods=["POST"])
@login_required
def sort_services():
    sort_by = request.form.get("sort_by")
    services = []

    if sort_by == "service":
        # Sort products by product_name
        services = db.execute("SELECT * FROM services ORDER BY service;")
    elif sort_by == "company_name":
        # Sort products by company_name
        services = db.execute("SELECT * FROM services ORDER BY company_name;")

    # Render the template with the sorted products
    return render_template('services_data.html', services=services)

