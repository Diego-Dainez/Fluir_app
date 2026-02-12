"""
Fluir — Backend FastAPI
Bem-estar que move resultados
"""

import io
import json
import os
import smtplib
import base64
import uuid
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import qrcode
from pydantic import BaseModel, Field
from collections import defaultdict
from typing import Dict, List, Optional

from database import init_db, get_db, SessionLocal, Survey, Respondent, Recommendation, AdminRecoveryEmail, generate_uuid, generate_code
from copsoq_data import QUESTIONS, DIMENSIONS, CATEGORIES, SCALE_LABELS
from copsoq_calculator import calc_dimension_scores, calc_kpis, calc_summary, get_status
from recommendations_engine import generate_recommendations
from export_service import export_excel, export_pptx
from gemini_prose_service import generate_recommendations_prose

EXPECTED_QUESTIONS = len(QUESTIONS)

# ────── App ──────

app = FastAPI(title="Fluir", description="Bem-estar que move resultados", version="1.0.0")
_cors_origins = os.getenv("CORS_ORIGINS", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins.split(",") if _cors_origins != "*" else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

static_path = Path(__file__).parent / "static"
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

init_db()


def _seed_recovery_email_if_configured():
    """Insere email de recuperacao a partir de ADMIN_RECOVERY_EMAIL se a tabela estiver vazia."""
    email = os.getenv("ADMIN_RECOVERY_EMAIL", "").strip().lower()
    if not email:
        return
    db = SessionLocal()
    try:
        existing = db.query(AdminRecoveryEmail).filter(AdminRecoveryEmail.email == email).first()
        if not existing:
            rec = AdminRecoveryEmail(email=email)
            db.add(rec)
            db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


_seed_recovery_email_if_configured()


# ────── Pydantic Models ──────

class AdminLogin(BaseModel):
    admin_code: str

class SurveyCreate(BaseModel):
    company_name: str = Field(..., max_length=200)
    admin_code: str = Field(default="fluir2026", max_length=50)

class SurveySettings(BaseModel):
    thank_you_title: Optional[str] = None
    thank_you_message: Optional[str] = None
    is_active: Optional[bool] = None
    company_name: Optional[str] = None

class SubmitAnswers(BaseModel):
    responses: Dict[str, int]

class RecoverCodeRequest(BaseModel):
    email: str = Field(..., max_length=255)


# ════════════════════════════════════════════
# PAGE ROUTES
# ════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def root():
    return (static_path / "login.html").read_text(encoding="utf-8")

@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    return (static_path / "admin.html").read_text(encoding="utf-8")

@app.get("/survey/{code}", response_class=HTMLResponse)
async def survey_page(code: str, db: Session = Depends(get_db)):
    survey = db.query(Survey).filter(Survey.code == code).first()
    if not survey or not survey.is_active:
        raise HTTPException(404, "Pesquisa não encontrada ou encerrada.")
    return (static_path / "survey.html").read_text(encoding="utf-8")


# ════════════════════════════════════════════
# ADMIN API
# ════════════════════════════════════════════

GLOBAL_ADMIN_CODE = os.getenv("FLUIR_ADMIN_CODE", "fluir2026")

@app.post("/api/admin/login")
def admin_login(body: AdminLogin, db: Session = Depends(get_db)):
    # Accept global admin code OR any code that matches existing surveys
    surveys = db.query(Survey).filter(Survey.admin_code == body.admin_code).all()
    if body.admin_code != GLOBAL_ADMIN_CODE and not surveys:
        raise HTTPException(401, "Codigo de acesso invalido.")
    return {"ok": True, "admin_code": body.admin_code, "surveys": [_survey_brief(s, db) for s in surveys]}


@app.post("/api/admin/recover-code")
def recover_code(body: RecoverCodeRequest, db: Session = Depends(get_db)):
    """Envia a chave de acesso para o email se estiver cadastrado. Resposta generica para evitar enumeracao."""
    email = body.email.strip().lower()
    if not email:
        return {"message": "Se o email estiver cadastrado, voce recebera a chave em instantes."}

    exists = db.query(AdminRecoveryEmail).filter(AdminRecoveryEmail.email == email).first()
    if not exists:
        return {"message": "Se o email estiver cadastrado, voce recebera a chave em instantes."}

    admin_code = os.getenv("FLUIR_ADMIN_CODE", "fluir2026")
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    smtp_from = os.getenv("SMTP_FROM") or smtp_user

    if not smtp_host or not smtp_user or not smtp_pass:
        return {"message": "Se o email estiver cadastrado, voce recebera a chave em instantes."}

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Fluir - Recuperacao de chave de acesso"
        msg["From"] = smtp_from
        msg["To"] = email
        text = f"""Fluir - Bem-estar que move resultados

Sua chave de acesso administrativo: {admin_code}

Guarde esta informacao em local seguro. Nao compartilhe com terceiros."""
        msg.attach(MIMEText(text, "plain", "utf-8"))
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_from, email, msg.as_string())
    except Exception:
        pass

    return {"message": "Se o email estiver cadastrado, voce recebera a chave em instantes."}


