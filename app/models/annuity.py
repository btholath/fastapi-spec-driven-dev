from sqlalchemy import Column, Integer, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Annuity(Base):
    __tablename__ = "annuities"
    id = Column(Integer, primary_key=True)
    principal = Column(Float, nullable=False)
    term_years = Column(Integer, nullable=False)
    annual_rate = Column(Float, nullable=False)
    premium = Column(Float, nullable=False)