from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SubmitField, HiddenField, SelectField
from wtforms.validators import InputRequired


class BookingForm(FlaskForm):
    """Booking form for a class with a tutor"""

    tutor_id = HiddenField()
    class_day = HiddenField()
    time = HiddenField()
    name = StringField("Вас зовут", [InputRequired("Пожалуйста, введите ваше имя")])
    phone = StringField(
        "Ваш телефон", [InputRequired("Пожалуйста, введите ваш номер телефона")]
    )
    submit = SubmitField("Записаться на пробный урок")


class RequestForm(FlaskForm):
    """Request form for a tutor search"""

    goal = RadioField(
        "Какая цель занятий?",
        default=1
    )
    time_for_practice = RadioField(
        "Сколько времени есть?",
        default=1
    )
    name = StringField(
        "Вас зовут", 
        [InputRequired()]
    )
    phone = StringField(
        "Ваш телефон", 
        [InputRequired()]
    )
    submit = SubmitField("Найдите мне преподавателя!")


class SortTutorsForm(FlaskForm):
    sort_by = SelectField(
        "Сортировка преподавателей",
        choices=[
            ("random", "В случайном порядке"),
            ("high_rating_first", "Сначала лучшие по рейтингу"),
            ("high_price_first", "Сначала дорогие"),
            ("low_price_first", "Сначала недорогие"),
        ],
        default="random",
    )
    submit = SubmitField("Сортировать")
