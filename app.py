import json
import random

from flask import Flask, render_template, request
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from sqlalchemy.sql import func

from config import Config
from forms import BookingForm, RequestForm, SortTutorsForm


app = Flask(__name__)
app.config.from_object(Config)
csrf = CSRFProtect(app)  # CSRF token for correct work of WTForms module
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)


#many-to-many table for Tutor and Goal
tutor_has_goal = db.Table('tutor_goals',
    db.Column('tutor_id', db.Integer, db.ForeignKey('tutors.id')),
    db.Column('goal_id', db.Integer, db.ForeignKey('goals.id'))
)


class Tutor(db.Model):
    """This is tutor's SQLAlchemy model.
    Tutor is related with Goal (many-to-many).
    """

    __tablename__ = "tutors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    about = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    picture = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    free = db.Column(db.JSON, nullable=False)
    goals = db.relationship('Goal', secondary=tutor_has_goal,back_populates="tutors")


class Goal(db.Model):
    """This is goal's SQLAlchemy model.
    Goal is related with Tutor (many-to-many).
    """

    __tablename__ = "goals"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    emoji = db.Column(db.String, nullable=False)
    tutors = db.relationship('Tutor', secondary=tutor_has_goal, back_populates="goals")


class Booking(db.Model):
    """This is booking SQLAlchemy model.
    Booking is related with Tutor (one-to-many).
    """

    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String, nullable=False)
    client_phone = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)
    class_day = db.Column(db.String, nullable=False)
    tutor_id = db.Column(db.Integer, db.ForeignKey("tutors.id"), nullable=False)
    tutors = db.relationship('Tutor')


class Request(db.Model):
    """This is booking SQLAlchemy model.
    Request is related with Goal (one-to-many)
    Request is related with TimeForPractice (one-to-many)
    """
    
    __tablename__ = "requests"
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String, nullable=False)
    client_phone = db.Column(db.String, nullable=False)

    time_for_practice = db.relationship('TimeForPractice')
    time_for_practice_id = db.Column(db.Integer, db.ForeignKey("timeforpractice.id"), nullable=False)

    goals = db.relationship('Goal')
    goal_id = db.Column(db.Integer, db.ForeignKey("goals.id"), nullable=False)


class TimeForPractice(db.Model):
    """This is time for practice SQLAlchemy model.
    TimeForPractice is related with Request (many-to-one).
    """

    __tablename__ = "timeforpractice"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String, nullable=False, unique=True)


class DaysOfWeek(db.Model):
    """This SQLAlchemy model contains all days of the week in English and Russian, plus a short English version.
    """

    __tablename__ = "daysofweek"
    id = db.Column(db.Integer, primary_key=True)
    eng_short_name = db.Column(db.String, nullable=False, unique=True)
    eng_full_name = db.Column(db.String, nullable=False, unique=True)
    rus_full_name = db.Column(db.String, nullable=False, unique=True)


@app.route("/")
def render_index():
    """Main page.
    Contains 6 random tutors, all possible education goals, request for a tutor search form.
    """

    random_tutors = db.session.query(Tutor).order_by(func.random()).limit(6)
    goals = db.session.query(Goal).all()

    return render_template("index.html", random_tutors=random_tutors, goals=goals)


@app.route("/all/", methods=["GET", "POST"])
def render_all():
    """Page with a list of all tutors and sorting form.
    Also contains request for a tutor search form.
    By default shows list of tutors with random order.
    """
    
    tutors = db.session.query(Tutor).order_by(func.random()).all()
    form = SortTutorsForm()
    # getting sort-mode and showing page with sorted tutors by certain sort-mode
    if request.method == "POST":
        sort_by = form.sort_by.data
        if sort_by == "high_rating_first":
            tutors = db.session.query(Tutor).order_by(Tutor.rating.desc()).all()
        elif sort_by == "high_price_first":
            tutors = db.session.query(Tutor).order_by(Tutor.price.desc()).all()
        elif sort_by == "low_price_first":
            tutors = db.session.query(Tutor).order_by(Tutor.price).all()

    return render_template("all.html", tutors=tutors, form=form)



@app.route("/goals/<int:goal_id>/")
def render_goal(goal_id):
    """Page with a list of tutors by certain education goal."""

    goal = db.session.query(Goal).get(goal_id)
    if goal is None:
        return render_not_found(404)

    return render_template("goal.html", goal=goal, tutors_by_goal=goal.tutors)


@app.route("/profiles/<int:tutor_id>/")
def render_tutor_profile(tutor_id):
    """Page with info about a certain tutor."""

    # getting data from DB for HTML template
    all_tutors = db.session.query(Tutor).all()
    days_of_week = db.session.query(DaysOfWeek).all()

    # getting tutor info by tutor_id
    try:
        tutor_info = [
            tutor
            for tutor in all_tutors
            if tutor.get("id", "No match data") == int(tutor_id)
        ][0]
    except IndexError:
        return render_not_found(404)

    return render_template(
        "profile.html", tutor_info=tutor_info, days_of_week=days_of_week
    )


