"""
Testes de integracao da API FastAPI.
"""
import pytest
from database import Respondent, Survey, generate_uuid


class TestAdminLogin:
    """Testes do endpoint de login administrativo."""

    def test_login_com_codigo_global(self, client):
        r = client.post("/api/admin/login", json={"admin_code": "test_admin"})
        assert r.status_code == 200
        data = r.json()
        assert data.get("ok") is True
        assert data.get("admin_code") == "test_admin"

    def test_login_invalido_retorna_401(self, client):
        r = client.post("/api/admin/login", json={"admin_code": "codigo_inexistente"})
        assert r.status_code == 401


class TestSurveyCRUD:
    """Testes de criacao, listagem e exclusao de pesquisas."""

    def test_criar_pesquisa(self, client):
        r = client.post("/api/admin/surveys", json={
            "company_name": "Empresa Nova",
            "admin_code": "test_admin",
        })
        assert r.status_code == 200
        data = r.json()
        assert "id" in data
        assert "code" in data
        assert data["company_name"] == "Empresa Nova"

    def test_listar_pesquisas(self, client, survey):
        r = client.get("/api/admin/surveys", params={"admin_code": "test_admin"})
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(s["company_name"] == "Empresa Teste" for s in data)

    def test_obter_pesquisa_por_id(self, client, survey):
        r = client.get(f"/api/admin/surveys/{survey.id}", params={"admin_code": "test_admin"})
        assert r.status_code == 200
        data = r.json()
        assert data["company_name"] == "Empresa Teste"

    def test_excluir_pesquisa(self, client, survey, db):
        survey_id = survey.id
        r = client.post(
            "/api/admin/surveys/delete",
            params={"survey_id": survey_id, "admin_code": "test_admin"},
        )
        assert r.status_code == 200
        assert r.json().get("ok") is True
        # Verifica que a pesquisa foi removida
        db.expire_all()  # Limpa cache para ver estado atual
        remaining = db.query(Survey).filter(Survey.id == survey_id).first()
        assert remaining is None

    def test_excluir_com_admin_global(self, client, db):
        """Exclusao com GLOBAL_ADMIN_CODE deve funcionar."""
        from database import Survey, generate_code
        s = Survey(company_name="Temp", admin_code="outro_codigo", code=generate_code())
        db.add(s)
        db.commit()
        db.refresh(s)
        r = client.post(
            "/api/admin/surveys/delete",
            params={"survey_id": s.id, "admin_code": "test_admin"},
        )
        assert r.status_code == 200

    def test_excluir_pesquisa_paifhoausfh_pelo_card(self, client, db):
        """Teste especifico: excluir pesquisa 'paifhoausfh' atraves do botao do card."""
        from database import Survey, generate_code, generate_uuid
        
        # Cria pesquisa com nome especifico
        survey_paifhoausfh = Survey(
            id=generate_uuid(),
            code=generate_code(),
            company_name="paifhoausfh",
            admin_code="test_admin",
        )
        db.add(survey_paifhoausfh)
        db.commit()
        db.refresh(survey_paifhoausfh)
        survey_id = survey_paifhoausfh.id
        
        # Verifica que a pesquisa existe na listagem
        r_list = client.get("/api/admin/surveys", params={"admin_code": "test_admin"})
        assert r_list.status_code == 200
        surveys_list = r_list.json()
        assert any(s["id"] == survey_id and s["company_name"] == "paifhoausfh" for s in surveys_list)
        
        # Simula clique no botao Excluir do card (chama o endpoint de exclusao)
        r_delete = client.post(
            "/api/admin/surveys/delete",
            params={
                "survey_id": survey_id,
                "admin_code": "test_admin"
            },
        )
        
        # Verifica que a exclusao foi bem-sucedida
        assert r_delete.status_code == 200
        assert r_delete.json().get("ok") is True
        
        # Verifica que a pesquisa foi removida do banco
        db.expire_all()
        remaining = db.query(Survey).filter(Survey.id == survey_id).first()
        assert remaining is None, "Pesquisa 'paifhoausfh' ainda existe no banco apos exclusao"
        
        # Verifica que nao aparece mais na listagem
        r_list_after = client.get("/api/admin/surveys", params={"admin_code": "test_admin"})
        assert r_list_after.status_code == 200
        surveys_list_after = r_list_after.json()
        assert not any(s["id"] == survey_id for s in surveys_list_after), "Pesquisa 'paifhoausfh' ainda aparece na listagem apos exclusao"


class TestSurveySubmit:
    """Testes do envio de respostas pelo respondente."""

    def test_submit_respostas_completas(self, client, survey):
        responses = {str(i): 3 for i in range(1, 42)}
        r = client.post(
            f"/api/survey/{survey.code}/submit",
            json={"responses": responses},
        )
        assert r.status_code == 200
        data = r.json()
        assert data.get("ok") is True
        assert "display_id" in data

    def test_submit_pesquisa_inexistente_404(self, client):
        r = client.post(
            "/api/survey/xxxx9999/submit",
            json={"responses": {str(i): 3 for i in range(1, 42)}},
        )
        assert r.status_code == 404


class TestDashboard:
    """Testes do dashboard administrativo."""

    def test_dashboard_vazio_sem_respondentes(self, client, survey):
        r = client.get(
            f"/api/admin/surveys/{survey.id}/dashboard",
            params={"admin_code": "test_admin"},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["total_respondents"] == 0
        assert data["company_name"] == "Empresa Teste"

    def test_dashboard_com_respondentes(self, client, survey_with_responses):
        r = client.get(
            f"/api/admin/surveys/{survey_with_responses.id}/dashboard",
            params={"admin_code": "test_admin"},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["total_respondents"] >= 1
        assert "dim_scores" in data
        assert "kpis" in data
        assert "recommendations" in data


class TestLandingPage:
    """Testes da pagina de landing."""

    def test_landing_retorna_html_200(self, client):
        """GET /landing deve retornar HTML com status 200."""
        r = client.get("/landing")
        assert r.status_code == 200
        assert "text/html" in r.headers.get("content-type", "")

    def test_landing_contem_headline_fluir(self, client):
        """Pagina de landing deve conter o headline principal."""
        r = client.get("/landing")
        assert r.status_code == 200
        assert "Pesquisa, análise e recomendações em um clique" in r.text


class TestRecoverCode:
    """Testes do endpoint de recuperacao de chave."""

    def test_recover_code_email_nao_cadastrado(self, client):
        """Deve retornar mensagem generica para evitar enumeracao."""
        r = client.post("/api/admin/recover-code", json={"email": "naoexiste@teste.com"})
        assert r.status_code == 200
        assert "message" in r.json()
