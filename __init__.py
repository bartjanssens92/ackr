from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from ackr.config import Config

app = Flask(__name__)
app.secret_key = Config.secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/sessions.db'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db = SQLAlchemy()
db.init_app(app)
from ackr.models import User
with app.app_context():
  db.create_all()


from ackr import routes
