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
from app.models.post import Post

def test():
    with app.app_context():
        # Clear existing data for fresh test
        db.drop_all()
        db.create_all()
        
        # Cria usuarios
        u1 = Registro(nome="Alice Hacker", email="alice@test.com", senha="123")
        u2 = Registro(nome="Bob Coder", email="bob@test.com", senha="123")
        u3 = Registro(nome="Charlie Dev", email="charlie@test.com", senha="123")
        
        db.session.add_all([u1, u2, u3])
        db.session.commit()
        
        # Cria perfis
        p1 = Perfil(user_id=u1.id, biografia="Python Lover", github_url="https://github.com/alice")
        p2 = Perfil(user_id=u2.id, biografia="React God")
        p3 = Perfil(user_id=u3.id, biografia="DevOps Engineer")
        db.session.add_all([p1, p2, p3])
        db.session.commit()
        
        # Cria habilidades
        python = Habilidade(nome="Python")
        react = Habilidade(nome="React")
        docker = Habilidade(nome="Docker")
        
        u1.habilidades.append(python)
        u1.habilidades.append(react)
        
        u2.habilidades.append(react)
        u2.habilidades.append(docker)
        
        u3.habilidades.append(python)
        u3.habilidades.append(docker)
        
        # Cria posts
        post1 = Post(conteudo="Just learned Python!", user_id=u1.id)
        post2 = Post(conteudo="React is awesome. Change my mind.", user_id=u2.id)
        
        db.session.add_all([python, react, docker, post1, post2])
        db.session.commit()
        
        print("Database populated successfully.")
        
        # Test query
        users = Registro.query.all()
        assert len(users) == 3
        posts = Post.query.all()
        assert len(posts) == 2
        print("All assertions passed!")
        
if __name__ == "__main__":
    test()
