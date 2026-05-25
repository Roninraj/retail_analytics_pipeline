import os
import sys

# Add frontend directory to path so settings and core can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), 'frontend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_app.settings')

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
