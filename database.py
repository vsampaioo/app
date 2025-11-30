import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

def criar_tabela():
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
        # Adicionei a coluna 'imagem'
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alertas (
                id SERIAL PRIMARY KEY,
                nome_produto TEXT,
                link TEXT,
                email TEXT,
                preco_alvo DECIMAL,
                imagem TEXT
            );
        ''')
        
        # Tenta atualizar a tabela caso ela já exista sem a coluna imagem
        try:
            cursor.execute("ALTER TABLE alertas ADD COLUMN IF NOT EXISTS imagem TEXT;")
        except:
            pass

        conn.commit()
        conn.close()
        print("--- Banco Conectado e Atualizado! ---")
    except Exception as e:
        print(f"Erro ao conectar no banco: {e}")

# Nova função aceitando 'imagem'
def salvar_no_banco(nome, link, email, preco, imagem):
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO alertas (nome_produto, link, email, preco_alvo, imagem)
            VALUES (%s, %s, %s, %s, %s)
        ''', (nome, link, email, preco, imagem))
        
        conn.commit()
        conn.close()
        print(f"Produto salvo: {nome}")
    except Exception as e:
        print(f"Erro ao salvar: {e}")