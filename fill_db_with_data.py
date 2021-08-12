from datetime import time
import json
from operator import countOf
from app import *
from typing import Any, Union


def get_data_from_db(option: str = "all") -> dict[str, Any]:
    """Read data from database (``db.json``) and returns a ``dict`` of data.
    1. Mode by default is ``option='all'`` returns dict with all data.
    2. ``option='tutors'`` returns dict with only about tutors.
    3. ``option='goals'`` returns dict with only about goals.
    4. ``option='days_of_week'`` returns dict with days of the week in rus and eng
    5. ``option='time_for_practice'`` returns dict with days.
    """
    if option not in ("all", "tutors", "goals", "days_of_week", "time_for_practice"):
        raise AttributeError

    with open("db.json", encoding="utf-8") as f:
        db: list[Union[list, dict]] = json.load(f)
        if option == "all":
            return db
        elif option == "goals":
            return db[0]
        elif option == "tutors":
            return db[1]
        elif option == "days_of_week":
            return db[2]
        elif option == "time_for_practice":
            return db[3]



#fill DaysOfWeek

d = {
    "travel": 1,
    "study": 2,
    "work": 3,
    "relocate": 4,
    "programming": 5
}
for tutor in get_data_from_db("tutors"):
    print(tutor['id'], tutor['goals'])



'''
#fill TimeForPractice
time_for_practice = get_data_from_db("time_for_practice")
for _, j in time_for_practice.items():
    print(j)
    my_time = TimeForPractice(description=j)
    db.session.add(my_time)
    db.session.commit()
'''

"""
#fill Tutors
for tutor in get_data_from_db("tutors"):
    tutor = Tutor(
        name=tutor['name'],
        about=tutor['about'],
        rating=tutor['rating'],
        picture=tutor['picture'],
        price=tutor['price'],
        free=tutor['free'],
    )
    db.session.add(tutor)
db.session.commit()"""


"""#fill Goals
for _, value in get_data_from_db("goals").items():
    print(value)
    goal = Goal(
        name=value[0],
        emoji=value[1]
    )
    db.session.add(goal)
db.session.commit()"""

"""#fill DaysOfWeek
count = 1
for _, value in get_data_from_db("days_of_week").items():
    if count == 8:
        break
    print(value)
    day = DaysOfWeek(
        eng_short_name = value[0],
        eng_full_name = value[1],
        rus_full_name = value[2]
    )
    db.session.add(day)
    count += 1
db.session.commit()"""