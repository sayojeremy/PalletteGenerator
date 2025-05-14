import os
from flask import Flask

def create_app():
    app = Flask(__name__, instance_relative_config=True)


    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Register blueprints
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
