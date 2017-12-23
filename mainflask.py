"""entrypoint for flask app."""
from flask import Flask, render_template, redirect, url_for, request, session
from flask import make_response, json
from domain import AuthDomain
from forms import CreateUserForm, LoginForm
from functools import wraps
application = Flask(__name__)
application.static_url_path = "/static"
application.secret_key = 'AfUHFkB6s&PIVULP3IUgNMjZYA9uN96R'


with open  ('config.json', 'r') as f:
    data = json.load(f)
    print(data)

HOST = data["host"]
PORT = int(data["port"])
DB = data["db"]
USER = data["user"]
PASS = data["pass"]

auth_domain = AuthDomain(HOST, PORT, DB, USER, PASS)


class auth_required(object):
    def __init__(self, group=None):
        self.group = group

    def __call__(self, f):
        print(self.group)
        @wraps(f)
        def _fn(*args, **kwargs):
            username = None
            token = session.get('Atmoscape-Token')
            if token is not None:
                userId = auth_domain.get_user_for_token(token)

            if userId is None:
                return redirect(url_for('get_login_form'))
            else:
                user, groups = auth_domain.get_user_by_id(userId)
                if self.group is not None:
                    print(self.group)
                    groups = [group.name for group in user.groups]
                    print(groups)
                    if self.group not in groups:
                        return redirect(url_for('index'))
                session['username'] = user.username
                return f(*args, **kwargs)

        return _fn


@application.route("/", methods=['GET'])
@auth_required()
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
    token = session.get('Atmoscape-Token')
    if token is not None:
        userId = auth_domain.get_user_for_token(token)
        if userId is not None:
            return redirect(url_for('index'))

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

@application.route('/logout', methods=['GET'])
@auth_required()
def logout():
    session.pop('Atmoscape-Token')
    return redirect(url_for('get_login_form'))

@application.route("/admin", methods=['GET'])
@auth_required("admin")
def admin():
    return render_template(
        "admin.html",
        title="Admin",
        pending_users=auth_domain.get_pending_users(),
        groups=auth_domain.get_groups()
    )

@application.route("/processuser", methods=['POST'])
@auth_required("admin")
def process_user():
    print(request.json)
    userId = request.json.get('userId')
    groupId = request.json.get('groupId')
    action = request.json.get('action')

    if userId is None or userId == '':
        return json.dumps({'success': False}), 400, { 'ContentType':'application/json' }

    if action is None or action == '':
        return json.dumps({'success': False}), 400, { 'ContentType':'application/json' }

    if action == 'accept' and (groupId is None or groupId == ''):
        return json.dumps({'success': False}), 400, { 'ContentType':'application/json' }

    if action == 'accept':
        auth_domain.accept_user(userId, groupId)
    else:
        auth_domain.delete_user(userId)

    return json.dumps({'success': request.json}), 200, { 'ContentType':'application/json' }

if __name__ == '__main__':
    application.run()
