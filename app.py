from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from secrets import token_urlsafe
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


# Create the Flask app instance
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Define the database models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)

    # Define a relationship to the Role model
    role = db.relationship('Role', back_populates='users')


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    secret_id = db.Column(db.String(50), unique=True, nullable=True)  # Add this line

    # Define a relationship to the User model
    users = db.relationship('User', back_populates='role')


#class UserRole(db.Model):
#    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
#    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), primary_key=True)

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Define routes and other application logic here

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/test')
def test():
    return 'This is a test route!'

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Extract form data
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Validate the form data (add more robust validation as needed)

        # Hash the password before storing it
        password_hash = generate_password_hash(password)

        # Check if a secret ID is provided
        secret_id = request.form.get('secret_id')

        if secret_id:
            # Check if the provided secret ID matches a valid role
            role = Role.query.filter_by(secret_id=secret_id).first()
            if role is None:
                flash("Invalid secret ID.", 'error')
                return render_template('register.html', error="Invalid secret ID.")
        else:
            # If no secret ID is provided, assign the default 'Member' role
            role = Role.query.filter_by(name='Member').first()

        new_user = User(username=username, email=email, password_hash=password_hash, role=role)
        db.session.add(new_user)

        try:
            db.session.commit()
            login_user(new_user)
            flash("Registration successful!", 'success')
            return redirect(url_for('home'))
        except IntegrityError:
            db.session.rollback()
            flash("Username or email is already in use.", 'error')
            return render_template('register.html', error="Username or email is already in use.")

    return render_template('register.html')



@app.route('/registration-error')
def registration_error():
    message = request.args.get('message', 'An error occurred during registration.')
    return render_template('registration_error.html', message=message)


class CreateRoleForm(FlaskForm):
    name = StringField('Role Name', validators=[DataRequired()])
    submit = SubmitField('Create Role')

@app.route('/create_role_form', methods=['GET', 'POST'])
def create_role():
    form = CreateRoleForm()

    if form.validate_on_submit():
        # Form data is valid, proceed with role creation
        name = form.name.data

        # Generate a unique secret ID
        secret_id = token_urlsafe(16)

        new_role = Role(name=name, secret_id=secret_id)
        db.session.add(new_role)

        try:
            db.session.commit()
            flash(f"Role {name} created with secret ID {secret_id}", 'success')
        except IntegrityError:
            db.session.rollback()
            flash("Role name already exists.", 'error')

        return redirect(url_for('home'))

    return render_template('create_role_form.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form['username_or_email']
        password = request.form['password']

        # TODO: Validate credentials and log in the user
        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Login successful!", 'success')
            
            if current_user.role.name == 'Admin':
                return redirect(url_for('admin_dashboard'))
            else:
                # Print statement for debugging
                print("Redirecting to home...")
            
                return redirect(url_for('home'))  
        else:
            flash("Invalid username/email or password.", 'error')
            return render_template('login.html', error="Invalid username/email or password.")          
    else:
        # Render the login form for GET requests
        return render_template('login.html')


@app.route('/logout')
def logout():
    # TODO: Add logout logic
    logout_user()
    flash("Logout successful!", 'success')
    return redirect(url_for('home'))


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    # Check if the current user has the 'Admin' role
    if current_user.role.name != 'Admin':
        abort(403)  # Forbidden
    # Render the admin dashboard
    return render_template('admin_dashboard.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)
