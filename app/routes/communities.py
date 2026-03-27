from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import db
from app.models.user import Registro
from app.models.comunidade import Comunidade, ComunidadePost
from app.models.preferences import Habilidade, Interesse

communities_bp = Blueprint('communities', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@communities_bp.route('/')
@login_required
def list_communities():
    user = Registro.query.get(session['user_id'])
    minhas_comunidades = user.comunidades_inscritas
    
    # Criando o sistema de recomendação visualizando sobreposição de tags
    todas_comunidades = Comunidade.query.all()
    
    # Exclui comunidades que eu já estou
    sugeridas = []
    meus_interesses = set([i.nome for i in user.interesses])
    minhas_habilidades = set([h.nome for h in user.habilidades])
    
    for com in todas_comunidades:
        if com not in minhas_comunidades:
            tags_com_interesses = set([i.nome for i in com.interesses])
            tags_com_habilidades = set([h.nome for h in com.habilidades])
            
            # Conta intersecções
            over_int = meus_interesses.intersection(tags_com_interesses)
            over_hab = minhas_habilidades.intersection(tags_com_habilidades)
            score = len(over_int) + len(over_hab)
            
            sugeridas.append((score, com))
            
    # Ordena pelo score decrescente
    sugeridas.sort(key=lambda x: x[0], reverse=True)
    
    # Separa recomendadas (score > 0) de todas as outras
    recomendadas = [s[1] for s in sugeridas if s[0] > 0]
    outras = [s[1] for s in sugeridas if s[0] == 0]
    
    return render_template('communities_list.html', 
                           minhas_comunidades=minhas_comunidades, 
                           recomendadas=recomendadas,
                           outras=outras,
                           meus_interesses=meus_interesses,
                           minhas_habilidades=minhas_habilidades)

@communities_bp.route('/create', methods=['POST'])
@login_required
def create_community():
    nome = request.form.get('nome')
    descricao = request.form.get('descricao')
    tags = request.form.get('tags', '')
    
    if not nome:
        flash('O nome da comunidade é obrigatório!', 'error')
        return redirect(url_for('communities.list_communities'))
        
    nova_comunidade = Comunidade(nome=nome, descricao=descricao, criador_id=session['user_id'])
    
    # Trata tags simplificadamente como habilidades/interesses misturados
    tags_list = [t.strip() for t in tags.split(',') if t.strip()]
    for t_nome in tags_list:
        # Tenta achar em Habilidade
        hab = Habilidade.query.filter_by(nome=t_nome).first()
        if hab:
            nova_comunidade.habilidades.append(hab)
            continue
            
        # Tenta achar em Interesse ou cria em Interesse
        inter = Interesse.query.filter_by(nome=t_nome).first()
        if not inter:
            inter = Interesse(nome=t_nome)
            db.session.add(inter)
        nova_comunidade.interesses.append(inter)
        
    # Adiciona o próprio criador como membro
    user = Registro.query.get(session['user_id'])
    nova_comunidade.membros.append(user)
    
    db.session.add(nova_comunidade)
    db.session.commit()
    
    flash('Comunidade criada com sucesso!', 'success')
    return redirect(url_for('communities.view_community', id=nova_comunidade.id))

@communities_bp.route('/<int:id>')
@login_required
def view_community(id):
    comunidade = Comunidade.query.get_or_404(id)
    user = Registro.query.get(session['user_id'])
    is_member = user in comunidade.membros
    
    posts = comunidade.posts.order_by(ComunidadePost.data_criacao.desc()).all()
    
    return render_template('community_view.html', comunidade=comunidade, posts=posts, is_member=is_member)

@communities_bp.route('/<int:id>/join', methods=['POST'])
@login_required
def join_community(id):
    comunidade = Comunidade.query.get_or_404(id)
    user = Registro.query.get(session['user_id'])
    
    if user not in comunidade.membros:
        comunidade.membros.append(user)
        db.session.commit()
        flash(f'Você entrou em {comunidade.nome}!', 'success')
    else:
        comunidade.membros.remove(user)
        db.session.commit()
        flash(f'Você saiu de {comunidade.nome}.', 'success')
        
    return redirect(url_for('communities.view_community', id=id))

@communities_bp.route('/<int:id>/post', methods=['POST'])
@login_required
def post_community(id):
    comunidade = Comunidade.query.get_or_404(id)
    user = Registro.query.get(session['user_id'])
    conteudo = request.form.get('conteudo')
    
    if user not in comunidade.membros:
        flash('Você precisa ser um membro para postar nesta comunidade.', 'error')
        return redirect(url_for('communities.view_community', id=id))
        
    if conteudo and conteudo.strip():
        novo_post = ComunidadePost(conteudo=conteudo, user_id=user.id, comunidade_id=comunidade.id)
        db.session.add(novo_post)
        db.session.commit()
        
    return redirect(url_for('communities.view_community', id=id))
