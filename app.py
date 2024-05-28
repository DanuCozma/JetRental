import os
from concurrent.futures import ThreadPoolExecutor  # Import ThreadPoolExecutor for parallel processing
from datetime import datetime
from flask import Flask, render_template, send_from_directory, redirect, request, url_for, flash, session
from werkzeug.utils import secure_filename
from db import db
from db_models import Jets, User, Rentals, Base
from models.DatabaseFacade import DatabaseFacade
from models.RentalStrategy import StandardPricingStrategy, MonthlyPricingStrategy
from models.Reposotory import UserRepository
from models.jet_builder import JetFactory
from models.jet_decorator import *
from models.observer import Subject, AdminObserver, UserObserver

# Import statements

# Initialize the Flask app
app = Flask(__name__)

# Define constants
UPLOAD_FOLDER = 'photos'

# Configure the Flask app
app.config['SECRET_KEY'] = 'do later'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/jetrentaldb'
app.config['UPLOADED_FOLDER'] = UPLOAD_FOLDER

# Initialize the database
db.init_app(app)
db.migrate(app, Base)

# Initialize the DatabaseFacade instance
db_facade = DatabaseFacade()

# Register the admin observer

subject = Subject()
subject.register(AdminObserver())
subject.register(UserObserver())

# Initialize the ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=2)

jet_factory = JetFactory()


@app.route('/')
def main():
    # Fetch all jets using DatabaseFacade
    jets = db_facade.fetch_all_available_jets()
    user_logged_in = 'user_id' in session
    return render_template('home.html', jets=jets, user_logged_in=user_logged_in, title="Jet Rental")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']

        new_user = db_facade.add_user(username, email, password, full_name)

        flash("User registered successfully", "success")
        return redirect(url_for('login'))

    return render_template('register.html', title="")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Use db.session.query() instead of User.query
        login_user = db.session.query(User).filter_by(username=username, password=password).first()

        if login_user is not None:
            login_user.last_login = datetime.now()  # Update last login time
            db.session.commit()

            # Set user_id in session upon successful login
            session['user_id'] = login_user.id_user

            return redirect(url_for('account'))
        else:
            flash("Invalid username or password", "error")
    return render_template("login.html")


@app.route('/delete-user/<int:id_user>', methods=['GET', 'POST'])
def delete_user(id_user):
    if request.method == 'POST':
        # Check if the user is logged in and is an admin
        if 'user_id' not in session:
            flash("You need to log in to perform this action", "error")
            return redirect(url_for('login'))

        # Call the delete_user method from UserRepository
        if UserRepository.delete_user(id_user):
            flash("User deleted successfully", "success")
        else:
            flash("User not found", "error")

        return redirect(url_for('home'))

    # If the request method is not POST, return a method not allowed error
    return "Method not allowed", 405


@app.route('/account')
def account():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = db_facade.fetch_user_by_id(user_id)
    user_logged_in = True
    username = user.username
    notifications = subject.notifications

    if user.is_admin:
        all_users = db_facade.fetch_all_users()
        all_rented_jets = db_facade.fetch_all_rented_jets()
        jets = db_facade.fetch_all_jets()

        return render_template('account.html', rented_jets=all_rented_jets, is_admin=user.is_admin,
                               user_logged_in=user_logged_in,
                               all_users=all_users, username=username, jets=jets, notifications=notifications)
    else:
        return render_template('account.html', is_admin=user.is_admin,
                               user_logged_in=user_logged_in, username=username, notifications=notifications)


@app.route('/rented-jets')
def rented_jets():
    if 'user_id' not in session:
        # Redirect to login if user is not logged in
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = db.session.query(User).get(user_id)
    user_logged_in = True

    if user.is_admin:
        # Fetch all rented jets if user is an admin
        rented_jets = db_facade.fetch_all_rented_jets()
    else:
        # Fetch jets rented by the current user
        rented_jets = db_facade.fetch_user_rented_jets(user_id)

    return render_template('rented_jets.html', rented_jets=rented_jets, user_logged_in=user_logged_in,
                           is_admin=user.is_admin, title="My Rented Jets")


@app.route('/delete-rental/<int:rental_id>', methods=['POST'])
def delete_rental(rental_id):
    if request.method == 'POST':
        # Check if the user is logged in or has admin privileges (if applicable)
        if 'user_id' not in session:
            flash("You need to log in to perform this action", "error")
            return redirect(url_for('login'))

        # Fetch the rental by its ID
        rental = db_facade.fetch_rental_by_id(rental_id)

        # Check if the rental exists
        if not rental:
            flash("Rental not found", "error")
            return redirect(url_for('rented_jets'))

        # Delete the rental from the database
        db_facade.delete_rental(rental_id)

        flash("Rental deleted successfully", "success")
        return redirect(url_for('rented_jets'))
    # If the request method is not POST, return a method not allowed error
    return "Method not allowed", 405


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/jets')
def jet_list():
    user_logged_in = 'user_id' in session
    user_is_admin = False
    if user_logged_in:
        # Fetch user details from session or database, assuming User model has an attribute is_admin
        user_id = session['user_id']
        user = db_facade.fetch_user_by_id(user_id)
        user_is_admin = user.is_admin if user else False

    # Fetch all jets using DatabaseFacade
    jets = db_facade.fetch_all_available_jets()

    return render_template('jet_list.html', jets=jets, user_logged_in=user_logged_in, user_is_admin=user_is_admin, title="Our Jets - Jet Rental")


