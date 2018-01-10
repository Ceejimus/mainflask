"""Defines the accounts blueprint."""
from page_wrappers import maybe_ignore_auth
from flask import current_app as application
from flask import Blueprint
from flask import session, render_template, make_response, redirect, url_for
from forms import LoginForm, CreateUserForm

accounts_bp = Blueprint('accounts', __name__, template_folder='templates/accounts')

@accounts_bp.route("/account/create", methods=['GET'])
@maybe_ignore_auth
def get_create_user_form():
    form = CreateUserForm()
    return render_template(
        "create_user.html",
        title="Create Account",
        form=form
    )


@accounts_bp.route("/account/create", methods=['POST'])
@maybe_ignore_auth
def create_user():
    form = CreateUserForm()
    if form.validate_on_submit():
        valid = True
        users = application.config['auth_domain'].get_users()
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
            application.config['auth_domain'].add_user(username, email, password)
            return redirect(url_for('accounts.get_login_form'))
    else:
        return render_template(
            "create_user.html",
            title="Create Account",
            form=form
        )


@accounts_bp.route("/login", methods=['GET'])
@maybe_ignore_auth
def get_login_form():
    application.logger.info('TEST LOGIN LOGGING')
    token = session.get('Atmoscape-Token')
    application.logger.info(token)
    if token is not None:
        userId = application.config['auth_domain'].get_user_for_token(token)
        if userId is not None:
            return redirect(url_for('index'))

    form = LoginForm()
    return render_template(
        "login.html",
        title="Login",
        form=form
    )


@accounts_bp.route("/login", methods=['POST'])
@maybe_ignore_auth
def login():
    form = LoginForm()
    if form.validate_on_submit():
        import sys
        username = form.username.data
        password = form.password.data
        token = application.config['auth_domain'].login(username, password)
        if token is not None:
            import sys
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

@accounts_bp.route('/logout', methods=['GET'])
def logout():
    session.pop('Atmoscape-Token')
    return redirect(url_for('accounts.get_login_form'))
