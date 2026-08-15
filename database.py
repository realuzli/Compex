import sqlite3

def conectar():
    conn = sqlite3.connect("clinica.db")
    conn.row_factory = sqlite3.Row
    return conn

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT NOT NULL,
            email TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS horarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            hora TEXT NOT NULL,
            disponivel INTEGER DEFAULT 1
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            horario_id INTEGER NOT NULL,
            observacao TEXT,
            cancelado INTEGER DEFAULT 0,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (horario_id) REFERENCES horarios(id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    criar_tabelas()
    print('Banco criado!')