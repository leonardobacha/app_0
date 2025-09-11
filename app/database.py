from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# DATABASE_URL = (
#     f"postgresql://{os.getenv('POSTGRES_USER')}:"
#     f"{os.getenv('POSTGRES_PASSWORD')}@"
#     f"{os.getenv('POSTGRES_HOST')}:"
#     f"{os.getenv('POSTGRES_PORT')}/"
#     f"{os.getenv('POSTGRES_DB')}"
# )


DATABASE_URL = "postgresql://fastapi_user:senha123@localhost/fastapi_db"

print(DATABASE_URL)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


#Base.metadata.drop_all(bind=engine)  # Apaga as tabelas existentes
#Base.metadata.create_all(bind=engine)  

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


