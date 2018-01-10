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
            application.logger.info('calling "{}"'.format(f.__name__))
            if application.config.get('ignore_auth'):
                application.logger.info('ignoring auth creating cake user')
                session['username'] = 'fake-user'
                session['Atmoscape-Token'] = 'fake-token'
                return f(*args, **kwargs)

            username = None
            token = session.get('Atmoscape-Token')
            userId = None
            if token is not None:
                application.logger.info('Token found: "{}"'.format(token))
                userId = (
                    application
                    .config['auth_domain']
                    .get_user_for_token(token)
                )

            if userId is None:
                application.logger.info('No user id for token -- redirecting')
                return redirect(url_for('accounts.get_login_form'))
            else:
                user, groups = (
                    application
                    .config['auth_domain']
                    .get_user_by_id(userId)
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
                application.logger.info(
                    'setting username for session: "{}"'.format(user.username)
                )
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