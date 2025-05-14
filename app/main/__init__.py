
from flask import Blueprint

main = Blueprint("main",
                 __name__,
                 template_folder='templates',
                 static_folder='static',  # points to app/main/static
                 static_url_path='/main_static'  # URL prefix for static files
                 )

from . import routes  # import routes to attach views