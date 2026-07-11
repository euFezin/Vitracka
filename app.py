import json
import os
from datetime import timedelta, date


from flask import Flask, render_template
from flask_login import LoginManager 
from flask_migrate import Migrate
from sqlalchemy.engine import URL
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager

from core.routes.institucional import institucional_bp
from core.routes.auth import auth_bp
from core.routes.api_auth import api_auth_bp
from core.routes.onboarding import onboarding_bp
from core.routes.api_onboarding import api_onboarding_bp
from core.routes.dashboard import dashboard_bp
from core.routes.api_dashboard import api_dashboard_bp
from core.routes.nutricao import nutricao_bp
from core.routes.api_nutricao import api_nutricao_bp
from core.routes.checkin import checkin_bp
from core.routes.api_checkin import api_checkin_bp
from core.routes.treino import treino_bp
from core.routes.api_treino import api_treino_bp
from core.routes.chat_routes import chat_bp
from core.routes.api_chat import api_chat_bp
from core.routes.configuracoes import configuracoes_bp
from core.routes.api_configuracoes import api_configuracoes_bp
from core.models import User, db

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "musculacao_Vitracka")


@app.template_filter("from_json")
def from_json_filter(value):
    return json.loads(value)

database_url = os.getenv("DATABASE_URL")
if not database_url:
    db_user = os.getenv("MYSQL_USER", "root")
    db_password = os.getenv("MYSQL_PASSWORD", "p@$$w0rd")
    db_host = os.getenv("MYSQL_HOST", "localhost")
    db_name = os.getenv("MYSQL_DATABASE", "vitracka")
    database_url = URL.create(
        "mysql+pymysql",
        username=db_user,
        password=db_password,
        host=db_host,
        database=db_name,
        query={"charset": "utf8mb4"},
    )

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "jwt-vitracka-dev")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Entre na sua conta para continuar."
login_manager.init_app(app)
jwt = JWTManager(app)

app.register_blueprint(institucional_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(api_auth_bp)
app.register_blueprint(onboarding_bp)
app.register_blueprint(api_onboarding_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(api_dashboard_bp)
app.register_blueprint(nutricao_bp)
app.register_blueprint(api_nutricao_bp)
app.register_blueprint(checkin_bp)
app.register_blueprint(api_checkin_bp)
app.register_blueprint(treino_bp)
app.register_blueprint(api_treino_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(api_chat_bp)
app.register_blueprint(configuracoes_bp)
app.register_blueprint(api_configuracoes_bp)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.cli.command("init-db")
def init_db():
    db.create_all()
    print("Banco de dados inicializado.")

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

