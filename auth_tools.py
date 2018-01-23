"""Useful decorators for views."""
import time
from flask import current_app as application
from flask import session, redirect, url_for
from functools import wraps


def session_expired(session_info):
    millis = int(round(time.time()) * 1000)
    if (session_info['exp'] < millis):
        return True

    session_info['exp'] = millis + (12 * 60 * 60 * 1000)
    return False


class auth_required(object):
    def __init__(self, group=None):
        self.group = group

    def __call__(self, f):
        @wraps(f)
        def _fn(*args, **kwargs):
            application.logger.info('calling "{}"'.format(f.__name__))
            if application.config.get('ignore_auth'):
                application.logger.info('ignoring auth creating cake user')
                millis = int(round(time.time()) * 1000)
                session['info'] = {
                    'user_id': 'fake-user-id',
                    'username': 'username',
                    'exp': millis + (12 * 60 * 60 * 1000)
                }
                return f(*args, **kwargs)

            session_info = session.get('info')

            if session_info is None or session_expired(session_info):
                session['info'] = None
                application.logger.info('No session info -- redirecting')
                return redirect(url_for('accounts.get_login_form'))
                
            user_id = session_info['user_id']
            user, groups = (
                application
                .config['auth_domain']
                .get_user_by_id(user_id)
            )
            application.logger.info('Got user for token: "{}" in groups: '.format(
                    user,
                    ','.join([str(g) for g in groups])
                )
            )
            if self.group is not None:
                application.logger.info(
                    'Call "{}" requires group "{}"'.format(f.__name__, self.group)
                )
                groups = [group.name for group in user.groups]
                if self.group not in groups:
                    application.logger.info('Access denied')
                    return redirect(url_for('index'))

            return f(*args, **kwargs)

        return _fn

def maybe_ignore_auth(f):
    @wraps(f)
    def _fn(*args, **kwargs):
        if application.config.get('ignore_auth'):
            return redirect(url_for('index'))
        return f(*args, **kwargs)

    return _fn