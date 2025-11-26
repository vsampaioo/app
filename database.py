import os
import psycopg2
from dotenv import load_dotenv


load_dotenv()


DB_URL = os.getenv("DATABASE_URL")

def criar_tabela():
   
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alertas (
                id SERIAL PRIMARY KEY,
                nome_produto TEXT,
                link TEXT,
                email TEXT,
                preco_alvo DECIMAL
            );
        ''')
        
        conn.commit()
        conn.close()
        print("--- Banco Supabase Conectado com Sucesso! ---")
    except Exception as e:
        print(f"Erro ao conectar no banco: {e}")

def salvar_no_banco(nome, link, email, preco):
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO alertas (nome_produto, link, email, preco_alvo)
            VALUES (%s, %s, %s, %s)
        ''', (nome, link, email, preco))
        
        conn.commit()
        conn.close()
        print(f"Produto salvo na nuvem: {nome}")
    except Exception as e:
        print(f"Erro ao salvar: {e}")