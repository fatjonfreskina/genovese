"""Run periodically with the backend's database environment; sends no email."""

from .database import SessionLocal
from .routers.email_links import cleanup_expired, utcnow


def main() -> None:
    with SessionLocal() as db:
        cleanup_expired(db, utcnow())
        db.commit()


if __name__ == "__main__":
    main()
