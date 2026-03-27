from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_models(app):
    db.init_app(app)
    # Importar as classes para o SQLAlchemy mapear
    from .user import Registro, Perfil, SolicitacaoAmizade
    from .preferences import Habilidade, Interesse
    from .post import Post
    from .comunidade import Comunidade, ComunidadePost