@app.post("/api/admin/surveys")
def create_survey(body: SurveyCreate, db: Session = Depends(get_db)):
    max_retries = 5
    for attempt in range(max_retries):
        survey = Survey(
            id=generate_uuid(),
            code=generate_code(),
            company_name=body.company_name,
            admin_code=body.admin_code,
        )
        db.add(survey)
        try:
            db.commit()
            db.refresh(survey)
            return _survey_brief(survey, db)
        except IntegrityError:
            db.rollback()
            if attempt == max_retries - 1:
                raise HTTPException(500, "Codigo de pesquisa em conflito. Tente novamente.")


@app.get("/api/admin/surveys")
def list_surveys(admin_code: str = Query(...), db: Session = Depends(get_db)):
    surveys = db.query(Survey).filter(Survey.admin_code == admin_code).all()
    return [_survey_brief(s, db) for s in surveys]


@app.post("/api/admin/surveys/delete")
def delete_survey(survey_id: str = Query(...), admin_code: str = Query(...), db: Session = Depends(get_db)):
    """Exclui permanentemente a pesquisa e todos os dados (respondentes, recomendacoes)."""
    survey = _get_survey_auth(survey_id, admin_code, db)
    db.delete(survey)
    db.commit()
    return {"ok": True}


@app.get("/api/admin/surveys/{survey_id}")
def get_survey(survey_id: str, admin_code: str = Query(...), db: Session = Depends(get_db)):
    survey = _get_survey_auth(survey_id, admin_code, db)
    return _survey_detail(survey, db)


@app.put("/api/admin/surveys/{survey_id}/settings")
def update_settings(survey_id: str, body: SurveySettings, admin_code: str = Query(...), db: Session = Depends(get_db)):
    survey = _get_survey_auth(survey_id, admin_code, db)
    if body.thank_you_title is not None:
        survey.thank_you_title = body.thank_you_title
    if body.thank_you_message is not None:
        survey.thank_you_message = body.thank_you_message
    if body.is_active is not None:
        survey.is_active = body.is_active
    if body.company_name is not None:
        survey.company_name = body.company_name
    db.commit()
    return {"ok": True}


@app.get("/api/admin/surveys/{survey_id}/responses")
def get_responses(survey_id: str, admin_code: str = Query(...), db: Session = Depends(get_db)):
    survey = _get_survey_auth(survey_id, admin_code, db)
    respondents = db.query(Respondent).filter(Respondent.survey_id == survey_id).order_by(Respondent.submitted_at).all()
    result = []
    for r in respondents:
        responses = {int(k): int(v) for k, v in r.responses.items()}
        dim_scores = calc_dimension_scores(responses)
        scores_map = {d["dimension_id"]: d["score"] for d in dim_scores}
        statuses_map = {d["dimension_id"]: d["status"] for d in dim_scores}
        result.append({
            "display_id": r.display_id,
            "submitted_at": r.submitted_at.isoformat() if r.submitted_at else None,
            "scores": scores_map,
            "statuses": statuses_map,
        })
    return result


