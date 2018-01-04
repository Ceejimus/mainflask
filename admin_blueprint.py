"""Defines the admin blueprint"""
from flask import current_app as application
from flask import Blueprint
from flask import render_template, json, request
from page_wrappers import auth_required

admin_bp = Blueprint('admin', __name__, template_folder='templates/admin')

@admin_bp.route("/admin", methods=['GET'])
@auth_required("admin")
def admin():
    return render_template(
        "admin.html",
        title="Admin",
        pending_users=application.config['auth_domain'].get_pending_users(),
        groups=application.config['auth_domain'].get_groups()
    )

@admin_bp.route("/processuser", methods=['POST'])
@auth_required("admin")
def process_user():
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
        application.config['auth_domain'].accept_user(userId, groupId)
    else:
        application.config['auth_domain'].delete_user(userId)

    return json.dumps({'success': request.json}), 200, { 'ContentType':'application/json' }