"""entrypoint for flask app."""
import os
import json
from flask import Flask, render_template, request, session
from flask import make_response
from domain import AuthDomain
from page_wrappers import auth_required, maybe_ignore_auth


with open('config.json', 'r') as f:
    config = json.load(f)
    print("running with config\n", json.dumps(config, indent=4))


def register_domains(application, config):
    db_host = config["host"]
    db_port = int(config["port"])
    db_name = config["db"]
    db_user = config["user"]
    db_pass = config["pass"]
    application.config['auth_domain'] = AuthDomain(db_host, db_port, db_name, db_user, db_pass)


def create_app(config):
    with open('flask.key', 'r') as f:
        key = f.read()

    application = Flask(__name__)

    import jinja2
    env = jinja2.Environment()
    env.filters['tojson'] = json.dumps

    register_domains(application, config)

    application.static_url_path = "/static"
    application.secret_key = key

    application.config['upload_folders'] = config["upload_folders"]
    application.config['default_folder'] = config.get("default_folder")
    application.config['tmp_dir'] = config.get('tmp_dir')

    ignore_auth = config.get("ignore_auth")
    application.config['ignore_auth'] = False if ignore_auth is None else ignore_auth

    from admin_blueprint import admin_bp
    from accounts_blueprint import accounts_bp
    from uploader_blueprint import uploader_bp
    application.register_blueprint(admin_bp)
    application.register_blueprint(accounts_bp)
    application.register_blueprint(uploader_bp)

    return application

application = create_app(config)


@application.route("/", methods=['GET'])
@auth_required()
def index():
    return render_template(
        "home.html",
        username=session['username']
    )


if __name__ == '__main__':
    application.run()