@app.get("/api/admin/surveys/{survey_id}/dashboard")
def get_dashboard(survey_id: str, admin_code: str = Query(...), db: Session = Depends(get_db)):
    survey = _get_survey_auth(survey_id, admin_code, db)
    respondents = db.query(Respondent).filter(Respondent.survey_id == survey_id).all()

    if not respondents:
        return {
            "company_name": survey.company_name,
            "total_respondents": 0,
            "dim_scores": [],
            "kpis": {},
            "summary": {},
            "recommendations": [],
            "recommendations_prose": {
                "imediata": "",
                "curto_prazo": "",
                "medio_prazo": "",
            },
            "respondents": [],
        }

    # Aggregate scores e dados por respondente (para tabela transposta)
    all_dim_scores = []
    respondents_data = []
    for r in respondents:
        responses = {int(k): int(v) for k, v in r.responses.items()}
        ds = calc_dimension_scores(responses)
        all_dim_scores.append(ds)
        respondents_data.append({
            "display_id": r.display_id,
            "scores": {d["dimension_id"]: d["score"] for d in ds},
            "statuses": {d["dimension_id"]: d["status"] for d in ds},
        })

    agg = _aggregate_dim_scores(all_dim_scores)
    kpis = calc_kpis(agg)
    summary = calc_summary(agg)
    summary["total_respondents"] = len(respondents)

    # Recommendations
    existing_recs = db.query(Recommendation).filter(Recommendation.survey_id == survey_id).order_by(Recommendation.order_index).all()
    if existing_recs:
        recs = [{"id": r.id, "dimension_ids": r.dimension_ids, "priority": r.priority, "title": r.title, "description": r.description, "is_custom": r.is_custom, "order_index": r.order_index} for r in existing_recs]
    else:
        recs = generate_recommendations(agg)
        for i, rec in enumerate(recs):
            db_rec = Recommendation(id=generate_uuid(), survey_id=survey_id, dimension_ids=rec["dimension_ids"], priority=rec["priority"], title=rec["title"], description=rec["description"], is_custom=False, order_index=i)
            db.add(db_rec)
            rec["id"] = db_rec.id
            rec["order_index"] = i
        db.commit()

    # Gera texto corrido consultivo (IA) a partir das recomendacoes estruturadas.
    recommendations_prose = generate_recommendations_prose(recs)

    return {
        "company_name": survey.company_name,
        "total_respondents": len(respondents),
        "dim_scores": agg,
        "kpis": kpis,
        "summary": summary,
        "recommendations": recs,
        "recommendations_prose": recommendations_prose,
        "respondents": respondents_data,
    }


@app.get("/api/admin/surveys/{survey_id}/qrcode")
def get_qrcode(survey_id: str, admin_code: str = Query(...), base_url: str = Query("http://localhost:8000"), db: Session = Depends(get_db)):
    survey = _get_survey_auth(survey_id, admin_code, db)
    url = f"{base_url}/survey/{survey.code}"
    img = qrcode.make(url, box_size=8, border=2)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    return {"qr_base64": f"data:image/png;base64,{b64}", "survey_url": url}


