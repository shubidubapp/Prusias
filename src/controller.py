from src import app, db, login_manager
from flask import render_template, redirect, url_for, request, session, flash, abort, jsonify
from flask_login import login_user, current_user, login_required, logout_user
from .forms import RegisterForm, LoginForm, BuildingForm, SoldierBuildingForm
from .models import User, Building, GoldBuilding, MeatBuilding, SwordsmanBuilding, ResourceBuilding ,SoldierBuilding
from werkzeug.security import generate_password_hash, check_password_hash


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"%s" % (
                error
            ), category='danger')


@app.route("/")
def index():
    return render_template("index.html.j2")


@app.route("/register/", methods=["GET"])
def register_get():
    form = RegisterForm()
    return render_template("register.html.j2", form=form)


@app.route("/login/", methods=["GET"])
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
            db.session.add(user)
            user.buildings.append(MeatBuilding())
            user.buildings.append(GoldBuilding())
            user.buildings.append(SwordsmanBuilding())
            user.set_time()
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
    building = Building.query.filter_by(user=current_user, id=form.id.data).first()
    if form.validate() and building:
        current_user.produce()
        result = building.upgrade()
        if result:
            db.session.commit()
            flash('Success!', 'success')
        else:
            flash('Fail!', 'warning')
    else:
        flash_errors(form)
    return redirect(url_for('u', username=current_user.username))


@app.route("/produceSoldier", methods=['POST'])
def produce_soldier():
    form = SoldierBuildingForm(request.form)
    building = Building.query.filter_by(user=current_user, id=form.id.data).first()
    if form.validate():
        if building.level > 0:
            current_user.produce()
            result = building.produce(form.count.data)
            if result:
                db.session.commit()
                flash('Success!', 'success')
            else:
                flash('Fail!', 'warning')
        else:
            flash('You should build this building first!')

    else:
        flash_errors(form)
    return redirect(url_for('u', username=current_user.username))


@login_required
@app.route("/u/<username>")
def u(username):
    if current_user.is_authenticated and current_user.username == username:
        current_user.produce()
        db.session.commit()
        resource_buildings = []
        soldier_buildings = []
        for building in current_user.buildings:
            if isinstance(building, ResourceBuilding):
                resource_buildings.append((building, BuildingForm(id=building.id)))
            else:
                soldier_buildings.append((building, BuildingForm(id=building.id), SoldierBuildingForm(id=building.id)))
        return render_template("u.html.j2", resource_buildings=resource_buildings, soldier_buildings=soldier_buildings)

    else:
        searched_user = User.query.filter_by(username=username).first()
        if searched_user is not None:
            return "Private!"
        else:
            abort(404)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/dbc")
def createdb():
    db.drop_all()
    db.create_all()
    flash("Database created", "success")
    return redirect(url_for('login_get'))

@app.route("/match")
def match():
    return render_template("match.html.j2")

