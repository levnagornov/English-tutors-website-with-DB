from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate

from config import Config

from errors.views import error_blp
from views.views import view_blp
from models import db


app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(view_blp)
app.register_blueprint(error_blp)

# CSRF token for correct work of WTForms module
csrf = CSRFProtect(app)

# initializing database
db.init_app(app)
migrate = Migrate(app, db, render_as_batch=True)


if __name__ == "__main__":
    app.run()
