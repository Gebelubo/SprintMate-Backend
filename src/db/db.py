from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect
from ..config import DATABASE_URL
from src.entities.models import Base

class Database:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL, echo=True)  
        self.Session = sessionmaker(bind=self.engine)
    
    def get_session(self):
        return self.Session()

    def create_tables(self):
        try:
            with self.engine.begin() as conn:
                print("Creating tables...")
                Base.metadata.create_all(bind=conn)
                print("Tables sucessfully created")
                conn.commit()  
        except Exception as e:
            print(f"Error on tables creation: {e}")
        self.test_connection()

    def test_connection(self):
        try:
            with self.engine.connect() as conn:
                print(f"Connecting to db: {conn.engine.url.database}")
                inspector = inspect(self.engine)
                print(f"Existing tables: {inspector.get_table_names()}")
                schemas = inspector.get_schema_names()
                print(f"Schemas avaliable: {schemas}")
                tabelas = inspector.get_table_names(schema="public")
                print(f"Tables on schema 'public': {tabelas}")
        except Exception as e:
            print(f"Error on db connection: {e}")