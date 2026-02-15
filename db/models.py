from sqlalchemy import create_all, Column, Integer, String, JSON, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class AuditSession(Base):
    __tablename__ = 'audit_sessions'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    network = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    results = relationship("HostResult", back_populates="session")

class HostResult(Base):
    __tablename__ = 'host_results'
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('audit_sessions.id'))
    ip = Column(String)
    hostname = Column(String)
    category = Column(String)
    vendor = Column(String)
    vulnerable = Column(Boolean, default=False)
    scan_data = Column(JSON)
    session = relationship("AuditSession", back_populates="results")

def get_session(db_path='sqlite:///netaudit.db'):
    from sqlalchemy import create_engine
    engine = create_engine(db_path)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()
