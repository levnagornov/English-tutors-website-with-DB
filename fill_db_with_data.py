from models import *


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
db.session.commit()

goals = get_data_from_db("goals")
for _, descr in goals:
    goal = Goal(
        name=descr[0],
        emoji=descr[1],
    )
    db.session.add(goal)
db.session.commit()

#add many-many tutors_goals


