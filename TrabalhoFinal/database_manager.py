import mysql.connector
from mysql.connector import errorcode
from typing import List, Dict, Any, Tuple, Optional
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
}

SQL_CREATE_PONTOS = """
CREATE TABLE IF NOT EXISTS pontos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL UNIQUE,
    tipo ENUM('Depósito', 'Cidade') NOT NULL,
    coord_x INT,
    coord_y INT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_modificacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;
"""

SQL_CREATE_CONEXOES = """
CREATE TABLE IF NOT EXISTS conexoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ponto_origem_id INT NOT NULL,
    ponto_destino_id INT NOT NULL,
    distancia DECIMAL(10, 2) NOT NULL,
    bidirecional BOOLEAN DEFAULT TRUE,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ponto_origem_id) REFERENCES pontos(id) ON DELETE CASCADE,
    FOREIGN KEY (ponto_destino_id) REFERENCES pontos(id) ON DELETE CASCADE,
    UNIQUE KEY idx_origem_destino (ponto_origem_id, ponto_destino_id)
) ENGINE=InnoDB;
"""

SQL_CREATE_CAMIOES = """
CREATE TABLE IF NOT EXISTS camioes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    matricula VARCHAR(20) NOT NULL UNIQUE,
    nome_descricao VARCHAR(255),
    capacidade DECIMAL(10, 2),
    unidade_capacidade VARCHAR(10) DEFAULT 'ton',
    tipo_veiculo VARCHAR(100),
    estado ENUM('Disponível', 'Em Rota', 'Em Manutenção', 'Indisponível') DEFAULT 'Disponível',
    localizacao_atual_ponto_id INT NULL,
    observacoes TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_modificacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (localizacao_atual_ponto_id) REFERENCES pontos(id) ON DELETE SET NULL
) ENGINE=InnoDB;
"""

SQL_CREATE_MOTORISTAS = """
CREATE TABLE IF NOT EXISTS motoristas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_completo VARCHAR(255) NOT NULL,
    cnh VARCHAR(20) NOT NULL UNIQUE,
    categoria_cnh VARCHAR(5),
    validade_cnh DATE NULL,
    telefone VARCHAR(20),
    email VARCHAR(255) UNIQUE,
    estado ENUM('Disponível', 'Em Rota', 'De Folga', 'Indisponível') DEFAULT 'Disponível',
    observacoes TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_modificacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;
"""

