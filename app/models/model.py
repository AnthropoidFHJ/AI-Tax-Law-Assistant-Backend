from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, DateTime, func
from app.config.config import settings

Base = declarative_base()
engine = create_engine(settings.POSTGRES_URL, future=True, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

class TaxReturn(Base):
    __tablename__ = "tax_returns"
    id = Column(Integer, primary_key=True, index=True)
    tin = Column(String, index=True)
    assessment_year = Column(String, index=True)
    payable = Column(Float)
    refundable = Column(Float)
    computation = Column(JSON)
    citations = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, index=True)
    details = Column(JSON)
    user_tin = Column(String, index=True)
    created_at = Column(DateTime, server_default=func.now())
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
