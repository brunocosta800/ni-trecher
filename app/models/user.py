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


class Perfil(db.Model):
    __tablename__ = 'perfil'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('registro.id'), unique=True)
    biografia = db.Column(db.Text)
    avatar_url = db.Column(db.String(255), default="/static/default_avatar.png")
    github_url = db.Column(db.String(255))