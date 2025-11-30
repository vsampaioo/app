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

def enviar_notificacao_html(email_usuario, produto, preco_atual, link, imagem, preco_alvo):
    msg = EmailMessage()
    msg['Subject'] = f"🔥 BAIXOU! {produto} por R$ {preco_atual}"
    msg['From'] = EMAIL_ROBO
    msg['To'] = email_usuario
    
    # Template HTML Profissional
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
        .container {{ background-color: #ffffff; padding: 20px; border-radius: 10px; max-width: 600px; margin: auto; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; color: #ff4b4b; }}
        .product-img {{ width: 200px; height: 200px; object-fit: contain; display: block; margin: 20px auto; border-radius: 8px; }}
        .price-box {{ background-color: #e8f5e9; color: #2e7d32; padding: 15px; text-align: center; font-size: 24px; font-weight: bold; border-radius: 5px; margin: 20px 0; }}
        .btn {{ display: block; width: 80%; margin: 20px auto; padding: 15px; background-color: #007bff; color: white; text-align: center; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 18px; }}
        .footer {{ text-align: center; font-size: 12px; color: #888; margin-top: 20px; }}
    </style>
    </head>
    <body>
        <div class="container">
            <h2 class="header">🚨 Alerta de Preço Atingido!</h2>
            <p>Olá! Temos boas notícias. O produto que você estava monitorando atingiu sua meta.</p>
            
            <img src="{imagem}" alt="Produto" class="product-img">
            
            <h3 style="text-align: center;">{produto}</h3>
            
            <div class="price-box">
                R$ {preco_atual:.2f}
            </div>
            
            <p style="text-align: center;">Sua meta era: <strong>R$ {preco_alvo}</strong> ou menos.</p>
            
            <a href="{link}" class="btn">👉 IR PARA A OFERTA</a>
            
            <div class="footer">
                Este é um e-mail automático do seu Monitor de Preços.<br>
                Não responda a este e-mail.
            </div>
        </div>
    </body>
    </html>
    """
    
    msg.set_content("Seu produto baixou de preço! Abra este e-mail para ver.") # Texto puro (fallback)
    msg.add_alternative(html_content, subtype='html') # Versão HTML bonita

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ROBO, SENHA_ROBO)
            smtp.send_message(msg)
            print(f"✅ E-mail HTML enviado para {email_usuario}")
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")

async def verificar_alertas():
    print("\n--- INICIANDO A RONDA DE PREÇOS ---")
    
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        # Busca também a imagem (coluna 5)
        cursor.execute("SELECT id, nome_produto, link, email, preco_alvo, imagem FROM alertas")
        alertas = cursor.fetchall()
        conn.close()
    except Exception as e:
        print(f"⚠️ Erro ao conectar no banco: {e}")
        return
    
    if not alertas:
        print("Nenhum alerta cadastrado.")
        return

    for alerta in alertas:
        # Desempacota as 6 colunas
        id_alerta, nome, link, email_usuario, preco_alvo, imagem = alerta
        
        print(f"Verificando: {nome}...")
        
        preco_agora = await checar_preco_link(link)
        
        if preco_agora > 0:
            print(f"   -> Meta: {preco_alvo} | Atual: {preco_agora}")
            
            # Lógica: Se o preço atual for MENOR ou IGUAL ao alvo
            if preco_agora <= float(preco_alvo):
                print("   🔥🔥 PREÇO BOM! Enviando e-mail...")
                # Envia e-mail bonito
                enviar_notificacao_html(email_usuario, nome, preco_agora, link, imagem, preco_alvo)
            else:
                print("   ❄️ Ainda caro. Nada a fazer.")
        else:
            print("   ⚠️ Erro ao ler preço.")
            
    print("--- FIM DA RONDA ---")

async def iniciar_robo():
    print("🤖 Robô iniciado! Pressione Ctrl+C para parar.")
    while True:
        await verificar_alertas()
        print("💤 Dormindo por 30 minutos...")
        await asyncio.sleep(1800) 

if __name__ == "__main__":
    try:
        asyncio.run(iniciar_robo())
    except KeyboardInterrupt:
        print("🛑 Robô parado.")