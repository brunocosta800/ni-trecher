from . import db
from .associations import user_habilidades, user_interesses, amizades

class Registro(db.Model):
    __tablename__ = 'registro'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    
    habilidades = db.relationship('Habilidade', secondary=user_habilidades, backref='usuarios')
    interesses = db.relationship('Interesse', secondary=user_interesses, backref='usuarios')
    
    # Relacionamento de Amizade (Grafo Não Dirigido)
    amigos = db.relationship(
        'Registro', secondary=amizades,
        primaryjoin=(amizades.c.user_id == id),
        secondaryjoin=(amizades.c.amigo_id == id),
        backref=db.backref('amigo_de', lazy='dynamic'),
        lazy='dynamic'
    )
    
    perfil = db.relationship('Perfil', backref='user_registro', uselist=False)
    
    # Solicitações de amizade enviadas e recebidas
    solicitacoes_enviadas = db.relationship(
        'SolicitacaoAmizade', 
        foreign_keys='SolicitacaoAmizade.remetente_id',
        backref='remetente', lazy='dynamic'
    )
    solicitacoes_recebidas = db.relationship(
        'SolicitacaoAmizade', 
        foreign_keys='SolicitacaoAmizade.destinatario_id',
        backref='destinatario', lazy='dynamic'
    )


class Perfil(db.Model):
    __tablename__ = 'perfil'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('registro.id'), unique=True)
    biografia = db.Column(db.Text)
    avatar_url = db.Column(db.String(255), default="/static/default_avatar.png")
    github_url = db.Column(db.String(255))


class SolicitacaoAmizade(db.Model):
    __tablename__ = 'solicitacao_amizade'
    id = db.Column(db.Integer, primary_key=True)
    remetente_id = db.Column(db.Integer, db.ForeignKey('registro.id'), nullable=False)
    destinatario_id = db.Column(db.Integer, db.ForeignKey('registro.id'), nullable=False)
    status = db.Column(db.String(20), default='pendente') # 'pendente', 'aceita', 'recusada'