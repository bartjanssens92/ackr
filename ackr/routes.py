import os

from time import time
from ackr import app, login_manager, db
from ackr import icinga, ldap
from ackr.models import User
from ackr.config import Config

from flask import render_template, request, jsonify, send_from_directory, flash ,redirect, url_for
from flask_login import login_required, current_user, UserMixin, login_user, logout_user

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField


@login_manager.user_loader
def user_loader(user_id):
  """
  Define the user_loader to return the id from the DB,
  this way flask-login knows that users are logged in
  and which users are not.
  """
  try:
    return User.query.get(user_id)
  except:
    return None

class LoginForm(FlaskForm):
  """
  Define the loginform
  """
  username = StringField('Username')
  password = PasswordField('Password')
  submit = SubmitField('Submit')


@app.route('/login', methods=['GET', 'POST'])
def login():
  """
  The login endpoint, it should just redirect the user if
  they are already logged in, otherwise show the loginform.
  """

  if current_user.is_authenticated:
    return redirect(url_for('dashboard'))

  form = LoginForm()
  if request.method == 'POST' and form.validate_on_submit():

    try:
      conn = ldap.login(form.username.data, form.password.data)
    except:
      flash('Invalid Username/Password combination')

    if ldap.in_group(conn, form.username.data, Config.icinga_group):
      id = str(int(ldap.get_uid(conn, form.username.data)) + int(time()))
      user = User(id = id, username = form.username.data)
      db.session.add(user)
      db.session.commit()
      login_user(user)
      next = request.args.get('next')
      return redirect(next or url_for('dashboard'))
    flash('User not authorized to access this resource')

  return render_template('login.html', form=form)


@app.route('/logout')
def logout():
   """
   Logout the user but first remove the session from the db.
   """
   User.query.filter_by(id=current_user.id).delete()
   db.session.commit()
   logout_user()
   return redirect(url_for('login'))


@app.route('/')
@login_required
def dashboard():
  return render_template('dashboard.html')


@app.route('/favicon.ico')
def favicon():
    """
    Make the favicon load the logo from disk.
    """
    return send_from_directory(os.path.join(app.root_path, 'static/images'),'logo.png', mimetype='image/logo.png')


@app.get('/services')
@login_required
def get_services():
  """
  Endpoint to get a json object containing all the services that are in state NOTOK.
  """
  services = icinga.get_services()
  return services, 200


@app.route('/ack', methods=["POST"])
@login_required
def ack():
  """
  Endpoint to acknoledge a service, the request should contain the service and host names:
  {
    "host_name": "host01.some.example.com",
    "service_name": "mem"
  }
  """
  if not 'host_name' in request.json or not 'service_name' in request.json:
    return '{"message": "invalid data passed, must include host_name and service_name"}', 502
  else:
    icinga.ack_service(request.json['host_name'], request.json['service_name'], str(current_user.username)) 

  return '{"message": "acked"}', 200
