from sqlalchemy import create_engine
from contextlib import contextmanager

from .models.RawVacanciesModel import VacanciesTable, Base

from itemadapter import ItemAdapter

from sqlalchemy.orm import scoped_session, sessionmaker
import logging 
from sqlalchemy.dialects.postgresql import insert

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from environs import Env
from pathlib import Path

def configure_db():
    env = Env()
    project_dir = Path(__file__).resolve().parent.parent
    env_file = project_dir / ".env"
    
    env.read_env(env_file)

    return {
        "user": env.str("POSTGRES_USER"),
        "password": env.str("POSTGRES_PASSWORD"),
        "db": env.str("POSTGRES_DB"),
        "host": env.str("POSTGRES_HOST"),
        "port": env.str("POSTGRES_PORT")
    }

def get_connection_string():
    config = configure_db()
    return f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['db']}"

class DatabasePipeline:
    def __init__(self):
        self.engine = create_engine(
            get_connection_string(),
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        self.session_factory = scoped_session(
            sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False
            )
        )

    @contextmanager
    def session_scope(self):
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            session.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        vacancy_data = {
            "title": adapter.get("title"),
            "salary": adapter.get("salary", "Не указано"),
            "company": adapter.get("company"),
            "rating": adapter.get("rating", None),
            "city": adapter.get("city", None),
            "remote": adapter.get("remote", None),
            "experience": adapter.get("experience", None),
            "link": adapter.get("link", None)
        }

        try:
            with self.session_scope() as session:
                stmt = insert(VacanciesTable).values(**vacancy_data)
                session.execute(stmt)
                logger.debug(f"Processed vacancy: {vacancy_data['title']}")
        except Exception as e:
            logger.error(f"Error saving vacancy {vacancy_data.get('title')}: {e}")
            raise

        return item

    def close_spider(self, spider):
        self.session_factory.remove()
        self.engine.dispose()
        logger.info("Database connection closed")
