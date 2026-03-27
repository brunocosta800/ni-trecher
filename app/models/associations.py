from . import db

# Tabela de ligação: Usuários <-> Habilidades
user_habilidades = db.Table('user_habilidades',
    db.Column('user_id', db.Integer, db.ForeignKey('registro.id'), primary_key=True),
    db.Column('lista_habilidade_id', db.Integer, db.ForeignKey('lista_habilidades.id'), primary_key=True)
)

# Tabela de ligação: Usuários <-> Interesses
user_interesses = db.Table('user_interesses',
    db.Column('user_id', db.Integer, db.ForeignKey('registro.id'), primary_key=True),
    db.Column('lista_interesse_id', db.Integer, db.ForeignKey('lista_interesses.id'), primary_key=True)
)

# Tabela de ligação: Amizade (Grafo Não Dirigido)
amizades = db.Table('amizades',
    db.Column('user_id', db.Integer, db.ForeignKey('registro.id'), primary_key=True),
    db.Column('amigo_id', db.Integer, db.ForeignKey('registro.id'), primary_key=True)
)


# Tabela de ligação: Comunidade <-> Usuários (Membros)
comunidade_membros = db.Table('comunidade_membros',
    db.Column('user_id', db.Integer, db.ForeignKey('registro.id'), primary_key=True),
    db.Column('comunidade_id', db.Integer, db.ForeignKey('comunidade.id'), primary_key=True)
)

# Tabela de ligação: Comunidade <-> Habilidades (Tags do tópico)
comunidade_habilidades = db.Table('comunidade_habilidades',
    db.Column('comunidade_id', db.Integer, db.ForeignKey('comunidade.id'), primary_key=True),
    db.Column('habilidade_id', db.Integer, db.ForeignKey('lista_habilidades.id'), primary_key=True)
)

# Tabela de ligação: Comunidade <-> Interesses (Tags do tópico)
comunidade_interesses = db.Table('comunidade_interesses',
    db.Column('comunidade_id', db.Integer, db.ForeignKey('comunidade.id'), primary_key=True),
    db.Column('interesse_id', db.Integer, db.ForeignKey('lista_interesses.id'), primary_key=True)
)