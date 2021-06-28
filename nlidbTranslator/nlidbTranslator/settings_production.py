"""
This is the settings file used in production.
First, it imports all default settings, then overrides respective ones.
Secrets are stored in and imported from an additional file, not set under version control.
"""

import nlidbTranslator.settings_secrets as secrets

# noinspection PyUnresolvedReferences
from nlidbTranslator.settings import *

NLTK_DATA=os.path.join(Path(PROJECT_ROOT), "nltk_data")

PROJECT_ROOT = secrets.PROJECT_ROOT

### SECURITY ###

DEBUG = False

ALLOWED_HOSTS = secrets.HOSTS

SECRET_KEY = secrets.SECRET_KEY

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


