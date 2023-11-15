# app.py
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__, static_url_path='/static')

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:01091998@localhost/hey_taxii'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'asap'  # Change this to a secure secret key
db = SQLAlchemy(app)

class Users(db.Model):
    __tablename__ = 'USERS'
    USER_ID = db.Column(db.String(50), primary_key=True)
    USERNAME = db.Column(db.String(50), nullable=False)
    EMAIL = db.Column(db.String(100), nullable=False)
    PASSWD = db.Column(db.String(6), nullable=False)
    PHONE_NUMBER = db.Column(db.Integer, nullable=False)
    ROLE = db.Column(db.String(20), nullable=False)

class Customer(db.Model):
    __tablename__ = 'CUSTOMER'
    CUSTOMER_ID = db.Column(db.String(50), primary_key=True)
    USER_ID = db.Column(db.String(50), db.ForeignKey('USERS.USER_ID'), nullable=False)
    PAYMENT_METHOD = db.Column(db.String(50), nullable=False)
    
    # Define the relationship with the Payment table
    payments = db.relationship('Payment', backref='customer', cascade='all, delete-orphan')


class Driver(db.Model):
    __tablename__ = 'DRIVER'
    DRIVER_ID = db.Column(db.String(50), primary_key=True)
    USER_ID = db.Column(db.String(50), db.ForeignKey('USERS.USER_ID'), nullable=False)
    LICENSE_NUMBER = db.Column(db.String(50), nullable=False)
    DRIVER_RATING = db.Column(db.Integer)

    # Define the relationship with the Vehicle table
    vehicles = db.relationship('Vehicle', backref='driver', cascade='all, delete-orphan')


class Vehicle(db.Model):
    __tablename__ = 'VEHICLE'
    VEHICLE_NUMBER = db.Column(db.String(25), primary_key=True)
    VEHICLE_TYPE = db.Column(db.String(20), nullable=False)
    NUMBER_OF_MEMBERS = db.Column(db.Integer, nullable=False)
    DRIVER_ID = db.Column(db.String(50), db.ForeignKey('DRIVER.DRIVER_ID'))

class Payment(db.Model):
    __tablename__ = 'PAYMENT'
    PAYMENT_ID = db.Column(db.String(50), primary_key=True)
    PAYMENT_METHOD = db.Column(db.String(50), nullable=False)
    FARE = db.Column(db.Integer, nullable=False)
    DATE_OF_RIDE = db.Column(db.Date, nullable=False)
    TIME_OF_RIDE = db.Column(db.Time, nullable=False)
    CUSTOMER_ID = db.Column(db.String(50), db.ForeignKey('CUSTOMER.CUSTOMER_ID'))

class Ride(db.Model):
    __tablename__ = 'RIDE'
    RIDE_ID = db.Column(db.String(50), primary_key=True)
    START_LOCATION = db.Column(db.String(255), nullable=False)
    END_LOCATION = db.Column(db.String(255), nullable=False)
    FARE = db.Column(db.Integer, nullable=False)
    DATE_OF_RIDE = db.Column(db.Date, nullable=False)
    TIME_OF_RIDE = db.Column(db.String(100), nullable=False)
    CUSTOMER_ID = db.Column(db.String(50), db.ForeignKey('CUSTOMER.CUSTOMER_ID'))
    DRIVER_ID = db.Column(db.String(50), db.ForeignKey('DRIVER.DRIVER_ID'))

