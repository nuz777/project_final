from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

# Configura aquí tus datos de acceso a MySQL
USERNAME = "root" 
PASSWORD = ""  
HOST = "localhost"
DATABASE = "gestion_tareas"

# URL de conexión a MySQL
URL = f"http://localhost/phpmyadmin/index.php?route=/database/structure&db=gestion_tareas{USERNAME}:{PASSWORD}@{HOST}/{DATABASE}"

from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://root:@localhost/gestion_tareas")

Session = sessionmaker(bind=engine)
session = Session()
