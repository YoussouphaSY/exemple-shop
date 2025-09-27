"""
WSGI config for shop360 project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop360.settings')

application = get_wsgi_application()