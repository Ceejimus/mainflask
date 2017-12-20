"""entrypoint for flask app."""
from flask import Flask, render_template, redirect, url_for, request, session
from flask import make_response
from domain import AuthDomain
from forms import CreateUserForm, LoginForm
from functools import wraps
import json
application = Flask(__name__)
application.static_url_path = "/static"
application.secret_key = 'AfUHFkB6s&PIVULP3IUgNMjZYA9uN96R'


with open  ('config.json', 'r') as f:
    data = json.load(f)
    print(data)

HOST = data["HOST"]
PORT = int(data["PORT"])
DB = data["DB"]
USER = data["USER"]
PASS = data["PASS"]

auth_domain = AuthDomain(HOST, PORT, DB, USER, PASS)


def login_required(fn):
    @wraps(fn)
    def _fn(*args, **kwargs):
        username = None
        if ('Atmoscape-Token' in session):
            token = session['Atmoscape-Token']
            username = auth_domain.get_user_for_token(token)

        if (username is None):
            return redirect(url_for('get_login_form'))
        else:
            session['username'] = username
            return fn(*args, **kwargs)

    return _fn


@application.route("/", methods=['GET'])
@login_required
def index():
    return render_template(
        "home.html",
        username=session['username']
    )


@application.route("/account/create", methods=['GET'])
def get_create_user_form():
    form = CreateUserForm()
    return render_template(
        "create_user.html",
        title="Create Account",
        form=form
    )


@application.route("/account/create", methods=['POST'])
def create_user():
    form = CreateUserForm()
    if form.validate_on_submit():
        valid = True
        users = auth_domain.get_users()
        if (form.username.data in [user.username for user in users]):
            form.username.errors.append("Username is not unique.")
            valid = False
        if (form.email.data in [user.email for user in users]):
            valid = False
            # TODO: handle this
        if (valid):
            username = form.username.data
            email = form.email.data
            password = form.password.data
            auth_domain.add_user(username, email, password)
            return redirect(url_for('get_login_form'))
    else:
        return render_template(
            "create_user.html",
            title="Create Account",
            form=form
        )


@application.route("/login", methods=['GET'])
def get_login_form():
    form = LoginForm()
    return render_template(
        "login.html",
        title="Login",
        form=form
    )


@application.route("/login", methods=['POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        import sys
        print("debug", file=sys.stderr)
        username = form.username.data
        password = form.password.data
        token = auth_domain.login(username, password)
        if token is not None:
            import sys
            print(token, file=sys.stderr)
            resp = make_response(redirect(url_for('index')))
            session['Atmoscape-Token'] = token
            return resp
        else:
            form.username.errors.append("User/Password incorrect")

    return render_template(
        "login.html",
        title="Login",
        form=form
    )


if __name__ == '__main__':
    application.run()
