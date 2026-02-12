"""
Testes do modulo database (models, init, utilitarios).
"""
import os
import json
import pytest

# Configura DB de teste antes de importar
os.environ.setdefault("TEST_DATABASE_URL", "sqlite:///./test_fluir.db")

from database import (
    init_db,
    Survey,
    Respondent,
    generate_uuid,
    generate_code,
    SessionLocal,
)


class TestGenerateUtils:
    """Testes das funcoes de geracao de identificadores."""

    def test_generate_uuid_retorna_string_36_chars(self):
        uid = generate_uuid()
        assert isinstance(uid, str)
        assert len(uid) == 36
        assert uid.count("-") == 4

    def test_generate_code_retorna_string_6_chars(self):
        code = generate_code()
        assert isinstance(code, str)
        assert len(code) == 6


class TestModels:
    """Testes dos modelos SQLAlchemy."""

    def test_survey_create(self, db):
        s = Survey(
            company_name="Teste Model",
            admin_code="test",
            code=generate_code(),
        )
        db.add(s)
        db.commit()
        db.refresh(s)
        assert s.id is not None
        assert s.company_name == "Teste Model"

    def test_respondent_responses_property(self, db, survey):
        responses = {"1": 3, "2": 4}
        r = Respondent(
            survey_id=survey.id,
            display_id="R1",
            responses_json=json.dumps(responses),
        )
        db.add(r)
        db.commit()
        db.refresh(r)
        assert r.responses == responses
