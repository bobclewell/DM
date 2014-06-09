import os
import sys

# Change this path to the absolute location of your DM repository
sys.path.append('/Users/bobclewell/Code/DM/ALPHA/DM')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()