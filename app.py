from flask import Flask
from extensions import db

# Blueprint'leri import ediyoruz
from blueprints.main import main_bp
from blueprints.projects import projects_bp
from blueprints.tasks import tasks_bp
from blueprints.users import users_bp
from blueprints.tags import tags_bp
from blueprints.reports import reports_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = "super_secret_rgb_key"

    # Veritabanı tablolarını otomatik olarak ilklendir
    db.init_db()

    # Blueprint modüllerini uygulamaya kaydediyoruz
    app.register_blueprint(main_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(tags_bp)
    app.register_blueprint(reports_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
