from . import db
from datetime import datetime
from .associations import comunidade_membros, comunidade_habilidades, comunidade_interesses

class Comunidade(db.Model):
    __tablename__ = 'comunidade'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    descricao = db.Column(db.Text)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    criador_id = db.Column(db.Integer, db.ForeignKey('registro.id'), nullable=False)
    
    criador = db.relationship('Registro', backref='comunidades_criadas')
    membros = db.relationship('Registro', secondary=comunidade_membros, backref='comunidades_inscritas')
    habilidades = db.relationship('Habilidade', secondary=comunidade_habilidades, backref='comunidades')
    interesses = db.relationship('Interesse', secondary=comunidade_interesses, backref='comunidades')

class ComunidadePost(db.Model):
    __tablename__ = 'comunidade_post'
    id = db.Column(db.Integer, primary_key=True)
    conteudo = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('registro.id'), nullable=False)
    comunidade_id = db.Column(db.Integer, db.ForeignKey('comunidade.id'), nullable=False)
    
    autor = db.relationship('Registro', backref='comunidade_posts')
    comunidade = db.relationship('Comunidade', backref=db.backref('posts', lazy='dynamic', cascade='all, delete-orphan'))