@app.route('/delete-jet/<int:jet_id>', methods=['POST'])
def delete_jet(jet_id):
    if request.method == 'POST':
        # Check if the user is logged in and is an admin
        if 'user_id' not in session:
            flash("You need to log in to perform this action", "error")
            return redirect(url_for('login'))

        user_id = session['user_id']
        user = db.session.query(User).get(user_id)

        if not user.is_admin:
            flash("You do not have permission to perform this action", "error")
            return redirect(url_for('jet_list'))

        # Delete the jet from the database
        db_facade.delete_jet_by_id(jet_id)

        flash("Jet deleted successfully", "success")
        return redirect(url_for('jet_list'))

    # If the request method is not POST, return a method not allowed error
    return "Method not allowed", 405


@app.route('/add_jet')
def add_jet():
    user_logged_in = 'user_id' in session
    return render_template('add_jet.html', user_logged_in=user_logged_in, title="Add a jet")


@app.route('/jet-details/<int:jet_id>')
def jet_details(jet_id):
    user_logged_in = 'user_id' in session
    jet = db_facade.fetch_jet_by_id(jet_id)
    if jet:
        return render_template('jet_details.html', jet=jet, user_logged_in=user_logged_in)
    else:
        return render_template('404.html'), 404


@app.route('/photos/<path:filename>')
def serve_image(filename):
    return send_from_directory('photos', filename)


@app.route('/submit-new-jet', methods=['POST'])
def submit_new_jet():
    if request.method == 'POST':
        # Extract form data
        name = request.form.get('name')
        model = request.form.get('model')
        year = request.form.get('year')
        color = request.form.get('color')
        engine = request.form.get('engine')
        price = request.form.get('price')

        # Handle the file upload
        if 'image_url' in request.files:
            photo = request.files['image_url']
            if photo.filename != '':
                filename = secure_filename(photo.filename)
                photo_path = os.path.join('photos', filename)
                photo.save(photo_path)
                image_url = f"photos/{filename}"
            else:
                image_url = None
        else:
            image_url = None

        # Create the jet using the factory pattern
        new_jet = jet_factory.create(name, model, year, engine, color, price, image_url)

        # Add the new jet to the database
        db.session.add(new_jet)
        db.session.commit()

        subject.notify_observers({"jet_model": model})

        # Redirect to the main page or any other appropriate page
        return redirect('/')

    return "Method not allowed", 405


@app.route("/rent/<int:jet_id>", methods=['GET', 'POST'])
def rent_jet(jet_id):
    if 'user_id' not in session:
        flash("You need to log in to rent a jet", "error")
        return redirect(url_for('login'))

    # Get the user ID from the session
    user_id = session['user_id']

    user = db.session.get(User, user_id)
    user_fullname = user.full_name

    # Get the jet object from the database
    jet = db.session.get(Jets, jet_id)

    # Check if the jet exists
    if not jet:
        flash("Jet not found", "error")
        return redirect(url_for('main'))

    # Inside the rent_jet route
    if request.method == 'POST':
        # Extract form data
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        selected_decorators = request.form.getlist('decorators')  # Assuming decorators are selected as checkboxes

        # Retrieve jet model and name from the database
        jet_model = jet.model
        jet_name = jet.name
        price_per_day = jet.price

        rental_days = (datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days

        # Determine pricing strategy based on the number of days rented
        if rental_days > 30:
            pricing_strategy = MonthlyPricingStrategy()
        else:
            pricing_strategy = StandardPricingStrategy()

        # Calculate total price using selected pricing strategy
        total_price = pricing_strategy.calculate_rental(rental_days, price_per_day)

        # Apply decorator costs
        for decorator_name in selected_decorators:
            if decorator_name == 'MaxSpeed':
                jet = MaxSpeed(jet)
            elif decorator_name == 'GPS':
                jet = GPS(jet)
            elif decorator_name == 'RoofBag':
                jet = RoofBag(jet)

        # Create Rentals object
        rental = Rentals(
            user_id=user_id,
            user_fullname=user_fullname,
            jet_id=jet_id,
            jet_model=jet_model,
            jet_name=jet_name,
            decorations=', '.join(selected_decorators),  # Join selected decorators into a string
            start_date=start_date,
            end_date=end_date,
            price_per_day=price_per_day,
            total_price=total_price,  # Update total price with decorators
            rental_days=rental_days
        )

        # Save the rental object to the database
        db.session.add(rental)
        db.session.commit()

        # Update the state of the jet to 'rented'
        jet.state = 'rented'
        db.session.commit()

        subject.notify_observers({"jet_model": jet_model, "user_id": user_id})

        # Redirect to the main page or any other appropriate page
        flash("Rental successful", "success")
        return redirect(url_for('main'))

    # Render the rental form template
    return render_template('rent_jet.html', jet=jet, title="")


if __name__ == '__main__':
    app.run(debug=True)
