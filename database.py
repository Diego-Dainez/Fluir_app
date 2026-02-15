"""
Fluir — Database (SQLAlchemy)
Desenvolvimento/local: SQLite (fluir.db)
Producao (Render): PostgreSQL (dados persistentes entre redeploys)
"""

import os
import uuid
import json
import random
import string
from datetime import datetime, timezone

from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Text, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Permite usar banco em memoria para testes (TEST_DATABASE_URL=sqlite:///:memory:)
# Render injeta DATABASE_URL apontando para PostgreSQL (fromDatabase no render.yaml)
_url = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL", "sqlite:///./fluir.db")
# Render usa postgres:// mas SQLAlchemy aceita; psycopg2 trata ambos
if _url.startswith("postgres://"):
    _url = _url.replace("postgres://", "postgresql://", 1)
_connect_args = {} if "sqlite" in _url else {}
if "sqlite" in _url:
    _connect_args["check_same_thread"] = False
engine = create_engine(_url, connect_args=_connect_args)
DATABASE_URL = _url
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


def generate_code(length=6):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


# ───── Models ─────

class Survey(Base):
    __tablename__ = "surveys"

    id = Column(String, primary_key=True, default=generate_uuid)
    code = Column(String(8), unique=True, nullable=False, default=generate_code)
    company_name = Column(String(200), nullable=False, default="Empresa")
    admin_code = Column(String(50), nullable=False, default="/admin")
    thank_you_title = Column(String(200), default="Obrigado pela sua participação!")
    thank_you_message = Column(Text, default="Suas respostas foram registradas com sucesso. Elas são anônimas e confidenciais, e contribuirão para melhorar o ambiente de trabalho.")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    respondents = relationship("Respondent", back_populates="survey", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="survey", cascade="all, delete-orphan")


class Respondent(Base):
    __tablename__ = "respondents"

    id = Column(String, primary_key=True, default=generate_uuid)
    survey_id = Column(String, ForeignKey("surveys.id"), nullable=False)
    display_id = Column(String(10), nullable=False)
    responses_json = Column(Text, nullable=False)   # JSON: {"1": 3, "2": 4, ...}
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    survey = relationship("Survey", back_populates="respondents")

    @property
    def responses(self):
        return json.loads(self.responses_json) if self.responses_json else {}

    @responses.setter
    def responses(self, value):
        self.responses_json = json.dumps(value)


class AdminRecoveryEmail(Base):
    """Emails autorizados a receber a chave de acesso (recuperacao)."""
    __tablename__ = "admin_recovery_emails"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String, primary_key=True, default=generate_uuid)
    survey_id = Column(String, ForeignKey("surveys.id"), nullable=False)
    dimension_ids = Column(String(500), nullable=False)   # comma-separated
    priority = Column(String(20), nullable=False)         # imediata, curto, medio
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=False)
    is_custom = Column(Boolean, default=False)
    order_index = Column(Integer, default=0)

    survey = relationship("Survey", back_populates="recommendations")


# ───── Init ─────

def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
