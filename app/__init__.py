import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Base class for model_class
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def create_app():
    app = Flask(__name__,instance_relative_config=True)
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass  # Already exists
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')

    # Create uploads folder if missing
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Define DB path relative to instance folder for better portability
    db_path = os.path.join(app.instance_path, "cafes.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Optional: Disable modification tracking
    app.config["SECRET_KEY"] = "RTY4676E7784883G7E"
    db.init_app(app)


    # Register blueprints
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    # Create tables within the application context
    with app.app_context():
        # Import models *inside* the context and after db is initialized
        # This avoids potential circular imports if models need the app context
        db.create_all()
        print(f"Database created at: {db_path}")  # Add print statement for confirmation

    return app
