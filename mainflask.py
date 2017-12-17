"""entrypoint for flask app."""
from flask import Flask, render_template, redirect, url_for
from domain import AuthDomain
from forms import CreateUserForm
application = Flask(__name__)
application.static_url_path = "/static"
application.secret_key = 'AfUHFkB6s&PIVULP3IUgNMjZYA9uN96R'


HOST = "192.168.0.104"
PORT = 5432
DB = "main"
USER = "postgres"
PASS = "postgres"

auth_domain = AuthDomain(HOST, PORT, DB, USER, PASS)


@application.route("/", methods=['GET'])
def index():
    return redirect(url_for('get_create_user_form'))
    # users = auth_domain.get_users()
    # return "\n".join([str(user) for user in users]) + '\n'


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
        if (auth_domain.is_username_unique(form.username.data) is not True):
            form.username.errors.append("Username is not unique.")
        else:
            return "success"

    return render_template(
        "create_user.html",
        title="Create Account",
        form=form
    )


if __name__ == '__main__':
    application.run()
