import random

from flask import render_template, request

from app import app
from models import db, Tutor, Goal
from forms import BookingForm, RequestForm, SortTutorsForm
from func import get_data_from_db, save_request


@app.route("/")
def render_index():
    """Main page.
    Contains 6 random tutors, all possible education goals, request for a tutor search form.
    """

    # getting data from DB for HTML template
    #it was
    #all_tutors = get_data_from_db(option="tutors") 
    #all_goals = get_data_from_db(option="goals")
    all_tutors = db.session.query(Tutor).all()
    all_goals = db.session.query(Goal).all()

    # generating list of 6 random tutors
    random_tutors = random.sample(list(all_tutors), k=6)

    return render_template(
        "index.html", random_tutors=random_tutors, all_goals=all_goals
    )


@app.route("/all/", methods=["GET", "POST"])
def render_all():
    """Page with a list of all tutors and sorting form.
    Also contains request for a tutor search form.
    By default shows list of tutors with random order.
    """
    # getting data from DB for HTML template
    all_tutors = get_data_from_db(option="tutors")

    # by default we show all tutors in random order
    sorted_tutors = random.sample(all_tutors, len(all_tutors))

    form = SortTutorsForm()

    # getting sort-mode and showing page with sorted tutors by certain sort-mode
    if request.method == "POST":
        sort_by = form.sort_by.data
        if sort_by == "high_rating_first":
            sorted_tutors.sort(key=lambda x: x["rating"], reverse=True)
        elif sort_by == "high_price_first":
            sorted_tutors.sort(key=lambda x: x["price"], reverse=True)
        elif sort_by == "low_price_first":
            sorted_tutors.sort(key=lambda x: x["price"])
        return render_template("all.html", all_tutors=sorted_tutors, form=form)

    return render_template("all.html", all_tutors=sorted_tutors, form=form)


@app.route("/goals/<goal>/")
def render_goal(goal):
    """Page with a list of tutors by certain education goal."""

    # getting data from DB for HTML template
    all_tutors = get_data_from_db(option="tutors")
    all_goals = get_data_from_db(option="goals")
    tutors_by_goal = [tutor for tutor in all_tutors if goal in tutor["goals"]]

    return render_template(
        "goal.html", goal=goal, tutors_by_goal=tutors_by_goal, all_goals=all_goals
    )


@app.route("/profiles/<int:tutor_id>/")
def render_tutor_profile(tutor_id):
    """Page with info about a certain tutor."""

    # getting data from DB for HTML template
    all_tutors = get_data_from_db(option="tutors")
    days_of_week = get_data_from_db(option="days_of_week")

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
    form = RequestForm()
    return render_template("request.html", form=form)


@app.route("/request_done/", methods=["GET", "POST"])
def render_request_done():
    """This page show only when /request/ is successfully done."""

    form = RequestForm()
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
        all_goals = get_data_from_db(option="goals")
        all_time_for_practice = get_data_from_db(option="time_for_practice")

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
    all_days_of_week = get_data_from_db(option="days_of_week")
    all_tutors = get_data_from_db(option="tutors")

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
        all_days_of_week = get_data_from_db(option="days_of_week")
        all_tutors = get_data_from_db(option="tutors")
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
