# Database package
from config import Config
from .db import Database, get_db as get_sqlite_db

# Import SQL Server database if configured
if Config.USE_SQL_SERVER:
    from .sqlserver_db import SQLServerDatabase, get_sqlserver_db
    
    # Use SQL Server as default
    def get_db():
        """Get database instance (SQL Server)"""
        return get_sqlserver_db()
else:
    # Use SQLite as default
    def get_db():
        """Get database instance (SQLite)"""
        return get_sqlite_db()

__all__ = ['Database', 'get_db']

if Config.USE_SQL_SERVER:
    __all__.extend(['SQLServerDatabase', 'get_sqlserver_db'])
