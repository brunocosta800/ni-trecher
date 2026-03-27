# Imports externos
import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

# Imports internos
from app.models import db, init_models
from app.routes.auth import auth_bp
from app.routes.posts import posts_bp
from app.routes.users import users_bp
from app.routes.communities import communities_bp

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.secret_key = os.getenv('SECRET_KEY', 'dev_secret_key_123')
load_dotenv()

# Configuracoes banco de dados
host = os.getenv('host')
user = os.getenv('user')
password = os.getenv('password')
port = os.getenv('port')
banco = os.getenv('banco')

banco_uri = os.getenv('DATABASE_URI')
if banco_uri:
    app.config['SQLALCHEMY_DATABASE_URI'] = banco_uri
elif host and user and banco:
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{user}:{password}@{host}/{banco}"
else:
    # Fallback to sqlite for local dev testing
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa o banco com a estrutura modular
init_models(app)

with app.app_context():
    db.create_all()

# Registro de blueprints Flask
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(posts_bp, url_prefix='/posts')
app.register_blueprint(users_bp, url_prefix='/users')
app.register_blueprint(communities_bp, url_prefix='/communities')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)