from src import app, db, login_manager
from flask import render_template, redirect, url_for, request, session, flash, abort, jsonify
from flask_login import login_user, current_user, login_required, logout_user
from .forms import RegisterForm, LoginForm, BuildingForm
from .models import User, Building, GoldBuilding, MeatBuilding
from werkzeug.security import generate_password_hash, check_password_hash


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), category='danger')


@app.route("/")
def index():
    return render_template("index.html.j2")


@app.route("/register", methods=["GET"])
def register_get():
    form = RegisterForm()
    return render_template("register.html.j2", form=form)


@app.route("/login", methods=["GET"])
def login_get():
    if current_user.is_authenticated:
        flash("You are already logged in", "success")
        return redirect(url_for('u', username=current_user.username))
    else:
        form = LoginForm()
        return render_template("login.html.j2", form=form)


@app.route("/signin", methods=["POST"])
def login_post():
    form = LoginForm(request.form)
    if form.validate():
        user_ = User.query.filter_by(username=form.username.data).first()
        if user_ and check_password_hash(user_.password, form.password.data):
            login_user(user_)
            flash('Login Successful!', category='success')
            return redirect(url_for('u', username=form.username.data))
        else:
            flash('Password or Username does not match', category='danger')
            return redirect(url_for("login_get"))
    else:
        flash_errors(form)
        return redirect(url_for("login_get"))


@app.route("/signup", methods=["POST"])
def register_post():
    form = RegisterForm(request.form)
    if form.validate():
        user_ = User.query.filter_by(username=form.username.data).first()
        email_ = User.query.filter_by(email=form.email.data).first()
        if not (user_ or email_):   # check if username or email address already exists.
            user = User()
            user.username = form.username.data
            user.password = generate_password_hash(form.password.data)
            user.email = form.email.data
            user.buildings = [MeatBuilding(), GoldBuilding()]
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Register Successful, now you are logged in!', category='success')
            return redirect(url_for('u', username=form.username.data))
        else:
            flash('This username or email address is already in use', category='warning')
    else:
        flash_errors(form)
    return redirect(url_for('register_get'))


@app.route("/upgradeBuilding", methods=['POST'])
def upgrade_building():
    form = BuildingForm(request.form)
    user_ = current_user
    building = Building.query.filter_by(user=user_, id=form.id.data).first()
    if building:
        result = building.upgrade()
        if result:
            db.session.commit()
            flash('Success!', 'success')
        else:
            flash('Fail!', 'warning')
        return redirect(url_for('u', username=user_.username))


@login_required
@app.route("/u/<username>")
def u(username):
    user_ = current_user
    if user_.is_authenticated and user_.username == username:
        user_.produce()
        db.session.commit()
        buildings = [(building, BuildingForm(id=building.id)) for building in user_.buildings]
        return render_template("u.html.j2", buildings=buildings)

    else:
        searched_user = User.query.filter_by(username=username).first()
        if searched_user is not None:
            return "Private!"
        else:
            abort(404)


@app.route("/u/<username>/_update")
def update_(username):
    user_ = current_user
    if user_.is_authenticated and user_.username == username:
        user_.produce()
        db.session.commit()
    return jsonify({'meat': int(user_.meat), 'gold': int(user_.gold)})


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return 'OK'


@app.route("/dbc")
def createdb():
    db.drop_all()
    db.create_all()
    return "OK"
