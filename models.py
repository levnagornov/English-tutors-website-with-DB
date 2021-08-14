from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


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
