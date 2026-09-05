from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
print(f"📊 Connecting to: {DATABASE_URL}")

# Create PostgreSQL engine
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Task database model
class TaskDB(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    done = Column(Boolean, default=False)

# Initialize database - create table and seed data only if empty
def init_db():
    print("🔄 Creating tables if not exist...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if table is empty
        count = db.query(TaskDB).count()
        print(f"📊 Current tasks count: {count}")
        
        if count == 0:
            # Seed 3 example tasks
            example_tasks = [
                TaskDB(title="Buy groceries", done=False),
                TaskDB(title="Finish assignment", done=False),
                TaskDB(title="Read a book", done=False)
            ]
            db.add_all(example_tasks)
            db.commit()
            print("✅ Seeded 3 example tasks into PostgreSQL!")
        else:
            print("✅ Tasks already exist, skipping seed.")
    finally:
        db.close()