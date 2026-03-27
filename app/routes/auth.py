from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db
from app.models.user import Registro, Perfil

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        user = Registro.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.senha, senha):
            session['user_id'] = user.id
            return redirect(url_for('posts.index'))
        else:
            flash('Login inválido. Verifique suas credenciais.', 'error')
            
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        user_exists = Registro.query.filter_by(email=email).first()
        if user_exists:
            flash('Email já cadastrado.', 'error')
            return redirect(url_for('auth.register'))
            
        hashed_password = generate_password_hash(senha)
        new_user = Registro(nome=nome, email=email, senha=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        # Cria perfil vazio
        new_profile = Perfil(user_id=new_user.id)
        db.session.add(new_profile)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))