"""
WSGI config for alquipiso project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import sys

project_path = "/home/alenicbra/alquipiso"
if project_path not in sys.path:
    sys.path.append(project_path)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alquipiso.settings')

application = get_wsgi_application()
