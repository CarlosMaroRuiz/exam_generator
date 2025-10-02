import sqlite3
from typing import List, Tuple, Optional, Union

class SQLiteDB:
    def __init__(self, db_name: str = "examenes.db"):
        self.db_name = db_name

    def _connect(self) -> sqlite3.Connection:
        
        return sqlite3.connect(self.db_name)

    def execute(self, query: str, params: Union[Tuple, List] = ()) -> None:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()

    def fetchall(self, query: str, params: Union[Tuple, List] = ()) -> List[Tuple]:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def fetchone(self, query: str, params: Union[Tuple, List] = ()) -> Optional[Tuple]:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()