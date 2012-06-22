import sys
import os

major, minor = sys.version_info[:2]
sys.path.append("%s/venv/lib/python%s.%s/site-packages" %
                (os.path.dirname(__file__), major, minor))

from mittach.web import app as application
