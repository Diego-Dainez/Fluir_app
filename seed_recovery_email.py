"""
Script para cadastrar email na tabela de recuperacao de chave.
Uso: python seed_recovery_email.py seu@email.com

Ou defina ADMIN_RECOVERY_EMAIL no .env - o app insere automaticamente ao iniciar.
"""
import sys
from database import init_db, SessionLocal, AdminRecoveryEmail

def main():
    if len(sys.argv) < 2:
        print("Uso: python seed_recovery_email.py seu@email.com")
        sys.exit(1)
    email = sys.argv[1].strip().lower()
    if not email or "@" not in email:
        print("Email invalido.")
        sys.exit(1)
    init_db()
    db = SessionLocal()
    try:
        existing = db.query(AdminRecoveryEmail).filter(AdminRecoveryEmail.email == email).first()
        if existing:
            print(f"Email {email} ja cadastrado.")
        else:
            rec = AdminRecoveryEmail(email=email)
            db.add(rec)
            db.commit()
            print(f"Email {email} cadastrado com sucesso.")
    except Exception as e:
        db.rollback()
        print(f"Erro: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
