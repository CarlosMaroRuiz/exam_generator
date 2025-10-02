import sqlite3

def crear_base_de_datos(db_name: str = "examenes.db") -> None:
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS examen (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url_bucket TEXT NOT NULL,
        id_usuario INTEGER NOT NULL,
        titulo TEXT NOT NULL,
        FOREIGN KEY (id_usuario) REFERENCES usuario(id)
    );
    """)

   
    conn.commit()
    conn.close()

    print(f"Base de datos '{db_name}' creada con tablas 'usuario' y 'examen'.")

