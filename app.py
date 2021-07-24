from flask import Flask
from flask_wtf.csrf import CSRFProtect

from config import Config


app = Flask(__name__)
app.config.from_object(Config)
csrf = CSRFProtect(app)  # CSRF token for correct work of WTForms module

# getting connection to DataBase

from views import *

if __name__ == "__main__":
    app.run(debug=True)