@app.get("/api/admin/surveys/{survey_id}/export/excel")
def export_excel_endpoint(survey_id: str, admin_code: str = Query(...), db: Session = Depends(get_db)):
    survey = _get_survey_auth(survey_id, admin_code, db)
    data = _get_export_data(survey, db)
    # Para o Excel mantemos o detalhamento das recomendacoes em lista estruturada.
    buf = export_excel(
        survey={"company_name": survey.company_name},
        respondents_data=data["respondents_data"],
        dim_scores_agg=data["dim_scores"],
        kpis=data["kpis"],
        summary=data["summary"],
        recommendations=data["recommendations"],
    )
    return StreamingResponse(buf, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": f'attachment; filename="fluir_{survey.company_name}_{datetime.now().strftime("%Y%m%d")}.xlsx"'})


@app.get("/api/admin/surveys/{survey_id}/export/pptx")
def export_pptx_endpoint(survey_id: str, admin_code: str = Query(...), db: Session = Depends(get_db)):
    """Gera relatorio em PowerPoint (.pptx) com a analise e recomendacoes em prosa."""
    survey = _get_survey_auth(survey_id, admin_code, db)
    data = _get_export_data(survey, db)
    recommendations_prose = generate_recommendations_prose(data["recommendations"])
    buf = export_pptx(
        survey={"company_name": survey.company_name},
        dim_scores_agg=data["dim_scores"],
        kpis=data["kpis"],
        summary=data["summary"],
        recommendations_prose=recommendations_prose,
    )
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f'attachment; filename="fluir_{survey.company_name}_{datetime.now().strftime("%Y%m%d")}.pptx"'},
    )


# ════════════════════════════════════════════
# SURVEY API (respondent-facing)
# ════════════════════════════════════════════

@app.get("/api/survey/{code}/info")
def survey_info(code: str, db: Session = Depends(get_db)):
    survey = db.query(Survey).filter(Survey.code == code, Survey.is_active == True).first()
    if not survey:
        raise HTTPException(404, "Pesquisa não encontrada ou encerrada.")
    return {"company_name": survey.company_name, "code": survey.code}


@app.get("/api/survey/{code}/questions")
def survey_questions(code: str, db: Session = Depends(get_db)):
    survey = db.query(Survey).filter(Survey.code == code, Survey.is_active == True).first()
    if not survey:
        raise HTTPException(404, "Pesquisa não encontrada ou encerrada.")
    pages = []
    for cat in CATEGORIES:
        questions = []
        for q_id in cat["questions"]:
            q = QUESTIONS[q_id]
            scale = SCALE_LABELS[q["scale"]]
            questions.append({"id": q_id, "text": q["text"], "scale_labels": scale})
        pages.append({
            "id": cat["id"],
            "name": cat["name"],
            "icon": cat["icon"],
            "description": cat["description"],
            "color": cat["color"],
            "questions": questions,
        })
    return pages


@app.post("/api/survey/{code}/submit")
def submit_survey(code: str, body: SubmitAnswers, db: Session = Depends(get_db)):
    survey = db.query(Survey).filter(Survey.code == code, Survey.is_active == True).first()
    if not survey:
        raise HTTPException(404, "Pesquisa não encontrada ou encerrada.")

    if len(body.responses) < EXPECTED_QUESTIONS:
        raise HTTPException(400, f"Todas as {EXPECTED_QUESTIONS} questões devem ser respondidas. Recebidas: {len(body.responses)}")

    for q_id, val in body.responses.items():
        if not (1 <= val <= 5):
            raise HTTPException(400, f"Questão {q_id}: valor deve ser entre 1 e 5.")

    # UUID curto evita colisao em submissoes simultaneas (sem migracao de schema)
    display_id = f"R{uuid.uuid4().hex[:8]}"

    respondent = Respondent(
        id=generate_uuid(),
        survey_id=survey.id,
        display_id=display_id,
        responses_json=json.dumps(body.responses),
    )
    db.add(respondent)

    # Regenerate recommendations if we had existing ones
    existing_custom = db.query(Recommendation).filter(Recommendation.survey_id == survey.id, Recommendation.is_custom == True).all()
    if not existing_custom:
        db.query(Recommendation).filter(Recommendation.survey_id == survey.id).delete()

    db.commit()

    return {
        "ok": True,
        "display_id": display_id,
        "thank_you_title": survey.thank_you_title,
        "thank_you_message": survey.thank_you_message,
    }


