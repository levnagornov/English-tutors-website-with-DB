from flask import render_template, Blueprint, request

from sqlalchemy.sql import func

from errors.views import render_page_not_found
from models import *
from forms import *


view_blp = Blueprint("view_blp", __name__)


@view_blp.route("/")
def render_index():
    """Main page.
    Contains 6 random tutors, all possible education goals, request for a tutor search form.
    """

    random_tutors = db.session.query(Tutor).order_by(func.random()).limit(6)
    goals = db.session.query(Goal).all()

    return render_template("index.html", random_tutors=random_tutors, goals=goals)


@view_blp.route("/all/", methods=["GET", "POST"])
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


@view_blp.route("/goals/<int:goal_id>/")
def render_goal(goal_id):
    """Page with a list of tutors by certain education goal."""

    goal = db.session.query(Goal).get(goal_id)
    if goal is None:
        return render_page_not_found(404)

    return render_template("goal.html", goal=goal, tutors_by_goal=goal.tutors)


@view_blp.route("/profiles/<int:tutor_id>/")
def render_tutor_profile(tutor_id):
    """Page with info about a certain tutor."""

    tutor = db.session.query(Tutor).get(tutor_id)
    if tutor is None:
        return render_page_not_found(404)

    days_of_week = db.session.query(DaysOfWeek).order_by(DaysOfWeek.id).all()

    return render_template("profile.html", tutor=tutor, days_of_week=days_of_week)


@view_blp.route("/request/")
def render_request():
    """Page with form for personal seeking a tutor."""

    goals = db.session.query(Goal).all()
    times_for_practice = db.session.query(TimeForPractice).all()

    form = RequestForm()
    form.goal.choices = [
        (goal.id, " ".join((goal.name, goal.emoji))) 
        for goal in goals
    ]

    form.time_for_practice.choices = [
        (time.id, time.description) 
        for time in times_for_practice
    ]

    return render_template("request.html", form=form)


# DOESN'T WORK validate_on_submit()!!!!!!!
@view_blp.route("/request_done/", methods=["GET", "POST"])
def render_request_done():
    """This page show only when /request/ is successfully done."""

    form = RequestForm()
    # Restrict access if /request/ was ignored
    # DOESN'T WORK validate_on_submit()!!!!!!!!
    if not (
        request.method == "POST" and form.validate_on_submit()
    ):
        return render_page_not_found(404)

    request_tutor = Request(
        client_name=form.name.data,
        client_phone=form.phone.data,
        time_for_practice_id=form.time_for_practice.data,
        goal_id=form.goal.data,
    )
    db.session.add(request_tutor)
    db.session.commit()

    goal = db.session.query(Goal).get(form.goal.data)
    time_for_practice = db.session.query(TimeForPractice).get(
        form.time_for_practice.data
    )

    return render_template(
        "request_done.html", goal=goal, time_for_practice=time_for_practice, form=form
    )


@view_blp.route("/booking/<int:tutor_id>/<int:class_day_id>/<time>/")
def render_booking(tutor_id, class_day_id, time):
    """Booking page.
    This page allows you to book a class with a certain tutor on a chosen day and time.
    Requires:
    1. tutor_id;
    2. class_day_id;
    3. time;

    """

    class_day = db.session.query(DaysOfWeek).get(class_day_id)
    tutor = db.session.query(Tutor).get(tutor_id)
    # checking if user fill url manually with mistakes
    if None in (tutor, class_day):
        return render_page_not_found(404)

    shedule = tutor.free.get(class_day.eng_short_name)
    if shedule.get(time) == False:
        return render_page_not_found(404)

    form = BookingForm()
    # assign hidden fields of form with passed from URL data
    form.class_day.data = class_day_id
    form.time.data = time
    form.tutor_id.data = tutor_id

    return render_template(
        "booking.html",
        tutor=tutor,
        class_day=class_day,
        time=time,
        form=form,
    )


@view_blp.route("/booking_done/", methods=["GET", "POST"])
def render_booking_done():
    """This page show only when /booking/ is successfully done."""

    form = BookingForm()
    # Restrict access if /booking/ was ignored
    if not (request.method == "POST" and form.validate_on_submit()):
        return render_page_not_found(404)

    booking = Booking(
        client_name=form.name.data,
        client_phone=form.phone.data,
        time=form.time.data,
        class_day=form.class_day.data,
        tutor_id=form.tutor_id.data,
    )
    db.session.add(booking)
    db.session.commit()

    class_day = db.session.query(DaysOfWeek).get(form.class_day.data)
    tutor = db.session.query(Tutor).get(form.tutor_id.data)

    return render_template(
        "booking_done.html", tutor=tutor, class_day=class_day, form=form
    )
