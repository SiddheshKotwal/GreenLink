from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
from helpers import login_required
from cs50 import SQL
import pandas as pd
import re
import csv
import sqlite3
import asyncio
import aiohttp

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = 'your_secret_key'

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

        # Check if the form has been submitted
        form_submitted = session.get('form_submitted', False)

        if form_submitted:
            emissions = session.get('emissions', {})

            co2_string = str('CO2: ' + str(emissions.get('CO2', 0)) + ' kg/yr')
            ch4_string = str('CH4: ' + str(emissions.get('CH4', 0)) + ' kg/yr')
            n2o_string = str('N2O: ' + str(emissions.get('N2O', 0)) + ' kg/yr')

            # Clear the session variable to prevent repeated display
            session.pop('form_submitted', None)

            return render_template('index.html', js_file=url_for("static", filename="js/script.js"),
                                your_emissions='Your yearly Emissions are:', co2_string=co2_string,
                                ch4_string=ch4_string, n2o_string=n2o_string)
        else:
            return render_template('index.html', js_file=url_for("static", filename="js/script.js"))

if __name__ == '__main__':
    app.run()

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


@app.route("/carbonFootprint", methods=["GET", "POST"])
@login_required
def carbonFootprint():

    if request.method == 'POST':

        age  = energy = water = waste = distance = airDistance = chicken = rice = beans = clothes = 0
        people = fuelEff = 1
        counter = 0        
        fuelType = dict()
        flights = dict()
        electronics = dict()
        EmissionFactors = {
            'waterCO2' : float(0.3),
            'wasteCO2' : float(0.5),
            'wasteCH4' : float(0.7),
            'wasteN2O' : float(0.01),
            'clothesCO2' : float(40),
            'clothesCH4' : float(0.6),
            'clothesN2O' : float(0.14),
            'chickenCO2' : float(6),
            'chickenCH4' : float(0.004),
            'chickenN2O' : float(0.002),
            'riceCO2' : float(4),
            'riceCH4' : float(0.1),
            'riceN2O' : float(0.003),
            'beansCO2' : float(0.8),
            'beansCH4' : float(0.025),
            'beansN2O' : float(0.0006)
        }
        
        try:
            if request.form.get('people'):
                counter = counter + 1
                people = int(request.form.get('people'))
                
            if request.form.get('age'):
                counter = counter + 1
                age = int(request.form.get('age'))

            if request.form.get('energy'):
                counter = counter + 1
                energy = float(request.form.get('energy'))
            
            if request.form.get('water'):
                counter = counter + 1
                water = float(request.form.get('water'))
            
            if request.form.get('waste'):
                counter = counter + 1
                waste = float(request.form.get('waste'))
            
            if request.form.get('fuel-mpg'):
                counter = counter + 1
                fuelEff = float(request.form.get('fuel-mpg'))
            
            if request.form.get('travel'):
                counter = counter + 1
                distance = float(request.form.get('travel'))
            
            if request.form.get('air_travel'):
                counter = counter + 1
                airDistance = float(request.form.get('air_travel'))
            
            if request.form.get('chicken'):
                counter = counter + 1
                chicken = float(request.form.get('chicken'))
            
            if request.form.get('rice'):
                counter = counter + 1
                rice = float(request.form.get('rice'))
            
            if request.form.get('beans'):
                counter = counter + 1
                beans = float(request.form.get('beans'))
            
            if request.form.get('clothes'):
                counter = counter + 1
                clothes = float(request.form.get('clothes'))

            if 'gasoline' in request.form:
                counter = counter + 1
                fuelType.update({'gasoline' : float(8.78)})

            if 'diesel' in request.form:
                counter = counter + 1
                fuelType.update({'diesel' : float(10.14)})

            if 'domestic' in request.form:
                counter = counter + 1
                flights.update({'domestic' : float(0.1)})

            if 'international' in request.form:
                counter = counter + 1
                flights.update({'international' : float(0.15)})

            if 'smartphone' in request.form:
                counter = counter + 1
                electronics.update({'smartphone' : float(100)})

            if 'laptop' in request.form:
                counter = counter + 1
                electronics.update({'laptop' : float(200)})

            if 'television' in request.form:
                counter = counter + 1
                electronics.update({'television' : float(300)})

            if 'refrigerator' in request.form:
                counter = counter + 1
                electronics.update({'refrigerator' : float(350)})

            if 'washing_machine' in request.form:
                counter = counter + 1
                electronics.update({'washing_machine' : float(180)})

            if 'air_conditioner' in request.form:
                counter = counter + 1
                electronics.update({'air_conditioner' : float(470)})

            if 'game_console' in request.form:
                counter = counter + 1
                electronics.update({'game_console' : float(70)})

            if request.form.get('country'):
                counter = counter + 1
                country = isinstance(request.form.get('country'), str)
                if country == True:
                    country = request.form.get('country')
                else:
                    country = 'United States'
            else:
                country = 'United States'
            
        except ValueError as e:
            print('ERROR!: Invalid input', e)
            return render_template("carbonFootprint.html", js_file=url_for("static", filename="js/script.js"), error="Invalid input!")
 
        def houseCarbon(energy, country, waste, water, EmissionFactors, people):
            energyEmission = dict()
            async def execute_query_async(loop, query, params=None):
                def execute_sync():
                    with sqlite3.connect('greenlink.db') as connection:
                        cursor = connection.cursor()
                        cursor.execute(query, params)
                        return cursor.fetchall()

                return await loop.run_in_executor(None, execute_sync)

            async def main():

                loop = asyncio.get_event_loop()

                queries = [
                    ("SELECT kgCO2_per_kWh FROM energy WHERE country LIKE ?;", ('%' + country + '%',)),
                    ("SELECT kgCH4_per_kWh FROM energy WHERE country LIKE ?;", ('%' + country + '%',)),
                    ("SELECT kgN2O_per_kWh FROM energy WHERE country LIKE ?;", ('%' + country + '%',))
                ]

                results = await asyncio.gather(
                    *[execute_query_async(loop, query, params) for query, params in queries]
                )

                # Fetch the emission factors from the first columns of each result
                emissionFactorCO2 = results[0][0][0]  # kgCO2_per_kWh
                emissionFactorCH4 = results[1][0][0]  # kgCH4_per_kWh
                emissionFactorN2O = results[2][0][0]  # kgN2O_per_kWh

                energyEmission.update({'CO2' : float(energy * emissionFactorCO2 * 1000)})
                energyEmission.update({'CH4' : float(energy * emissionFactorCH4 * 1000)})
                energyEmission.update({'N2O' : float(energy * emissionFactorN2O * 1000)})

            asyncio.run(main())

            waterEmissionsCO2 = EmissionFactors['waterCO2'] * (water * 12)

            wasteEmissionCO2 = (waste * 12) * EmissionFactors['wasteCO2']
            wasteEmissionCH4 = (waste * 12) * EmissionFactors['wasteCH4']
            wasteEmissionN2O = (waste * 12) * EmissionFactors['wasteN2O']

            houseEmissions = {
                'CO2' : ((energyEmission['CO2'] + waterEmissionsCO2 + wasteEmissionCO2) / people),
                'CH4' : ((energyEmission['CH4'] + wasteEmissionCH4) / people),
                'N2O' : ((energyEmission['N2O'] + wasteEmissionN2O) / people)
            }

            return houseEmissions

        def transportCarbon(fuelType, distance, fuelEff):

            fuel_list = list(fuelType.keys())
            if (len(fuelType) == 0):
                fuelMultiple = float(8.78)
            elif (len(fuelType) == 2):
                fuelMultiple = fuelType['diesel']
            else:
                fuelMultiple = fuelType[fuel_list[0]]
                
            fuelCons = distance / fuelEff
            travelEmission = fuelCons * fuelMultiple
            travelEmissions = {
                'CO2' : travelEmission,
                'CH4' : 0,
                'N2O' : 0
            }

            return travelEmissions

        def airCarbon(flights, airDistance):

            flight_list = list(flights.keys())
            if (len(flights) == 0):
                flightMultiple = float(0.1)
            elif (len(flights) == 2):
                flightMultiple = flights['international']
            else:
                flightMultiple = flights[flight_list[0]]

            airTravelEmission = airDistance * flightMultiple
            airTravelEmissions = {
                'CO2' : float(airTravelEmission),
                'CH4' : float(0),
                'N2O' : float(0)
            }

            return airTravelEmissions

        def otherCarbon(electronics, EmissionFactors, clothes, chicken, rice, beans):
            total_electronics = 0
            for e in electronics:
                total_electronics = total_electronics + electronics[e]

            clothesEmissionCO2 = clothes * EmissionFactors['clothesCO2']
            clothesEmissionCH4 = clothes * EmissionFactors['clothesCH4']
            clothesEmissionN2O = clothes * EmissionFactors['clothesN2O']
            chickenEmissionsCO2 = (chicken * 12) * EmissionFactors['chickenCO2']
            chickenEmissionsCH4 = (chicken * 12) * EmissionFactors['chickenCH4']
            chickenEmissionsN2O = (chicken * 12) * EmissionFactors['chickenN2O']
            riceEmissionsCO2 = (rice * 12) * EmissionFactors['riceCO2']
            riceEmissionsCH4 = (rice * 12) * EmissionFactors['riceCH4']
            riceEmissionsN2O = (rice * 12) * EmissionFactors['riceN2O']
            beansEmissionsCO2 = (beans * 12) * EmissionFactors['beansCO2']
            beansEmissionsCH4 = (beans * 12) * EmissionFactors['beansCH4']
            beansEmissionsN2O = (beans * 12) * EmissionFactors['beansN2O']

            otherEmissions = {
                'CO2' : float(total_electronics + clothesEmissionCO2 + chickenEmissionsCO2 + riceEmissionsCO2 + beansEmissionsCO2),
                'CH4' : float(clothesEmissionCH4 + chickenEmissionsCH4 + riceEmissionsCH4 + beansEmissionsCH4),
                'N2O' : float(clothesEmissionN2O + chickenEmissionsN2O + riceEmissionsN2O + beansEmissionsN2O)
            }
            
            return otherEmissions

        house_ = transport_ = airTransport_ = other_ = dict()
        
        house_ = houseCarbon(energy, country, waste, water, EmissionFactors, people)
        transport_ = transportCarbon(fuelType, distance, fuelEff)
        airTransport_ = airCarbon(flights, airDistance)
        other_ = otherCarbon(electronics, EmissionFactors, clothes, chicken, rice, beans)
        
        emissions = {
            'CO2': round(float(house_['CO2'] + transport_['CO2'] + airTransport_['CO2'] + other_['CO2']), 1),
            'CH4': round(float(house_['CH4'] + transport_['CH4'] + airTransport_['CH4'] + other_['CH4']), 1),
            'N2O': round(float(house_['N2O'] + transport_['N2O'] + airTransport_['N2O'] + other_['N2O']), 1)
        }

        if (counter < 10):
            return render_template("carbonFootprint.html", js_file=url_for("static", filename="js/script.js"), error="Give atleast 10 inputs for better calculation of your carbon Footprint")
        else:
            electronics_string = ", ".join(electronics.keys())
            fuel_string = ", ".join(fuelType.keys())
            flights_string = ", ".join(flights.keys())
            formatted_pairs = [f"{key}: {value}" for key, value in emissions.items()]
            emissions_string = ", ".join(formatted_pairs)

            food_dict = {
                'chicken' : chicken,
                'rice' : rice,
                'beans' : beans
            }
            formattedPairs = [f"{key}: {value}" for key, value in food_dict.items()]
            food_string = ", ".join(formattedPairs)

            db.execute('INSERT INTO user_details(user_details_id, no_of_people, age, country, "energy_consumption(MWh/yr)", "water_consumption(L/mo)", "waste_produced(kg/mo)", "fuel_efficiency(mpg)", "distance_travelled_on_land(miles/yr)", "distance_travelled_by_plane(miles/yr)", fuel_used_for_vehicle, flight_type, "food_consumed(kg/mo)", "clothes_used(kg/yr)", electronics_products, "greenhouse_gas_emissions(kg/yr)") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                        session["user_id"], people, age, country, energy, water, waste, fuelEff, distance, airDistance, fuel_string, flights_string, food_string, clothes, electronics_string, emissions_string)

            # Store emissions in session
            session['emissions'] = emissions

            # Set session variable to indicate form submission
            session['form_submitted'] = True

            return redirect(url_for('index'))

    else:

        # Use only to update the products database
        # f = open('energy.csv')
        # file = csv.DictReader(f)
        # for d in file:
        #     db.execute('INSERT INTO energy(country, kgCO2_per_kWh, kgCH4_per_kWh, kgN2O_per_kWh) VALUES (?, ?, ?, ?);', d['country'], d['kgCO2/kWh'], d['kgCH4/kWh'], d['kgN2O/kWh'])

        return render_template('carbonFootprint.html')
    
@app.route('/calculate_emissions', methods=['POST'])
@login_required
def calculate_emissions():
    data = request.json  # Get the JSON data from the frontend

    age = energy = water = waste = distance = airDistance = chicken = rice = beans = clothes = 0
    people = fuelEff = 1
    fuelType = dict()
    flights = dict()
    electronics = dict()
    EmissionFactors = {
        'waterCO2' : float(0.3),
        'wasteCO2' : float(0.5),
        'wasteCH4' : float(0.7),
        'wasteN2O' : float(0.01),
        'clothesCO2' : float(40),
        'clothesCH4' : float(0.6),
        'clothesN2O' : float(0.14),
        'chickenCO2' : float(6),
        'chickenCH4' : float(0.004),
        'chickenN2O' : float(0.002),
        'riceCO2' : float(4),
        'riceCH4' : float(0.1),
        'riceN2O' : float(0.003),
        'beansCO2' : float(0.8),
        'beansCH4' : float(0.025),
        'beansN2O' : float(0.0006)
    }
    
    try:
        if data['people']:
            people = int(data['people'])
            
        if data['age']:
            age = int(data['age'])

        if data['energy']:
            energy = float(data['energy'])
        
        if data['water']:
            water = float(data['water'])
        
        if data['waste']:
            waste = float(data['waste'])
        
        if data['fuel-mpg']:
            fuelEff = float(data['fuel-mpg'])
        
        if data['travel']:
            distance = float(data['travel'])
        
        if data['air_travel']:
            airDistance = float(data['air_travel'])
        
        if data['chicken']:
            chicken = float(data['chicken'])
        
        if data['rice']:
            rice = float(data['rice'])
        
        if data['beans']:
            beans = float(data['beans'])
        
        if data['clothes']:
            clothes = float(data['clothes'])

        if data['gasoline'] == True:
            fuelType.update({'gasoline' : float(8.78)})

        if data['diesel'] == True:
            fuelType.update({'diesel' : float(10.14)})

        if data['domestic'] == True:
            flights.update({'domestic' : float(0.1)})

        if data['international'] == True:
            flights.update({'international' : float(0.15)})

        if data['smartphone'] == True:
            electronics.update({'smartphone' : float(100)})

        if data['laptop'] == True:
            electronics.update({'laptop' : float(200)})

        if data['television'] == True:
            electronics.update({'television' : float(300)})

        if data['refrigerator'] == True:
            electronics.update({'refrigerator' : float(350)})

        if data['washing_machine'] == True:
            electronics.update({'washing_machine' : float(180)})

        if data['air_conditioner'] == True:
            electronics.update({'air_conditioner' : float(470)})

        if data['game_console'] == True:
            electronics.update({'game_console' : float(70)})

        if data['country']:
            if (isinstance(data['country'], str)) == True:
                country = data['country']
            else:
                country = 'United States'
        else:
            country = 'United States'
        
    except ValueError as e:
        print('ERROR!: Invalid input', e)
        emissions = {
            'CO2': 0,
            'CH4': 0,
            'N2O': 0
        }
        
        return jsonify(emissions) 

    def houseCarbon(energy, country, waste, water, EmissionFactors, people):
        energyEmission = dict()
        async def execute_query_async(loop, query, params=None):
            def execute_sync():
                with sqlite3.connect('greenlink.db') as connection:
                    cursor = connection.cursor()
                    cursor.execute(query, params)
                    return cursor.fetchall()

            return await loop.run_in_executor(None, execute_sync)

        async def main():

            loop = asyncio.get_event_loop()

            queries = [
                ("SELECT kgCO2_per_kWh FROM energy WHERE country LIKE ?;", ('%' + country + '%',)),
                ("SELECT kgCH4_per_kWh FROM energy WHERE country LIKE ?;", ('%' + country + '%',)),
                ("SELECT kgN2O_per_kWh FROM energy WHERE country LIKE ?;", ('%' + country + '%',))
            ]

            results = await asyncio.gather(
                *[execute_query_async(loop, query, params) for query, params in queries]
            )

            # Fetch the emission factors from the first columns of each result
            emissionFactorCO2 = results[0][0][0]  # kgCO2_per_kWh
            emissionFactorCH4 = results[1][0][0]  # kgCH4_per_kWh
            emissionFactorN2O = results[2][0][0]  # kgN2O_per_kWh

            energyEmission.update({'CO2' : float(energy * emissionFactorCO2 * 1000)})
            energyEmission.update({'CH4' : float(energy * emissionFactorCH4 * 1000)})
            energyEmission.update({'N2O' : float(energy * emissionFactorN2O * 1000)})

        asyncio.run(main())

        waterEmissionsCO2 = EmissionFactors['waterCO2'] * (water * 12)

        wasteEmissionCO2 = (waste * 12) * EmissionFactors['wasteCO2']
        wasteEmissionCH4 = (waste * 12) * EmissionFactors['wasteCH4']
        wasteEmissionN2O = (waste * 12) * EmissionFactors['wasteN2O']

        houseEmissions = {
            'CO2' : ((energyEmission['CO2'] + waterEmissionsCO2 + wasteEmissionCO2) / people),
            'CH4' : ((energyEmission['CH4'] + wasteEmissionCH4) / people),
            'N2O' : ((energyEmission['N2O'] + wasteEmissionN2O) / people)
        }

        return houseEmissions

    def transportCarbon(fuelType, distance, fuelEff):

        fuel_list = list(fuelType.keys())
        if (len(fuelType) == 0):
            fuelMultiple = float(8.78)
        elif len(fuelType) == '2':
            fuelMultiple = fuelType['diesel']
        else:
            fuelMultiple = fuelType[fuel_list[0]]
            
        fuelCons = distance / fuelEff
        travelEmission = fuelCons * fuelMultiple
        travelEmissions = {
            'CO2' : travelEmission,
            'CH4' : 0,
            'N2O' : 0
        }

        return travelEmissions

    def airCarbon(flights, airDistance):

        flight_list = list(flights.keys())
        if (len(flights) == 0):
            flightMultiple = float(0.1)
        elif len(flights) == '2':
            flightMultiple = flights['international']
        else:
            flightMultiple = flights[flight_list[0]]

        airTravelEmission = airDistance * flightMultiple
        airTravelEmissions = {
            'CO2' : airTravelEmission,
            'CH4' : 0,
            'N2O' : 0
        }

        return airTravelEmissions

    def otherCarbon(electronics, EmissionFactors, clothes, chicken, rice, beans):
        total_electronics = 0
        for e in electronics:
            total_electronics = total_electronics + electronics[e]

        clothesEmissionCO2 = clothes * EmissionFactors['clothesCO2']
        clothesEmissionCH4 = clothes * EmissionFactors['clothesCH4']
        clothesEmissionN2O = clothes * EmissionFactors['clothesN2O']
        chickenEmissionsCO2 = (chicken * 12) * EmissionFactors['chickenCO2']
        chickenEmissionsCH4 = (chicken * 12) * EmissionFactors['chickenCH4']
        chickenEmissionsN2O = (chicken * 12) * EmissionFactors['chickenN2O']
        riceEmissionsCO2 = (rice * 12) * EmissionFactors['riceCO2']
        riceEmissionsCH4 = (rice * 12) * EmissionFactors['riceCH4']
        riceEmissionsN2O = (rice * 12) * EmissionFactors['riceN2O']
        beansEmissionsCO2 = (beans * 12) * EmissionFactors['beansCO2']
        beansEmissionsCH4 = (beans * 12) * EmissionFactors['beansCH4']
        beansEmissionsN2O = (beans * 12) * EmissionFactors['beansN2O']

        otherEmissions = {
            'CO2' : (total_electronics + clothesEmissionCO2 + chickenEmissionsCO2 + riceEmissionsCO2 + beansEmissionsCO2),
            'CH4' : (clothesEmissionCH4 + chickenEmissionsCH4 + riceEmissionsCH4 + beansEmissionsCH4),
            'N2O' : (clothesEmissionN2O + chickenEmissionsN2O + riceEmissionsN2O + beansEmissionsN2O)
        }
        
        return otherEmissions
    
    house_ = transport_ = airTransport_ = other_ = dict()
    
    house_ = houseCarbon(energy, country, waste, water, EmissionFactors, people)
    transport_ = transportCarbon(fuelType, distance, fuelEff)
    airTransport_ = airCarbon(flights, airDistance)
    other_ = otherCarbon(electronics, EmissionFactors, clothes, chicken, rice, beans)
    
    emissions = {
        'CO2': float(house_['CO2'] + transport_['CO2'] + airTransport_['CO2'] + other_['CO2']),
        'CH4': float(house_['CH4'] + transport_['CH4'] + airTransport_['CH4'] + other_['CH4']),
        'N2O': float(house_['N2O'] + transport_['N2O'] + airTransport_['N2O'] + other_['N2O'])
    }
    
    return jsonify(emissions)