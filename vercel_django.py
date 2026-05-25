import os
import sys

# Add frontend directory to path so settings and core can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), 'frontend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_app.settings')

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()

# Automatically collect static files for WhiteNoise on serverless boot
from django.conf import settings
staticfiles_dir = settings.STATIC_ROOT
if not os.path.exists(staticfiles_dir):
    try:
        from django.core.management import call_command
        call_command('collectstatic', '--noinput', '--clear')
    except Exception as e:
        print(f"Error running collectstatic: {e}")
