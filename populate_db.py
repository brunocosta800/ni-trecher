import os
from werkzeug.security import generate_password_hash
import random

# Importações do Flask
import sys
import importlib.util

spec = importlib.util.spec_from_file_location("main_app", "app.py")
main_app = importlib.util.module_from_spec(spec)
sys.modules["main_app"] = main_app
spec.loader.exec_module(main_app)

app = main_app.app
from app.models import db
from app.models.user import Registro, Perfil
from app.models.preferences import Habilidade, Interesse

def populate():
    with app.app_context():
        nomes_falsos = [
            "Lucas Mendes", "Fernanda Costa", "Rafael Lima", "Camila Rocha",
            "Thiago Souza", "Mariana Silva", "Bruno Alves", "Julia Carvalho",
            "Rodrigo Gomes", "Beatriz Santos"
        ]
        
        lista_habilidades = [
            "Python", "JavaScript", "Java", "C++", "C#", "Ruby", "PHP", 
            "Go", "Swift", "Kotlin", "TypeScript", "Rust", "Dart", 
            "React", "Angular", "Vue.js", "Django", "Flask", "Spring Boot", 
            "Node.js", "Express", "Docker", "Kubernetes", "AWS", "Azure",
            "SQL", "NoSQL", "Git", "Linux", "Machine Learning", "Data Science"
        ]
        
        lista_interesses = [
            "Inteligencia Artificial", "Desenvolvimento Web", "Desenvolvimento Mobile",
            "Seguranca da Informacao", "DevOps", "Cloud Computing", "Internet das Coisas",
            "Jogos Digitais", "Realidade Virtual", "Realidade Aumentada",
            "Blockchain", "Criptomoedas", "Big Data", "Data Analytics",
            "UX/UI Design", "Agile", "Scrum", "Empreendedorismo Tech",
            "Open Source", "Arquitetura de Software", "Sistemas Distribuidos"
        ]
        
        # Garante que as habilidades existam
        habilidades_db = {h.nome: h for h in Habilidade.query.all()}
        for hab_nome in lista_habilidades:
            if hab_nome not in habilidades_db:
                nova_hab = Habilidade(nome=hab_nome)
                db.session.add(nova_hab)
                habilidades_db[hab_nome] = nova_hab
                
        # Garante que os interesses existam
        interesses_db = {i.nome: i for i in Interesse.query.all()}
        for int_nome in lista_interesses:
            if int_nome not in interesses_db:
                novo_int = Interesse(nome=int_nome)
                db.session.add(novo_int)
                interesses_db[int_nome] = novo_int
                
        db.session.commit()
        
        count = 0
        hashed_password = generate_password_hash("123456")
        
        for nome in nomes_falsos:
            email = nome.lower().replace(" ", ".") + "@fake.com"
            
            # Checa se já existe
            if Registro.query.filter_by(email=email).first():
                continue
                
            novo_user = Registro(nome=nome, email=email, senha=hashed_password)
            db.session.add(novo_user)
            db.session.flush() # Para pegar o ID
            
            novo_perfil = Perfil(
                user_id=novo_user.id,
                biografia=f"Olá! Sou {nome}, apaixonado por tecnologia.",
                avatar_url=f"https://api.dicebear.com/7.x/avataaars/svg?seed={nome.replace(' ', '')}"
            )
            db.session.add(novo_perfil)
            
            # Randomiza 2 a 5 habilidades e interesses
            num_habs = random.randint(2, 5)
            num_ints = random.randint(2, 5)
            
            habs_escolhidas = random.sample(lista_habilidades, num_habs)
            ints_escolhidos = random.sample(lista_interesses, num_ints)
            
            for h in habs_escolhidas:
                novo_user.habilidades.append(habilidades_db[h])
                
            for i in ints_escolhidos:
                novo_user.interesses.append(interesses_db[i])
                
            count += 1
            
        db.session.commit()
        print(f"Foram criados {count} perfis randomizados na rede!")

if __name__ == "__main__":
    populate()
