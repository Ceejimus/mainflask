"""Defines the admin blueprint"""
import os
from flask import current_app as application
from flask import Blueprint
from flask import render_template, json, request
from auth_tools import auth_required
from helpers import json_response
from werkzeug import secure_filename
from helpers import eprint

uploader_bp = Blueprint('uploader', __name__, template_folder='templates/uploader')


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'mp4', 'mkv', 'avi', 'srt', 'vtt' 'mp3', 'nfo'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def secure_path(path):
    parts = path.split(os.sep)

    secure_parts = [
       secure_part
       for secure_part
       in [
           part.replace('..', '')
           for part
           in parts
       ] if secure_part is not ''
    ]

    fullpath = ""

    for secure_part in secure_parts:
        fullpath = os.path.join(fullpath, secure_part)

    return fullpath


@uploader_bp.route('/uploader', methods=['GET'])
@auth_required()
def uploader():
    return render_template('fileupload.html',
        folders=application.config["upload_folders"].keys(),
        default_folder=application.config["default_folder"]
    )


@uploader_bp.route('/upload_file/<folder>', methods=['POST'])
@auth_required()
def upload_file(folder):
    file = request.files.get('file')
    if file is None:
        return json_response({'message': 'No file provided.'}, status_code=400)
    elif file.name == '' or not allowed_file(file.filename):
        return json_response({'message': 'File not allowed.'}, status_code=400)

    path, filename = os.path.split(file.filename)

    if os.sep == '\\':
        path = path.replace('/', '\\')
    else:
        path = path.replace('\\', '/')

    secured_path = secure_path(path)

    fullpath = os.path.join(application.config['tmp_dir'], secured_path)

    os.makedirs(fullpath, exist_ok=True)

    filepath = os.path.join(fullpath, filename)

    file.save(filepath)
    return json.dumps({'success': request.json}), 200, { 'ContentType':'application/json' }