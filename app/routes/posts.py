from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import db
from app.models.post import Post
from app.models.user import Registro

posts_bp = Blueprint('posts', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@posts_bp.route('/')
@login_required
def index():
    # Obtém posts ordenados do mais recente para o mais antigo
    posts = Post.query.order_by(Post.data_criacao.desc()).all()
    user_id = session.get('user_id')
    user = Registro.query.get(user_id)
    return render_template('feed.html', posts=posts, current_user=user)

@posts_bp.route('/create', methods=['POST'])
@login_required
def create_post():
    conteudo = request.form.get('conteudo')
    if not conteudo:
        flash('O conteúdo do post não pode estar vazio.', 'error')
        return redirect(url_for('posts.index'))
    
    user_id = session['user_id']
    new_post = Post(conteudo=conteudo, user_id=user_id)
    db.session.add(new_post)
    db.session.commit()
    return redirect(url_for('posts.index'))