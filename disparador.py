import os
import psycopg2
import smtplib
import asyncio
from email.message import EmailMessage
from dotenv import load_dotenv
from buscador import checar_preco_link


load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

EMAIL_ROBO = "avisaeu.app@gmail.com"
SENHA_ROBO = "zgnk zgxd nirx dbwa"

def enviar_notificacao(email_usuario, produto, preco_atual, link):
    msg = EmailMessage()
    msg['Subject'] = f"🚨 BAIXOU! {produto} está barato!"
    msg['From'] = EMAIL_ROBO
    msg['To'] = email_usuario
    
    conteudo = f"""
    Olá! Boas notícias.
    
    O produto "{produto}" atingiu o preço que você queria!
    
    💰 Preço Atual: R$ {preco_atual}
    
    🔗 Compre agora: {link}
    
    Att,
    Seu Bot Monitor
    """
    msg.set_content(conteudo)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ROBO, SENHA_ROBO)
            smtp.send_message(msg)
            print(f"✅ E-mail enviado para {email_usuario}")
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")

async def verificar_alertas():
    print("--- INICIANDO A RONDA DE PREÇOS ---")
    
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome_produto, link, email, preco_alvo FROM alertas")
    alertas = cursor.fetchall()
    conn.close()
    
    if not alertas:
        print("Nenhum alerta cadastrado.")
        return

    for alerta in alertas:
        id_alerta, nome, link, email_usuario, preco_alvo = alerta
        
        print(f"Verificando: {nome}...")
        
        preco_agora = await checar_preco_link(link)
        
        if preco_agora:
            print(f"   -> Meta: {preco_alvo} | Atual: {preco_agora}")
            
            if preco_agora <= float(preco_alvo):
                print("   🔥🔥 PREÇO BOM! Enviando e-mail...")
                enviar_notificacao(email_usuario, nome, preco_agora, link)
            else:
                print("   ❄️ Ainda caro. Nada a fazer.")
        else:
            print("   ⚠️ Erro ao ler preço.")
            
    print("--- FIM DA RONDA ---")

if __name__ == "__main__":
    asyncio.run(verificar_alertas())