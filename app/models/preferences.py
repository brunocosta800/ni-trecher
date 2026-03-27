from . import db

class Habilidade(db.Model):
    __tablename__ = 'lista_habilidades'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)

class Interesse(db.Model):
    __tablename__ = 'lista_interesses'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)