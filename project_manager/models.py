from sqlalchemy import Column, Integer, String, ForeignKey, Date, Enum
from sqlalchemy.orm import relationship
from database import Base
import enum

class UserRole(enum.Enum):
    admin = "Administrador"
    member = "Colaborador"

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(50), nullable=False)
    role = Column(Enum(UserRole), nullable=False)

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(200))
    start_date = Column(Date)
    end_date = Column(Date)
    tasks = relationship("Task", back_populates="project")

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    description = Column(String(200))
    due_date = Column(Date)
    priority = Column(String(20))
    status = Column(String(20))
    project_id = Column(Integer, ForeignKey('projects.id'))
    project = relationship("Project", back_populates="tasks")
