import os
import sys

web_path = os.path.dirname(os.path.dirname(__file__))
sys.path.append(web_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'tr069_site.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()