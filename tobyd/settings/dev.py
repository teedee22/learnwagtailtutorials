from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '7w$qbg$a23$@$tq0_kka4*iklpnyjmt7f(d+=w4wfmw&)6$swu'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

STATIC_URL = '/static/'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ['MG_HOST']
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ['MG_ADDRESS']
EMAIL_HOST_PASSWORD =os.environ['MG_PASSWORD']
EMAIL_USE_TLS = True

INSTALLED_APPS = INSTALLED_APPS + [
    'debug_toolbar',
    'django_extensions',
]

MIDDLEWARE = MIDDLEWARE + [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = ("127.0.0.1", "172.17.0.1")

try:
    from .local import *
except ImportError:
    pass