class Admin(db.Model):
    __tablename__ = 'Adminn'
    ADMIN_ID = db.Column(db.String(10), primary_key=True)
    PASSWD = db.Column(db.String(4), nullable=False)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = Users(
            USER_ID=request.form['user_id'],
            USERNAME=request.form['username'],
            EMAIL=request.form['email'],
            PASSWD=request.form['passwd'],
            PHONE_NUMBER=request.form['phone_number'],
            ROLE=request.form['role']
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['passwd']
        user = Users.query.filter_by(USER_ID=user_id, PASSWD=password).first()

        if user:
            session['user_id'] = user_id
            if user.ROLE == 'customer':
                return redirect(url_for('customer_operations'))
            elif user.ROLE == 'driver':
                return redirect(url_for('driver_operations'))
            elif user.ROLE == 'admin':
                return redirect(url_for('admin_operations'))

    return render_template('login.html')



@app.route('/driver_operations', methods=['GET', 'POST'])
def driver_operations():
    if request.method == 'POST':
        selected_operation = request.form.get('operation')
        if selected_operation == 'populate_driver':
            return redirect(url_for('populate_driver'))
        elif selected_operation == 'populate_vehicle':
            return redirect(url_for('populate_vehicle'))
        elif selected_operation == 'update_driver':
            return redirect(url_for('update_driver'))
        elif selected_operation == 'view_details':
            return redirect(url_for('view_ride_payment_details'))
    return render_template('driver_operations.html')
@app.route('/populate_driver', methods=['GET', 'POST'])
def populate_driver():
    if request.method == 'POST':
        driver_id = request.form['driver_id']
        license_number = request.form['license_number']
        driver = Driver(DRIVER_ID=driver_id, LICENSE_NUMBER=license_number, USER_ID=session['user_id'])
        db.session.add(driver)
        db.session.commit()
        return redirect(url_for('driver_operations'))
    return render_template('populate_driver.html')

@app.route('/populate_vehicle', methods=['GET', 'POST'])
def populate_vehicle():
    if request.method == 'POST':
        vehicle_number = request.form['vehicle_number']
        vehicle_type = request.form['vehicle_type']
        number_of_members = request.form['number_of_members']
        driver_id = request.form['driver_id']
        vehicle = Vehicle(VEHICLE_NUMBER=vehicle_number, VEHICLE_TYPE=vehicle_type,
                          NUMBER_OF_MEMBERS=number_of_members, DRIVER_ID=driver_id)
        db.session.add(vehicle)
        db.session.commit()
        return redirect(url_for('driver_operations'))
    return render_template('populate_vehicle.html')

@app.route('/update_driver', methods=['GET', 'POST'])
def update_driver():
    if request.method == 'POST':
        driver_id = request.form['driver_id']
        new_license_number = request.form['new_license_number']
        driver = Driver.query.filter_by(DRIVER_ID=driver_id).first()
        if driver:
            driver.LICENSE_NUMBER = new_license_number
            db.session.commit()
        return redirect(url_for('driver_operations'))
    return render_template('update_driver.html')

@app.route('/view_ride_payment_details')
def view_ride_payment_details():
    driver_id = session.get('user_id')
    rides = Ride.query.filter_by(DRIVER_ID=driver_id).all()
    payments = Payment.query.filter_by(CUSTOMER_ID=driver_id).all()
    return render_template('view_ride_payment_details.html', rides=rides, payments=payments)


@app.route('/customer_operations', methods=['GET', 'POST'])
def customer_operations():
    if request.method == 'POST':
        selected_operation = request.form.get('operation')
        if selected_operation == 'populate_customer':
            return redirect(url_for('populate_customer'))
        elif selected_operation == 'populate_ride_payment':
            return redirect(url_for('populate_ride_payment'))
        elif selected_operation == 'update_user':
            return redirect(url_for('register'))
        elif selected_operation == 'view_ride_payment_details':
            return redirect(url_for('view_ride_payment_details'))
    return render_template('customer_operations.html')

@app.route('/populate_customer', methods=['GET', 'POST'])
def populate_customer():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        user_id = session['user_id']
        payment_method = request.form['payment_method']
        customer = Customer(CUSTOMER_ID=customer_id, USER_ID=user_id, PAYMENT_METHOD=payment_method)
        db.session.add(customer)
        db.session.commit()
        return redirect(url_for('customer_operations'))
    return render_template('populate_customer.html')

@app.route('/populate_ride_payment', methods=['GET', 'POST'])
def populate_ride_payment():
    if request.method == 'POST':
        ride_id = request.form['ride_id']
        start_location = request.form['start_location']
        end_location = request.form['end_location']
        fare = request.form['fare']
        date_of_ride = request.form['date_of_ride']
        time_of_ride = request.form['time_of_ride']
        customer_id = session['user_id']
        driver_id = request.form['driver_id']
        
        ride = Ride(RIDE_ID=ride_id, START_LOCATION=start_location, END_LOCATION=end_location,
                    FARE=fare, DATE_OF_RIDE=date_of_ride, TIME_OF_RIDE=time_of_ride,
                    CUSTOMER_ID=customer_id, DRIVER_ID=driver_id)
        
        payment = Payment(PAYMENT_ID=ride_id, PAYMENT_METHOD='YourPaymentMethod', FARE=fare,
                          DATE_OF_RIDE=date_of_ride, TIME_OF_RIDE=time_of_ride, CUSTOMER_ID=customer_id)
        
        db.session.add_all([ride, payment])
        db.session.commit()
        return redirect(url_for('customer_operations'))
    return render_template('populate_ride_payment.html')

@app.route('/explore')
def explore():
    return render_template('explore.html')



@app.route('/admin_operations', methods=['GET', 'POST'])
def admin_operations():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    if request.method == 'POST':
        selected_option = request.form.get('admin_option')
        if selected_option == 'insert_driver_customer':
            return redirect(url_for('insert_driver_customer'))
        elif selected_option == 'delete_driver_customer':
            return redirect(url_for('delete_driver_customer'))
        elif selected_option == 'update_driver_customer':
            return redirect(url_for('update_driver_customer'))
        elif selected_option == 'view_all_tables':
            return redirect(url_for('view_all_tables'))

    return render_template('admin_operations.html')

@app.route('/insert_driver_customer', methods=['GET', 'POST'])
def insert_driver_customer():
    if request.method == 'POST':
        # Retrieve data from the form
        driver_id = request.form['driver_id']
        license_number = request.form['license_number']
        vehicle_number = request.form['vehicle_number']
        vehicle_type = request.form['vehicle_type']
        number_of_members = request.form['number_of_members']
        customer_id = request.form['customer_id']
        payment_method = request.form['payment_method']

        # Perform database operations
        # Insert into DRIVER table
        new_driver = Driver(DRIVER_ID=driver_id, USER_ID=session['user_id'], LICENSE_NUMBER=license_number)
        db.session.add(new_driver)

        # Insert into VEHICLE table
        new_vehicle = Vehicle(VEHICLE_NUMBER=vehicle_number, VEHICLE_TYPE=vehicle_type,
                              NUMBER_OF_MEMBERS=number_of_members, DRIVER_ID=driver_id)
        db.session.add(new_vehicle)

        # Insert into CUSTOMER table
        new_customer = Customer(CUSTOMER_ID=customer_id, USER_ID=session['user_id'], PAYMENT_METHOD=payment_method)
        db.session.add(new_customer)

        # Commit the changes to the database
        db.session.commit()

        return "Insert operation performed successfully."
    
    return render_template('insert_driver_customer.html')

@app.route('/delete_driver_customer', methods=['GET', 'POST'])
def delete_driver_customer():
    if request.method == 'POST':
        # Retrieve data from the form
        driver_id_to_delete = request.form['driver_id']
        customer_id_to_delete = request.form['customer_id']
                # Perform database operations
        # Delete from RIDE table first
        rides_to_delete = Ride.query.filter_by(CUSTOMER_ID=customer_id_to_delete).all()
        for ride in rides_to_delete:
            db.session.delete(ride)

        # Delete from PAYMENT table
        payments_to_delete = Payment.query.filter_by(CUSTOMER_ID=customer_id_to_delete).all()
        for payment in payments_to_delete:
            db.session.delete(payment)

        # Perform database operations
        # Delete from DRIVER table
        driver_to_delete = Driver.query.filter_by(DRIVER_ID=driver_id_to_delete).first()
        if driver_to_delete:
            db.session.delete(driver_to_delete)

        # Delete from CUSTOMER table
        customer_to_delete = Customer.query.filter_by(CUSTOMER_ID=customer_id_to_delete).first()
        if customer_to_delete:
            db.session.delete(customer_to_delete)

        # Commit the changes to the database
        db.session.commit()

        return "Delete operation performed successfully."

    return render_template('delete_driver_customer.html')

@app.route('/update_driver_customer', methods=['GET', 'POST'])
def update_driver_customer():
    if request.method == 'POST':
        # Retrieve data from the form
        driver_id_to_update = request.form['driver_id']
        new_license_number = request.form['new_license_number']
        customer_id_to_update = request.form['customer_id']
        new_payment_method = request.form['new_payment_method']

        # Perform database operations
        # Update DRIVER table
        driver_to_update = Driver.query.filter_by(DRIVER_ID=driver_id_to_update).first()
        if driver_to_update:
            driver_to_update.LICENSE_NUMBER = new_license_number

        # Update CUSTOMER table
        customer_to_update = Customer.query.filter_by(CUSTOMER_ID=customer_id_to_update).first()
        if customer_to_update:
            customer_to_update.PAYMENT_METHOD = new_payment_method

        # Commit the changes to the database
        db.session.commit()

        return "Update operation performed successfully."

    return render_template('update_driver_customer.html')



from sqlalchemy import text


from sqlalchemy import text



@app.route('/view_all_tables', methods=['POST','GET'])
def view_all_tables():
    if request.method == 'POST':
        # Retrieve data from the form
        view_criteria = request.form['view_criteria']
        selected_value = request.form['selected_value']

        # Define the base query
        base_query = """
            SELECT RIDE.RIDE_ID, RIDE.START_LOCATION, RIDE.END_LOCATION, RIDE.FARE, RIDE.DATE_OF_RIDE, RIDE.TIME_OF_RIDE,
                   CUSTOMER.USER_ID AS CUSTOMER_ID, DRIVER.USER_ID AS DRIVER_ID
            FROM RIDE
            INNER JOIN CUSTOMER ON RIDE.CUSTOMER_ID = CUSTOMER.CUSTOMER_ID
            INNER JOIN DRIVER ON RIDE.DRIVER_ID = DRIVER.DRIVER_ID
        """

        # Perform database operations based on view criteria
        if view_criteria == 'start_location':
            query = text(base_query + " WHERE RIDE.START_LOCATION = :value")
        elif view_criteria == 'end_location':
            query = text(base_query + " WHERE RIDE.END_LOCATION = :value")
        elif view_criteria == 'date':
            query = text(base_query + " WHERE RIDE.DATE_OF_RIDE = :value")
        elif view_criteria == 'customer':
            query = text(base_query + " WHERE CUSTOMER.USER_ID = :value")
        elif view_criteria == 'driver':
            query = text(base_query + " WHERE DRIVER.USER_ID = :value")
        else:
            # Handle the default case or do nothing
            pass

        # Execute the query and fetch results
        params = {'value': selected_value}
        result = db.session.execute(query, params).fetchall()

        # Display results (modify this based on your frontend requirements)
        return render_template('view_all_tables_result.html', result=result)

    return render_template('view_all_tables.html')




@app.route('/view_all_tables_result', methods=['GET'])
def view_all_tables_result():
    # This route is used to display the result of the view_all_tables operation
    return render_template('view_all_tables_result.html')

@app.route('/get_driver_count', methods=['GET', 'POST'])
def get_driver_count():

    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    if request.method == 'POST'or 'GET':
        selected_option = request.form.get('admin_option')

        if selected_option == 'join_query':
            return redirect(url_for('join_query'))
        elif selected_option == 'nested_query':
            return redirect(url_for('nested_query'))
        elif selected_option == 'aggregate_query':
            return redirect(url_for('aggregate_query'))


    return render_template('get_driver_count.html')

from sqlalchemy import text

@app.route('/get_max_fare_for_driver', methods=['POST'])
def get_max_fare_for_driver():
    if request.method == 'POST':
        # Retrieve data from the form
        driver_id = request.form['driver_id']

        # Call the stored procedure
        query = text("CALL GetMaxFareForDriver(:driver_id)")
        result = db.session.execute(query, {'driver_id': driver_id}).fetchall()

        # Display results (modify this based on your frontend requirements)
        return render_template('get_max_fare_for_driver_result.html', result=result)

    return render_template('get_max_fare_for_driver.html')



@app.route('/join_query', methods=['GET'])
def join_query():
    # Define the base query using text
    base_query = text("""
        SELECT RIDE.RIDE_ID, RIDE.START_LOCATION, RIDE.END_LOCATION, RIDE.FARE, RIDE.DATE_OF_RIDE, RIDE.TIME_OF_RIDE,
               CUSTOMER.USER_ID AS CUSTOMER_ID, DRIVER.USER_ID AS DRIVER_ID
        FROM RIDE
        INNER JOIN CUSTOMER ON RIDE.CUSTOMER_ID = CUSTOMER.CUSTOMER_ID
        INNER JOIN DRIVER ON RIDE.DRIVER_ID = DRIVER.DRIVER_ID
    """)

    # Execute the query and fetch results
    result = db.session.execute(base_query).fetchall()

    # Display results (modify this based on your frontend requirements)
    return render_template('join_query_result.html', result=result)


from flask import request

# ...

from sqlalchemy import text

from sqlalchemy import text

@app.route('/nested_query', methods=['GET'])
def nested_query():
    # Retrieve data from the query parameters
    vehicle_type = request.args.get('vehicle_type')

    if vehicle_type is not None and vehicle_type.strip() != "":
        # Define the nested query using text()
        nested_query = text(f"""
            SELECT D.driver_id, D.user_id, D.license_number, D.driver_rating,
                   COUNT(R.ride_id) AS numberOfRides
            FROM DRIVER D
            LEFT JOIN RIDE R ON D.driver_id = R.driver_id
            LEFT JOIN VEHICLE V ON D.driver_id = V.driver_id
            WHERE V.vehicle_type = '{vehicle_type}'
            GROUP BY D.driver_id, D.user_id, D.license_number, D.driver_rating
        """)

        # Execute the nested query and fetch results
        result = db.session.execute(nested_query).fetchall()

        # Display results
        return render_template('nested_query_result.html', result=result)

    return render_template('nested_query.html')






from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

@app.route('/aggregate_query', methods=['GET'])
def aggregate_query():
    try:
        # Define the aggregate query
        aggregate_query = """
            SELECT DRIVER_ID, MAX(FARE) AS MaxFare
            FROM RIDE
            GROUP BY DRIVER_ID
        """

        # Explicitly declare the query as text
        full_query = text(aggregate_query)

        # Execute the query and fetch results
        result = db.session.execute(full_query).fetchall()

        # Display results (modify this based on your frontend requirements)
        return render_template('aggregate_query.html', result=result)

    except SQLAlchemyError as e:
        # Print or log the error for debugging
        print(f"SQLAlchemy Error: {e}")
        return "An error occurred during the query execution."




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