@app.route("/request/")
def render_request():
    """Page with form for personal seeking a tutor."""

    goals = db.session.query(Goal).all()
    times_for_practice = db.session.query(TimeForPractice).all()

    form = RequestForm()

    form.goal.choices = [
        (key, " ".join(value))
        for key, value in goals.items()
    ]
    form.time_for_practice.choices=[
        (key, value)
        for key, value in times_for_practice.items()
    ]

    return render_template("request.html", form=form)


@app.route("/request_done/", methods=["GET", "POST"])
def render_request_done():
    """This page show only when /request/ is successfully done."""

    goals = db.session.query(Goal).all()
    times_for_practice = db.session.query(TimeForPractice).all()

    form = RequestForm()
    
    form.goal.choices = [
        (key, " ".join(value))
        for key, value in goals.items()
    ]
    form.time_for_practice.choices=[
        (key, value)
        for key, value in times_for_practice.items()
    ]

    if request.method == "POST" and form.validate_on_submit():
        # saving users requests in a json file
        goal = form.goal.data
        time_for_practice = form.time_for_practice.data
        client_name = form.name.data
        client_phone = form.phone.data
        req = {
            "client_name": client_name,
            "client_phone": client_phone,
            "goal": goal,
            "time_for_practice": time_for_practice,
        }
        save_request(req, file_name="request.json")

        # getting data from DB for HTML template
        all_goals = db.session.query(Goal).all()
        all_time_for_practice = db.session.query(TimeForPractice).all()

        return render_template(
            "request_done.html",
            all_goals=all_goals,
            all_time_for_practice=all_time_for_practice,
            goal=goal,
            time_for_practice=time_for_practice,
            client_name=client_name,
            client_phone=client_phone,
        )

    # Restrict access if /request/ was ignored
    return render_not_found(404)


@app.route("/booking/<tutor_id>/<class_day>/<time>/")
def render_booking(tutor_id, class_day, time):
    """Booking page.
    This page allows you to book a class with a certain tutor on a chosen day and time.
    Requires:
    1. tutor_id;
    2. class_day;
    3. time;

    Additional info from db - all_days_of_week and all_tutors.
    """
    # getting data from DB for HTML template
    all_days_of_week = db.session.query(DaysOfWeek).all()
    all_tutors = db.session.query(Tutor).all()

    # getting data about certain tutor among all tutors for a temlate
    try:
        tutor_info = [
            tutor
            for tutor in all_tutors
            if tutor.get("id", "No match data") == int(tutor_id)
        ][0]
    except IndexError:
        return render_not_found(404)

    # TODO: add this to TRY block above. Check class_day and time by tutor_id
    # handling error in day of week spelling
    # if class_day not in []:
    #     return render_not_found(404)

    # assign hidden fields of form with passed from URL data
    form = BookingForm()
    form.class_day.data = class_day
    form.time.data = time
    form.tutor_id.data = tutor_id

    return render_template(
        "booking.html",
        tutor_info=tutor_info,
        tutor_id=tutor_id,
        class_day=class_day,
        time=time,
        all_days_of_week=all_days_of_week,
        form=form,
    )


@app.route("/booking_done/", methods=["GET", "POST"])
def render_booking_done():
    """This page show only when /booking/ is successfully done."""

    form = BookingForm()
    if request.method == "POST" and form.validate_on_submit():
        # saving booking-request in a json file
        client_name = form.name.data
        client_phone = form.phone.data
        class_day = form.class_day.data
        time = form.time.data
        tutor_id = form.tutor_id.data
        req = {
            "client_name": client_name,
            "client_phone": client_phone,
            "class_day": class_day,
            "time": time,
            "tutor_id": tutor_id,
        }
        save_request(req, file_name="booking.json")

        # getting data from DB for HTML template
        all_days_of_week = db.session.query(DaysOfWeek).all()
        all_tutors = db.session.query(Tutor).all()
        tutor_info = [
            tutor
            for tutor in all_tutors
            if tutor.get("id", "No match data") == int(tutor_id)
        ][0]

        return render_template(
            "booking_done.html",
            all_days_of_week=all_days_of_week,
            class_day=class_day,
            time=time,
            client_name=client_name,
            client_phone=client_phone,
            tutor_info=tutor_info,
            tutor_id=tutor_id,
        )

    # Restrict access if /booking/ was ignored
    return render_not_found(404)


# errors handling
@app.errorhandler(500)
def render_server_error(error, msg="Что-то не так, но мы все починим!"):
    """Handling 500 error."""

    return render_template("error.html", msg=msg), 500


@app.errorhandler(404)
def render_not_found(
    error, msg="Ничего не нашлось! Вот неудача, отправляйтесь на главную!"
):
    """Handling 404 error"""

    return render_template("error.html", msg=msg), 404


@app.errorhandler(400)
def render_bad_request(
    error, msg="Ничего не нашлось! Вот неудача, отправляйтесь на главную!"
):
    """Handling 400 error"""

    return render_template("error.html", msg=msg), 400


def save_request(request, file_name):
    """Saves user request into file_name"""
    try:
        with open(file_name, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []
    data.append(request)
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4, separators=(",", ": "))



if __name__ == "__main__":
    app.run(debug=True)
