import os
import sys
import importlib.util

# Carregar o modulo app a partir do arquivo app.py na raiz
spec = importlib.util.spec_from_file_location("main_app", "app.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["main_app"] = mod
spec.loader.exec_module(mod)
app = mod.app

from app.models import db
from app.models.user import Registro
from app.models.comunidade import Comunidade
from app.models.preferences import Habilidade, Interesse

def get_or_create_tag(model, name):
    tag = model.query.filter_by(nome=name).first()
    if not tag:
        tag = model.query.filter_by(nome=name.lower()).first()
    if not tag:
        tag = model(nome=name)
        db.session.add(tag)
        db.session.commit()
    return tag

def seed():
    with app.app_context():
        # Verificando se existe um criador
        criador = Registro.query.first()
        if not criador:
            print("Criando usuario administrador padrao...")
            criador = Registro(nome="Admin", email="admin@dbqp.com", senha="admin")
            db.session.add(criador)
            db.session.commit()
        
        comunidades_data = [
            {
                "nome": "Java Professionals",
                "descricao": "Espaço para discutir ecossistema Java, Spring Boot, Hibernate e JVM.",
                "habilidades": ["Java", "Spring Boot"],
                "interesses": ["Backend", "Enterprise Architecture"]
            },
            {
                "nome": "C# & .NET Community",
                "descricao": "Tudo sobre .NET, C#, Azure e desenvolvimento de software na stack Microsoft.",
                "habilidades": ["C#", ".NET Core"],
                "interesses": ["Cloud", "Desktop Development"]
            },
            {
                "nome": "C++ Low Level Performance",
                "descricao": "Discussões avançadas sobre C++, Gerenciamento de Memória, Game Dev e Sistemas de Performance.",
                "habilidades": ["C++", "C"],
                "interesses": ["Game Development", "Embedded Systems"]
            },
            {
                "nome": "Modern Web Development",
                "descricao": "Fullstack, Frontend, Backend e as melhores práticas do desenvolvimento Web moderno.",
                "habilidades": ["React", "Node.js", "HTML", "CSS"],
                "interesses": ["Web Design", "UI/UX", "APIs"]
            },
            {
                "nome": "Rustaceans & Memory Safety",
                "descricao": "Voltado para entusiastas de Rust. Segurança de memória sem garbage collector.",
                "habilidades": ["Rust"],
                "interesses": ["Systems Programming", "WebAssembly"]
            }
        ]
        
        for data in comunidades_data:
            existente = Comunidade.query.filter_by(nome=data["nome"]).first()
            if existente:
                print(f"Comunidade '{data['nome']}' ja existe.")
                continue
            
            nova_com = Comunidade(
                nome=data["nome"],
                descricao=data["descricao"],
                criador_id=criador.id
            )
            
            for h_nome in data["habilidades"]:
                nova_com.habilidades.append(get_or_create_tag(Habilidade, h_nome))
            
            for i_nome in data["interesses"]:
                nova_com.interesses.append(get_or_create_tag(Interesse, i_nome))
            
            # Criador vira membro por padrao
            nova_com.membros.append(criador)
            
            db.session.add(nova_com)
            print(f"Criando: {data['nome']}")
        
        db.session.commit()
        print("Finalizado com sucesso!")

if __name__ == "__main__":
    seed()
