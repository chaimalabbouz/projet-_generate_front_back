"""
Deux connexions MySQL distinctes, jamais mélangées :
  - moonpilot_db : users, generations, admins   (base applicative, dans WSL)
  - llm_config   : prompts, models, configs     (base LLM, dans Docker)

Les connexions sont mises en pool : établies une fois, puis réutilisées.
"""
import os
from contextlib import contextmanager
from mysql.connector import pooling
from dotenv import load_dotenv

load_dotenv()

_moonpilot_pool = None
_llm_pool = None


def _get_moonpilot_pool():
    global _moonpilot_pool
    if _moonpilot_pool is None:
        _moonpilot_pool = pooling.MySQLConnectionPool(
            pool_name="moonpilot",
            pool_size=5,
            host=os.getenv("MOONPILOT_DB_HOST", "172.23.223.163"),
            port=int(os.getenv("MOONPILOT_DB_PORT", 3306)),
            user=os.getenv("MOONPILOT_DB_USER", "moonpilot_app"),
            password=os.getenv("MOONPILOT_DB_PASSWORD", ""),
            database=os.getenv("MOONPILOT_DB_NAME", "moonpilot_db"),
            connection_timeout=30,
        )
    return _moonpilot_pool


def _get_llm_pool():
    global _llm_pool
    if _llm_pool is None:
        _llm_pool = pooling.MySQLConnectionPool(
            pool_name="llm",
            pool_size=3,
            host=os.getenv("MYSQL_HOST", "mysql"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            user=os.getenv("MYSQL_USER", "llm_user"),
            password=os.getenv("MYSQL_PASSWORD", "1234"),
            database=os.getenv("MYSQL_DATABASE", "llm_config"),
            connection_timeout=30,
        )
    return _llm_pool


@contextmanager
def moonpilot_cursor(dictionary: bool = True):
    """Curseur sur la base applicative. Commit auto, connexion rendue au pool."""
    conn = _get_moonpilot_pool().get_connection()
    cursor = conn.cursor(dictionary=dictionary)
    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


@contextmanager
def llm_cursor(dictionary: bool = True):
    """Curseur sur la base des prompts LLM."""
    conn = _get_llm_pool().get_connection()
    cursor = conn.cursor(dictionary=dictionary)
    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()