from ackr import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
  """
  Define the user model, users should have an ID and username.
  """

  __tablename__ = 'flasklogin-users'
  id = db.Column(
      db.Integer,
      primary_key=True
  )
  username = db.Column(
      db.String(100),
      nullable=False,
      unique=False
  )

  def __init__(self, id, username):
    self.id = id
    self.username = username

  """
  Methods needed for flask-login
  """
  def get_id(self):
    return self.id

  @property
  def is_authenticated(self):
    return True

  @property
  def is_active(self):
    return True

  @property
  def is_anonymous(self):
    return False