SQL_CREATE_CARGAS = """
CREATE TABLE IF NOT EXISTS cargas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(255) NOT NULL,
    tipo_carga VARCHAR(100),
    peso_kg DECIMAL(10, 2) NULL,
    volume_m3 DECIMAL(10, 3) NULL,
    ponto_origem_id INT NOT NULL,
    ponto_destino_id INT NOT NULL,
    cliente_nome VARCHAR(255),
    data_prevista_coleta DATE NULL,
    data_prevista_entrega DATE NULL,
    estado ENUM('Pendente', 'Agendada', 'Coletada', 'Em Trânsito', 'Entregue', 'Cancelada', 'Atrasada') DEFAULT 'Pendente',
    camiao_atribuido_id INT NULL,
    motorista_atribuido_id INT NULL,
    observacoes TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_modificacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (ponto_origem_id) REFERENCES pontos(id) ON DELETE RESTRICT,
    FOREIGN KEY (ponto_destino_id) REFERENCES pontos(id) ON DELETE RESTRICT,
    FOREIGN KEY (camiao_atribuido_id) REFERENCES camioes(id) ON DELETE SET NULL,
    FOREIGN KEY (motorista_atribuido_id) REFERENCES motoristas(id) ON DELETE SET NULL
) ENGINE=InnoDB;
"""

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR: print("Erro: Utilizador ou senha MySQL incorretos.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR: print(f"Erro: Base de dados '{DB_CONFIG['database']}' não existe.")
        else: print(f"Erro ao conectar à BD: {err}")
        return None

def initialize_database():
    conn = get_db_connection()
    if conn is None: return False
    cursor = conn.cursor()
    try:
        print(f"A usar a base de dados: {DB_CONFIG['database']}")
        cursor.execute(SQL_CREATE_PONTOS); print("Tabela 'pontos' OK.")
        cursor.execute(SQL_CREATE_CONEXOES); print("Tabela 'conexoes' OK.")
        cursor.execute(SQL_CREATE_CAMIOES); print("Tabela 'camioes' OK.")
        cursor.execute(SQL_CREATE_MOTORISTAS); print("Tabela 'motoristas' OK.")
        cursor.execute(SQL_CREATE_CARGAS); print("Tabela 'cargas' OK.")
        conn.commit()
        print("Inicialização da base de dados concluída.")
        return True
    except mysql.connector.Error as err:
        print(f"Erro ao inicializar tabelas: {err}")
        conn.rollback()
        return False
    finally:
        if conn.is_connected(): cursor.close(); conn.close()

def adicionar_ponto_db(nome: str, tipo: str, coord_x: Optional[int] = None, coord_y: Optional[int] = None) -> Optional[int]:
    conn = get_db_connection(); cursor = conn.cursor() if conn else None
    if not cursor: return None
    sql = "INSERT INTO pontos (nome, tipo, coord_x, coord_y) VALUES (%s, %s, %s, %s)"
    try:
        cursor.execute(sql, (nome, tipo, coord_x, coord_y)); conn.commit(); return cursor.lastrowid
    except mysql.connector.Error as err: print(f"Erro add ponto '{nome}': {err}"); conn.rollback(); return None
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def obter_ponto_por_nome_db(nome: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection(); cursor = conn.cursor(dictionary=True) if conn else None
    if not cursor: return None
    try: cursor.execute("SELECT * FROM pontos WHERE nome = %s", (nome,)); return cursor.fetchone()
    except mysql.connector.Error as err: print(f"Erro obter ponto '{nome}': {err}"); return None
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def obter_ponto_por_id_db(ponto_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection(); cursor = conn.cursor(dictionary=True) if conn else None
    if not cursor: return None
    try: cursor.execute("SELECT * FROM pontos WHERE id = %s", (ponto_id,)); return cursor.fetchone()
    except mysql.connector.Error as err: print(f"Erro obter ponto ID '{ponto_id}': {err}"); return None
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def obter_todos_pontos_db() -> List[Dict[str, Any]]:
    conn = get_db_connection(); cursor = conn.cursor(dictionary=True) if conn else None
    if not cursor: return []
    try: cursor.execute("SELECT * FROM pontos ORDER BY nome"); return cursor.fetchall()
    except mysql.connector.Error as err: print(f"Erro obter todos pontos: {err}"); return []
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def atualizar_ponto_coords_db(ponto_id: int, coord_x: int, coord_y: int) -> bool:
    conn = get_db_connection(); cursor = conn.cursor() if conn else None
    if not cursor: return False
    sql = "UPDATE pontos SET coord_x = %s, coord_y = %s WHERE id = %s"
    try: cursor.execute(sql, (coord_x, coord_y, ponto_id)); conn.commit(); return cursor.rowcount > 0
    except mysql.connector.Error as err: print(f"Erro update coords ponto {ponto_id}: {err}"); conn.rollback(); return False
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def remover_ponto_db(ponto_id: int) -> bool:
    conn = get_db_connection(); cursor = conn.cursor() if conn else None
    if not cursor: return False
    try: cursor.execute("DELETE FROM pontos WHERE id = %s", (ponto_id,)); conn.commit(); return cursor.rowcount > 0
    except mysql.connector.Error as err: print(f"Erro remover ponto {ponto_id}: {err}"); conn.rollback(); return False
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def adicionar_conexao_db(p_orig_id: int, p_dest_id: int, dist: float, bidir: bool = True) -> Optional[int]:
    conn = get_db_connection(); cursor = conn.cursor() if conn else None
    if not cursor: return None
    sql = "INSERT INTO conexoes (ponto_origem_id, ponto_destino_id, distancia, bidirecional) VALUES (%s, %s, %s, %s)"
    try: cursor.execute(sql, (p_orig_id, p_dest_id, dist, bidir)); conn.commit(); return cursor.lastrowid
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_DUP_ENTRY: print(f"Erro: Conexão {p_orig_id}->{p_dest_id} já existe.")
        else: print(f"Erro add conexão: {err}")
        conn.rollback(); return None
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def obter_todas_conexoes_db() -> List[Dict[str, Any]]:
    conn = get_db_connection(); cursor = conn.cursor(dictionary=True) if conn else None
    if not cursor: return []
    sql = """SELECT c.id, c.ponto_origem_id, po.nome as nome_origem, c.ponto_destino_id,
                pd.nome as nome_destino, c.distancia, c.bidirecional
        FROM conexoes c JOIN pontos po ON c.ponto_origem_id = po.id JOIN pontos pd ON c.ponto_destino_id = pd.id
        ORDER BY po.nome, pd.nome"""
    try: cursor.execute(sql); return cursor.fetchall()
    except mysql.connector.Error as err: print(f"Erro obter todas conexões: {err}"); return []
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def adicionar_camiao_db(mat: str, nome: str, cap: float, unid: str, tipo: str, est: str = 'Disponível',
                        loc_id: Optional[int] = None, obs: str = "") -> Optional[int]:
    conn = get_db_connection(); cursor = conn.cursor() if conn else None
    if not cursor: return None
    sql = """INSERT INTO camioes (matricula, nome_descricao, capacidade, unidade_capacidade, tipo_veiculo,
                                estado, localizacao_atual_ponto_id, observacoes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
    try:
        cursor.execute(sql, (mat, nome, cap, unid, tipo, est, loc_id, obs)); conn.commit(); return cursor.lastrowid
    except mysql.connector.Error as err: print(f"Erro add camião '{mat}': {err}"); conn.rollback(); return None
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def obter_camiao_por_id_db(camiao_id: int) -> Optional[Dict[str, Any]]: # Nova função
    conn = get_db_connection(); cursor = conn.cursor(dictionary=True) if conn else None
    if not cursor: return None
    sql = """SELECT ca.*, p.nome as nome_localizacao_atual
            FROM camioes ca LEFT JOIN pontos p ON ca.localizacao_atual_ponto_id = p.id
            WHERE ca.id = %s"""
    try: cursor.execute(sql, (camiao_id,)); return cursor.fetchone()
    except mysql.connector.Error as err: print(f"Erro obter camião ID {camiao_id}: {err}"); return None
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def obter_todos_camioes_db() -> List[Dict[str, Any]]:
    conn = get_db_connection(); cursor = conn.cursor(dictionary=True) if conn else None
    if not cursor: return []
    sql = """SELECT ca.*, p.nome as nome_localizacao_atual
            FROM camioes ca LEFT JOIN pontos p ON ca.localizacao_atual_ponto_id = p.id
            ORDER BY ca.matricula"""
    try: cursor.execute(sql); return cursor.fetchall()
    except mysql.connector.Error as err: print(f"Erro obter todos camiões: {err}"); return []
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def atualizar_camiao_db(cam_id: int, dados: Dict[str, Any]) -> bool:
    conn = get_db_connection(); cursor = conn.cursor() if conn else None
    if not cursor or not dados: return False
    set_clauses, valores = [], []
    permitidas = ['matricula','nome_descricao','capacidade','unidade_capacidade','tipo_veiculo',
                'estado','localizacao_atual_ponto_id','observacoes']
    for col, val in dados.items():
        if col in permitidas: set_clauses.append(f"{col} = %s"); valores.append(val)
    if not set_clauses: return False
    valores.append(cam_id)
    sql = f"UPDATE camioes SET {', '.join(set_clauses)} WHERE id = %s"
    try: cursor.execute(sql, tuple(valores)); conn.commit(); return cursor.rowcount > 0
    except mysql.connector.Error as err: print(f"Erro update camião {cam_id}: {err}"); conn.rollback(); return False
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def remover_camiao_db(cam_id: int) -> bool:
    conn = get_db_connection(); cursor = conn.cursor() if conn else None
    if not cursor: return False
    try: cursor.execute("DELETE FROM camioes WHERE id = %s", (cam_id,)); conn.commit(); return cursor.rowcount > 0
    except mysql.connector.Error as err: print(f"Erro remover camião {cam_id}: {err}"); conn.rollback(); return False
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def adicionar_motorista_db(nome: str, cnh: str, cat_cnh: Optional[str], val_cnh: Optional[str], 
                        tel: Optional[str], email: Optional[str], est: str = 'Disponível', 
                        obs: str = "") -> Optional[int]:
    conn = get_db_connection(); cursor = conn.cursor() if conn else None
    if not cursor: return None
    sql = """INSERT INTO motoristas (nome_completo, cnh, categoria_cnh, validade_cnh, telefone, 
                                    email, estado, observacoes) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
    try:
        validade_cnh_db = val_cnh if val_cnh else None
        cursor.execute(sql, (nome, cnh, cat_cnh, validade_cnh_db, tel, email, est, obs))
        conn.commit(); return cursor.lastrowid
    except mysql.connector.Error as err: print(f"Erro add motorista '{nome}': {err}"); conn.rollback(); return None
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def obter_todos_motoristas_db() -> List[Dict[str, Any]]:
    conn = get_db_connection(); cursor = conn.cursor(dictionary=True) if conn else None
    if not cursor: return []
    try: cursor.execute("SELECT * FROM motoristas ORDER BY nome_completo"); return cursor.fetchall()
    except mysql.connector.Error as err: print(f"Erro obter todos motoristas: {err}"); return []
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def obter_motorista_por_id_db(motorista_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection(); cursor = conn.cursor(dictionary=True) if conn else None
    if not cursor: return None
    try: cursor.execute("SELECT * FROM motoristas WHERE id = %s", (motorista_id,)); return cursor.fetchone()
    except mysql.connector.Error as err: print(f"Erro obter motorista ID {motorista_id}: {err}"); return None
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def atualizar_motorista_db(mot_id: int, dados: Dict[str, Any]) -> bool:
    conn = get_db_connection(); cursor = conn.cursor() if conn else None
    if not cursor or not dados: return False
    set_clauses, valores = [], []
    permitidas = ['nome_completo','cnh','categoria_cnh','validade_cnh','telefone',
                'email','estado','observacoes']
    for col, val in dados.items():
        if col in permitidas:
            set_clauses.append(f"{col} = %s")
            if col == 'validade_cnh' and not val:
                valores.append(None)
            else:
                valores.append(val)
    if not set_clauses: return False
    valores.append(mot_id)
    sql = f"UPDATE motoristas SET {', '.join(set_clauses)} WHERE id = %s"
    try: cursor.execute(sql, tuple(valores)); conn.commit(); return cursor.rowcount > 0
    except mysql.connector.Error as err: print(f"Erro update motorista {mot_id}: {err}"); conn.rollback(); return False
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def remover_motorista_db(mot_id: int) -> bool:
    conn = get_db_connection(); cursor = conn.cursor() if conn else None
    if not cursor: return False
    try: cursor.execute("DELETE FROM motoristas WHERE id = %s", (mot_id,)); conn.commit(); return cursor.rowcount > 0
    except mysql.connector.Error as err: print(f"Erro remover motorista {mot_id}: {err}"); conn.rollback(); return False
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def adicionar_carga_db(desc: str, tipo: Optional[str], peso: Optional[float], vol: Optional[float],
                    p_orig_id: int, p_dest_id: int, cliente: Optional[str], dt_col: Optional[str],
                    dt_ent: Optional[str], est: str = 'Pendente', cam_id: Optional[int] = None,
                    mot_id: Optional[int] = None, obs: str = "") -> Optional[int]:
    conn = get_db_connection(); cursor = conn.cursor() if conn else None
    if not cursor: return None
    sql = """INSERT INTO cargas (descricao, tipo_carga, peso_kg, volume_m3, ponto_origem_id, ponto_destino_id,
                                cliente_nome, data_prevista_coleta, data_prevista_entrega, estado,
                                camiao_atribuido_id, motorista_atribuido_id, observacoes)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    try:
        dt_col_db = dt_col if dt_col else None
        dt_ent_db = dt_ent if dt_ent else None
        cursor.execute(sql, (desc,tipo,peso,vol,p_orig_id,p_dest_id,cliente,dt_col_db,dt_ent_db,est,cam_id,mot_id,obs))
        conn.commit(); return cursor.lastrowid
    except mysql.connector.Error as err: print(f"Erro add carga '{desc}': {err}"); conn.rollback(); return None
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def obter_todas_cargas_db_detalhado() -> List[Dict[str, Any]]:
    conn = get_db_connection(); cursor = conn.cursor(dictionary=True) if conn else None
    if not cursor: return []
    sql = """
        SELECT
            cg.*,
            po.nome as nome_ponto_origem,
            pd.nome as nome_ponto_destino,
            ca.matricula as matricula_camiao,
            ca.nome_descricao as nome_camiao,
            mo.nome_completo as nome_motorista,
            mo.cnh as cnh_motorista
        FROM cargas cg
        JOIN pontos po ON cg.ponto_origem_id = po.id
        JOIN pontos pd ON cg.ponto_destino_id = pd.id
        LEFT JOIN camioes ca ON cg.camiao_atribuido_id = ca.id
        LEFT JOIN motoristas mo ON cg.motorista_atribuido_id = mo.id
        ORDER BY cg.data_criacao DESC, cg.id DESC
    """
    try: cursor.execute(sql); return cursor.fetchall()
    except mysql.connector.Error as err: print(f"Erro obter todas cargas detalhado: {err}"); return []
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def obter_carga_por_id_db(carga_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection(); cursor = conn.cursor(dictionary=True) if conn else None
    if not cursor: return None
    try: cursor.execute("SELECT * FROM cargas WHERE id = %s", (carga_id,)); return cursor.fetchone()
    except mysql.connector.Error as err: print(f"Erro obter carga ID {carga_id}: {err}"); return None
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def obter_carga_por_id_db_detalhado(carga_id: int) -> Optional[Dict[str, Any]]: # Para aba de entrega
    conn = get_db_connection(); cursor = conn.cursor(dictionary=True) if conn else None
    if not cursor: return None
    sql = """
        SELECT cg.*, po.nome as nome_ponto_origem, pd.nome as nome_ponto_destino,
            ca.matricula as matricula_camiao, mo.nome_completo as nome_motorista
        FROM cargas cg
        JOIN pontos po ON cg.ponto_origem_id = po.id
        JOIN pontos pd ON cg.ponto_destino_id = pd.id
        LEFT JOIN camioes ca ON cg.camiao_atribuido_id = ca.id
        LEFT JOIN motoristas mo ON cg.motorista_atribuido_id = mo.id
        WHERE cg.id = %s
    """
    try: cursor.execute(sql, (carga_id,)); return cursor.fetchone()
    except mysql.connector.Error as err: print(f"Erro obter carga detalhada ID {carga_id}: {err}"); return None
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()


def atualizar_carga_db(carga_id: int, dados: Dict[str, Any]) -> bool:
    conn = get_db_connection(); cursor = conn.cursor() if conn else None
    if not cursor or not dados: return False
    set_clauses, valores = [], []
    permitidas = ['descricao','tipo_carga','peso_kg','volume_m3','ponto_origem_id','ponto_destino_id',
                'cliente_nome','data_prevista_coleta','data_prevista_entrega','estado',
                'camiao_atribuido_id','motorista_atribuido_id','observacoes']
    for col, val in dados.items():
        if col in permitidas:
            set_clauses.append(f"{col} = %s")
            if col in ['data_prevista_coleta', 'data_prevista_entrega'] and not val:
                valores.append(None)
            else:
                valores.append(val)
    if not set_clauses: return False
    valores.append(carga_id)
    sql = f"UPDATE cargas SET {', '.join(set_clauses)} WHERE id = %s"
    try: cursor.execute(sql, tuple(valores)); conn.commit(); return cursor.rowcount > 0
    except mysql.connector.Error as err: print(f"Erro update carga {carga_id}: {err}"); conn.rollback(); return False
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def remover_carga_db(carga_id: int) -> bool:
    conn = get_db_connection(); cursor = conn.cursor() if conn else None
    if not cursor: return False
    try: cursor.execute("DELETE FROM cargas WHERE id = %s", (carga_id,)); conn.commit(); return cursor.rowcount > 0
    except mysql.connector.Error as err: print(f"Erro remover carga {carga_id}: {err}"); conn.rollback(); return False
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()
