from sqlalchemy import Column, Text, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class VacanciesTable(Base):
    __tablename__ = "vacancies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text)
    salary = Column(Text)
    company = Column(Text)
    link = Column(Text)
    city = Column(Text)
    rating = Column(Text)
    remote = Column(Text)
    experience = Column(Text)


    
    