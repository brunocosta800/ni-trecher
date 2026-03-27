import os
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash, current_app
from werkzeug.utils import secure_filename
from app.models import db
from app.models.user import Registro, Perfil, SolicitacaoAmizade
from app.models.preferences import Habilidade, Interesse

users_bp = Blueprint('users', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@users_bp.route('/profile')
@login_required
def profile():
    user = Registro.query.get(session['user_id'])
    return render_template('view_profile.html', user=user, Registro=Registro)


@users_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = Registro.query.get(session['user_id'])
    
    if request.method == 'POST':
        biografia = request.form.get('biografia', '')
        github_url = request.form.get('github_url', '')
        
        # Atualiza o perfil básico
        perfil = user.perfil
        if not perfil:
            perfil = Perfil(user_id=user.id)
            db.session.add(perfil)
            
        avatar_file = request.files.get('avatar')
        if avatar_file and avatar_file.filename != '':
            filename = secure_filename(avatar_file.filename)
            
            # Garante que a imagem seja salva na pasta app/static já existente
            static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
            uploads_dir = os.path.join(static_dir, 'uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            
            file_path = os.path.join(uploads_dir, filename)
            avatar_file.save(file_path)
            perfil.avatar_url = f"/static/uploads/{filename}"
        elif not perfil.avatar_url:
            perfil.avatar_url = "/static/default_avatar.png"
            
        perfil.biografia = biografia
        perfil.github_url = github_url
        
        # Atualiza Habilidades (separadas por vírgula)
        habilidades_str = request.form.get('habilidades', '')
        habilidades_nomes = [h.strip() for h in habilidades_str.split(',') if h.strip()]
        
        user.habilidades = []
        for h_nome in habilidades_nomes:
            hab = Habilidade.query.filter_by(nome=h_nome).first()
            if not hab:
                hab = Habilidade(nome=h_nome)
                db.session.add(hab)
            user.habilidades.append(hab)
            
        # Atualiza Interesses (separadas por vírgula)
        interesses_str = request.form.get('interesses', '')
        interesses_nomes = [i.strip() for i in interesses_str.split(',') if i.strip()]
        
        user.interesses = []
        for i_nome in interesses_nomes:
            int_obj = Interesse.query.filter_by(nome=i_nome).first()
            if not int_obj:
                int_obj = Interesse(nome=i_nome)
                db.session.add(int_obj)
            user.interesses.append(int_obj)
            
        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('users.profile'))
        
    return render_template('profile.html', user=user)

@users_bp.route('/profile/<int:user_id>')
@login_required
def view_profile(user_id):
    if user_id == session['user_id']:
        return redirect(url_for('users.profile'))
    
    user = Registro.query.get_or_404(user_id)
    current_user = Registro.query.get(session['user_id'])
    is_following = user in current_user.amigos
    is_friend = current_user in user.amigos and is_following
    
    # Verifica se há solicitação pendente enviada pelo usuário logado para este perfil
    has_pending_request = SolicitacaoAmizade.query.filter_by(
        remetente_id=current_user.id, 
        destinatario_id=user_id, 
        status='pendente'
    ).first() is not None
    
    return render_template('view_profile.html', user=user, is_following=is_following, is_friend=is_friend, has_pending_request=has_pending_request, Registro=Registro)


@users_bp.route('/follow/<int:user_id>')
@login_required
def follow(user_id):
    current_user = Registro.query.get(session['user_id'])
    target_user = Registro.query.get_or_404(user_id)
    
    if target_user not in current_user.amigos:
        current_user.amigos.append(target_user)
        db.session.commit()
        flash(f'Agora você segue {target_user.nome}!', 'success')
    else:
        current_user.amigos.remove(target_user)
        db.session.commit()
        flash(f'Você deixou de seguir {target_user.nome}.', 'info')
        
    return redirect(url_for('users.view_profile', user_id=user_id))


@users_bp.route('/friend_request/send/<int:user_id>')
@login_required
def send_request(user_id):
    current_user_id = session['user_id']
    if current_user_id == user_id:
        flash("Você não pode enviar solicitação para si mesmo.", "warning")
        return redirect(url_for('users.profile'))
    
    # Verifica se já existe solicitação pendente ou se já são amigos mútuos
    existing_request = SolicitacaoAmizade.query.filter(
        ((SolicitacaoAmizade.remetente_id == current_user_id) & (SolicitacaoAmizade.destinatario_id == user_id)) |
        ((SolicitacaoAmizade.remetente_id == user_id) & (SolicitacaoAmizade.destinatario_id == current_user_id))
    ).filter(SolicitacaoAmizade.status == 'pendente').first()
    
    if existing_request:
        flash("Já existe uma solicitação pendente entre vocês.", "info")
        return redirect(url_for('users.view_profile', user_id=user_id))
    
    new_request = SolicitacaoAmizade(remetente_id=current_user_id, destinatario_id=user_id)
    db.session.add(new_request)
    db.session.commit()
    flash("Solicitação de amizade enviada!", "success")
    return redirect(url_for('users.view_profile', user_id=user_id))


@users_bp.route('/friend_request/accept/<int:request_id>')
@login_required
def accept_request(request_id):
    req = SolicitacaoAmizade.query.get_or_404(request_id)
    if req.destinatario_id != session['user_id']:
        flash("Permissão negada.", "danger")
        return redirect(url_for('users.profile'))
    
    req.status = 'aceita'
    
    # Estabelece a amizade mútua (ambos se seguem)
    remetente = Registro.query.get(req.remetente_id)
    destinatario = Registro.query.get(req.destinatario_id)
    
    if destinatario not in remetente.amigos:
        remetente.amigos.append(destinatario)
    if remetente not in destinatario.amigos:
        destinatario.amigos.append(remetente)
        
    db.session.commit()
    flash(f"Agora você e {remetente.nome} são amigos!", "success")
    return redirect(url_for('users.friend_requests'))


@users_bp.route('/friend_request/reject/<int:request_id>')
@login_required
def reject_request(request_id):
    req = SolicitacaoAmizade.query.get_or_404(request_id)
    if req.destinatario_id != session['user_id']:
        flash("Permissão negada.", "danger")
        return redirect(url_for('users.profile'))
    
    req.status = 'recusada'
    db.session.commit()
    flash("Solicitação recusada.", "info")
    return redirect(url_for('users.friend_requests'))


@users_bp.route('/friend_requests')
@login_required
def friend_requests():
    user = Registro.query.get(session['user_id'])
    pendentes = user.solicitacoes_recebidas.filter_by(status='pendente').all()
    return render_template('friend_requests.html', pendentes=pendentes)

@users_bp.route('/network/analysis')
@login_required
def network_analysis():
    from app.utils.graph_utils import bfs_distance, suggest_friends_of_friends, dijkstra_interest_distance, find_communities, who_can_help, get_graph
    
    current_user_id = session['user_id']
    all_users = Registro.query.all()
    user = Registro.query.get(current_user_id)
    graph = get_graph(all_users)
    
    # 1. Sugestões de amigos de amigos
    fof_suggestions_ids = suggest_friends_of_friends(graph, current_user_id)
    fof_suggestions = [Registro.query.get(sid) for sid in fof_suggestions_ids[:5]]
    
    # 2. Comunidades (DFS)
    communities = find_communities(all_users)
    user_community = next((comm for comm in communities if current_user_id in comm), [])
    community_members = [Registro.query.get(uid) for uid in user_community]
    
    # 3. Quem pode ajudar (BFS 3 graus)
    skill_query = request.args.get('skill', '')
    helpers = []
    if skill_query:
        helper_results = who_can_help(all_users, current_user_id, skill_query)
        helpers = [(Registro.query.get(uid), dist) for uid, dist in helper_results]

    return render_template('network_analysis.html', 
                           fof_suggestions=fof_suggestions,
                           community_members=community_members,
                           helpers=helpers,
                           skill_query=skill_query,
                           all_users=all_users,
                           bfs_distance=bfs_distance,
                           dijkstra_interest_distance=dijkstra_interest_distance,
                           graph=graph,
                           current_user=user,
                           float=float)


@users_bp.route('/network')
@login_required
def network():
    user = Registro.query.get(session['user_id'])
    return render_template('network.html', current_user=user)

@users_bp.route('/api/network_data')
@login_required
def network_data():
    current_user_id = session['user_id']
    all_users = Registro.query.all()
    
    nodes = []
    edges = []
    
    # Mapeamento para evitar duplicidade de arestas de similaridade
    similarity_edges = set()
    
    for i, u in enumerate(all_users):
        nodes.append({
            "id": u.id,
            "label": u.nome,
            "title": f"Habilidades: {', '.join([h.nome for h in u.habilidades])}\\nInteresses: {', '.join([i.nome for i in u.interesses])}",
            "group": 1 if u.id == current_user_id else 2,
            "shape": "dot"
        })
        
        # 1. Conexões explícitas (Seguindo)
        for amigo in u.amigos:
            is_mine = (u.id == current_user_id or amigo.id == current_user_id)
            edges.append({
                "from": u.id,
                "to": amigo.id,
                "arrows": "to",
                "label": "segue",
                "color": "#47D15A" if is_mine else "rgba(71, 209, 90, 0.2)",
                "width": 3 if is_mine else 1,
                "title": f"{u.nome} segue {amigo.nome}",
                "font": {"size": 10, "color": "#47D15A" if is_mine else "rgba(255,255,255,0.2)"}
            })
            
        # 2. Conexões por Similaridade (Habilidades/Interesses em comum)
        for j in range(i + 1, len(all_users)):
            u2 = all_users[j]
            
            shared_hab = set(h.nome for h in u.habilidades) & set(h.nome for h in u2.habilidades)
            shared_int = set(i.nome for i in u.interesses) & set(i.nome for i in u2.interesses)
            
            weight = len(shared_hab) + len(shared_int)
            
            if weight > 0:
                is_mine = (u.id == current_user_id or u2.id == current_user_id)
                titles = []
                if shared_hab: titles.append(f"Hab: {', '.join(shared_hab)}")
                if shared_int: titles.append(f"Int: {', '.join(shared_int)}")
                
                label_text = f"{weight} tags comum"
                
                edges.append({
                    "from": u.id,
                    "to": u2.id,
                    "value": weight,
                    "title": " | ".join(titles),
                    "label": label_text if is_mine else "",
                    "color": "rgba(255, 215, 0, 0.8)" if is_mine else "rgba(255, 215, 0, 0.1)",
                    "width": 2 if is_mine else 1,
                    "font": {"size": 10, "color": "gold" if is_mine else "rgba(255,255,255,0.1)"}
                })
                
    return jsonify({"nodes": nodes, "edges": edges})
