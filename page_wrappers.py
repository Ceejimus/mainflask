"""Useful decorators for views."""
from flask import current_app as application
from flask import session, redirect, url_for
from functools import wraps

class auth_required(object):
    def __init__(self, group=None):
        self.group = group

    def __call__(self, f):
        @wraps(f)
        def _fn(*args, **kwargs):
            if application.config.get('ignore_auth'):
                session['username'] = 'fake-user'
                session['Atmoscape-Token'] = 'fake-token'
                return f(*args, **kwargs)

            username = None
            token = session.get('Atmoscape-Token')
            userId = None
            if token is not None:
                userId = (
                    application
                    .config['auth_domain']
                    .get_user_for_token(token)
                )

            if userId is None:
                return redirect(url_for('accounts.get_login_form'))
            else:
                user, groups = (
                    application
                    .config['auth_domain']
                    .get_user_by_id(userId)
                )
                if self.group is not None:
                    groups = [group.name for group in user.groups]
                    if self.group not in groups:
                        return redirect(url_for('index'))
                session['username'] = user.username
                return f(*args, **kwargs)

        return _fn

def maybe_ignore_auth(f):
    @wraps(f)
    def _fn(*args, **kwargs):
        if application.config.get('ignore_auth'):
            return redirect(url_for('index'))
        return f(*args, **kwargs)

    return _fn