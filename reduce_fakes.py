import os
import sys
import importlib.util

spec = importlib.util.spec_from_file_location("main_app", "app.py")
main_app = importlib.util.module_from_spec(spec)
sys.modules["main_app"] = main_app
spec.loader.exec_module(main_app)

app = main_app.app
from app.models import db
from app.models.user import Registro, Perfil

def reduce_fakes():
    with app.app_context():
        # Estes são os 17 nomes originais
        nomes_falsos = [
            "Lucas Mendes", "Fernanda Costa", "Rafael Lima", "Camila Rocha",
            "Thiago Souza", "Mariana Silva", "Bruno Alves", "Julia Carvalho",
            "Rodrigo Gomes", "Beatriz Santos", "Leonardo Ferreira", "Gabriela Ribeiro",
            "Marcelo Martins", "Natalia Pereira", "Felipe Almeida", "Isabela Castro",
            "Gustavo Nogueira"
        ]
        
        # Queremos manter apenas os 10 primeiros
        para_manter = nomes_falsos[:10]
        para_deletar = nomes_falsos[10:]
        
        count = 0
        for nome in para_deletar:
            email = nome.lower().replace(" ", ".") + "@fake.com"
            usuario = Registro.query.filter_by(email=email).first()
            if usuario:
                # O SQLAlchemy apaga em cascata o perfil devido às constraints se configurarmos?
                # Como não temos cascade literal sem backref configurado pra isso, apagamos manual
                if usuario.perfil:
                    db.session.delete(usuario.perfil)
                
                # Desconecta as habilidades e interesses
                usuario.habilidades.clear()
                usuario.interesses.clear()
                
                # E também os posts, se houver
                for post in usuario.posts:
                    db.session.delete(post)
                    
                db.session.delete(usuario)
                count += 1
                
        db.session.commit()
        print(f"Foram deletados {count} perfis falsos. O total agora está em 10.")

if __name__ == "__main__":
    reduce_fakes()
