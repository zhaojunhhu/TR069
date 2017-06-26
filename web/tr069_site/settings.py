"""
Django settings for tr069_site project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TR069_DIR = os.path.dirname(os.path.dirname(BASE_DIR))

sys.path.append(TR069_DIR)
#import  testlibversion
#BS_VERSION = testlibversion.VERSION

#add by jias  20140627
sys.path.append(os.path.join(TR069_DIR, "TR069", "lib"))
sys.path.append(os.path.join(TR069_DIR, "TR069", "vendor"))

import TR069.lib.common.config as config
CONFIG_PATH = os.path.join(TR069_DIR, 'TR069', 'data', 'database.cfg')

def read_config():
    ret, ret_data = config.read_cfg(path=CONFIG_PATH, keys = "database")
    if ret == config.FAIL:
        err_info = "read config file failed, err info:%s!" % ret_data
        print err_info
        ret_data = {}
    return ret_data

dict_cfg = read_config()
if (not dict_cfg):
    desc = "read config file=%s fail" %CONFIG_PATH
    print desc
    raise Exception(desc)

# from cfg file --------------------------------------------------------
try:
    DB_HOST             = str(dict_cfg.get("DB_HOST"))
    DB_PORT             = int(dict_cfg.get("DB_PORT"))
    DB_NAME             = str(dict_cfg.get("DB_NAME"))
    DB_USER             = str(dict_cfg.get("DB_USER"))
    DB_PASSWORD         = str(dict_cfg.get("DB_PASSWORD"))
    VISIT_HOSTS         = str(dict_cfg.get("VISIT_HOSTS"))
    print '[%s:%s] %s %s(%s)' % (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD)
    
except Exception,e:    
    desc = "fail:%s" %(e)
    print desc
    raise Exception(desc)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(^=(wzt2i7+40er+wrtd*ee$g6ca3cunh2pp72gt9aw872wh%$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False

if not DEBUG:
    ALLOWED_HOSTS = ['localhost']
    ALLOWED_HOSTS.extend(VISIT_HOSTS.split(','))
    print ALLOWED_HOSTS

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'itms',
    'user_manager',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'tr069_site.urls'

WSGI_APPLICATION = 'tr069_site.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE':       'django.db.backends.mysql',
        'NAME':         DB_NAME,
        'USER':         DB_USER,
        'PASSWORD':     DB_PASSWORD,
        'HOST':         DB_HOST,
        'PORT':         DB_PORT
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'zh-CN'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SESSION_COOKIE_AGE = 60 * 60 * 12       # Age of cookie, in seconds. Set 12hours to expire for test and debug.
#SESSION_COOKIE_AGE = 60 * 15           # Age of cookie, in seconds. Set 15mins to expire.
SESSION_SAVE_EVERY_REQUEST = True       # Whether to save the session data on every request.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Whether a user's session cookie expires when the Web browser is closed.

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

#MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'media').replace('\\','/')

#STATIC_ROOT = 'D:/WorkSpace/TR069_BS/Trunk/tr069_site/static/'
if not DEBUG:
    STATIC_ROOT = os.path.join(os.path.dirname(__file__), 'static').replace('\\','/')

STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.path.dirname(__file__), 'static').replace('\\', '/'),
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    # r"C:\Python27\Lib\site-packages\django\templates",
    os.path.join(os.path.dirname(__file__), 'templates').replace('\\', '/'),
)