@app.get("/api/survey/{code}/thanks")
def survey_thanks(code: str, db: Session = Depends(get_db)):
    survey = db.query(Survey).filter(Survey.code == code).first()
    if not survey:
        raise HTTPException(404)
    return {"title": survey.thank_you_title, "message": survey.thank_you_message}


# ════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════

def _get_survey_auth(survey_id: str, admin_code: str, db: Session) -> Survey:
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(404, "Pesquisa nao encontrada.")
    if survey.admin_code != admin_code and admin_code != GLOBAL_ADMIN_CODE:
        raise HTTPException(403, "Acesso negado.")
    return survey


def _survey_brief(s: Survey, db: Session) -> dict:
    count = db.query(Respondent).filter(Respondent.survey_id == s.id).count()
    return {
        "id": s.id,
        "code": s.code,
        "company_name": s.company_name,
        "is_active": s.is_active,
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "respondent_count": count,
    }


def _survey_detail(s: Survey, db: Session) -> dict:
    brief = _survey_brief(s, db)
    brief["thank_you_title"] = s.thank_you_title
    brief["thank_you_message"] = s.thank_you_message
    return brief


def _aggregate_dim_scores(all_scores: list) -> list:
    """Average dimension scores across all respondents."""
    totals = defaultdict(lambda: {"scores": [], "type": None, "name": None, "category": None, "description": None})
    for respondent_scores in all_scores:
        for d in respondent_scores:
            key = d["dimension_id"]
            totals[key]["scores"].append(d["score"])
            totals[key]["type"] = d["type"]
            totals[key]["name"] = d["name"]
            totals[key]["category"] = d["category"]
            totals[key]["description"] = d["description"]

    result = []
    for dim_id, data in totals.items():
        avg = round(sum(data["scores"]) / len(data["scores"]), 2)
        status = get_status(avg, data["type"])
        result.append({
            "dimension_id": dim_id,
            "name": data["name"],
            "score": avg,
            "status": status,
            "type": data["type"],
            "category": data["category"],
            "description": data["description"],
        })
    return result


def _get_export_data(survey: Survey, db: Session) -> dict:
    respondents = db.query(Respondent).filter(Respondent.survey_id == survey.id).order_by(Respondent.submitted_at).all()
    if not respondents:
        return {"dim_scores": [], "kpis": {}, "summary": {"green": 0, "yellow": 0, "red": 0, "total": 0}, "recommendations": [], "respondents_data": []}

    all_dim_scores = []
    respondents_data = []
    for r in respondents:
        responses = {int(k): int(v) for k, v in r.responses.items()}
        ds = calc_dimension_scores(responses)
        all_dim_scores.append(ds)
        respondents_data.append({
            "display_id": r.display_id,
            "scores": {d["dimension_id"]: d["score"] for d in ds},
            "statuses": {d["dimension_id"]: d["status"] for d in ds},
        })

    agg = _aggregate_dim_scores(all_dim_scores)
    kpis = calc_kpis(agg)
    summary = calc_summary(agg)

    recs = db.query(Recommendation).filter(Recommendation.survey_id == survey.id).order_by(Recommendation.order_index).all()
    recs_list = [{"title": r.title, "description": r.description, "priority": r.priority, "dimension_ids": r.dimension_ids, "is_custom": r.is_custom} for r in recs]
    if not recs_list:
        recs_list = generate_recommendations(agg)

    return {"dim_scores": agg, "kpis": kpis, "summary": summary, "recommendations": recs_list, "respondents_data": respondents_data}


# ════════════════════════════════════════════
# RUN
# ════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 60)
    print("  Fluir -- Bem-estar que move resultados")
    print("=" * 60)
    print(f"  Questionario: {len(QUESTIONS)} questoes")
    print(f"  Dimensoes: {len(DIMENSIONS)} dimensoes psicossociais")
    print("=" * 60)
    print("  Acesse: http://localhost:8000")
    print("  API Docs: http://localhost:8000/docs")
    print("=" * 60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
