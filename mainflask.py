"""entrypoint for flask app."""
import os
import json
from flask import Flask, render_template, request, session
from flask import make_response
import jinja2
from domain import AuthDomain
from werkzeug import secure_filename
from page_wrappers import auth_required, maybe_ignore_auth

env = jinja2.Environment()
env.filters['tojson'] = json.dumps

with open  ('config.json', 'r') as f:
    config = json.load(f)
    print("running with config\n", json.dumps(config, indent=4))

HOST = config["host"]
PORT = int(config["port"])
DB = config["db"]
USER = config["user"]
PASS = config["pass"]

auth_domain = AuthDomain(HOST, PORT, DB, USER, PASS)

active_dir_uploads = {}

def create_app(config):
    import sys
    from admin_blueprint import admin_bp
    from accounts_blueprint import accounts_bp
    from uploader_blueprint import uploader_bp

    application = Flask(__name__)
    application.register_blueprint(admin_bp)
    application.register_blueprint(accounts_bp)
    application.register_blueprint(uploader_bp)

    application.static_url_path = "/static"
    application.secret_key = 'AfUHFkB6s&PIVULP3IUgNMjZYA9uN96R'

    application.config['upload_folders'] = config["upload_folders"]
    application.config['default_folder'] = config.get("default_folder")
    application.config['tmp_dir'] = config.get('tmp_dir')

    application.config['auth_domain'] = auth_domain

    ignore_auth = config.get("ignore_auth")
    application.config['ignore_auth'] = False if ignore_auth is None else ignore_auth

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
