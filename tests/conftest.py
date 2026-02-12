"""
Pytest fixtures para o Fluir.
Configura banco de testes em memoria antes de importar a aplicacao.
"""
import os
import sys

# Deve rodar ANTES de qualquer import que use database.
# Usa arquivo no diretorio do projeto para que engine e sessions compartilhem o mesmo schema.
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(_root)  # Garante que caminhos relativos funcionem
os.environ["TEST_DATABASE_URL"] = "sqlite:///./test_fluir.db"
os.environ["FLUIR_ADMIN_CODE"] = "test_admin"
os.environ["ADMIN_RECOVERY_EMAIL"] = ""  # Evita seed durante testes

# Garante que o diretorio raiz esteja no path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient

# Import apos configurar env - database usa TEST_DATABASE_URL
from main import app
from database import init_db, SessionLocal, Survey, Respondent, generate_uuid, generate_code


@pytest.fixture(scope="function")
def db():
    """Sessao do banco limpa para cada teste."""
    init_db()
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()




@pytest.fixture
def client(db):
    """TestClient do FastAPI com get_db sobrescrito para usar a sessao de teste."""
    def override_get_db():
        try:
            yield db
        finally:
            pass  # Nao fechamos pois controlamos no fixture

    from main import get_db
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def survey(db):
    """Cria uma pesquisa de teste."""
    s = Survey(
        id=generate_uuid(),
        code=generate_code(),
        company_name="Empresa Teste",
        admin_code="test_admin",
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@pytest.fixture
def survey_with_responses(db, survey):
    """Cria pesquisa com um respondente e respostas completas (1-41)."""
    import json
    responses = {str(i): 3 for i in range(1, 42)}  # Todas com valor 3 (medio)
    r = Respondent(
        id=generate_uuid(),
        survey_id=survey.id,
        display_id="R001",
        responses_json=json.dumps(responses),
    )
    db.add(r)
    db.commit()
    return survey
