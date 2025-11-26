import streamlit as st
import asyncio
import sys
from buscador import buscar_produto_ml
from database import salvar_no_banco, criar_tabela

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

criar_tabela()

st.set_page_config(page_title="Monitor de Preços", page_icon="🕵️")
st.title("🕵️ Buscador de Ofertas")

if 'resultados' not in st.session_state:
    st.session_state['resultados'] = []

produto = st.text_input("Qual produto você quer monitorar?", placeholder="Ex: iPhone 13, Crocs...")

if st.button("Pesquisar"):
    if not produto:
        st.warning("Por favor, digite o nome de um produto.")
    else:
        with st.spinner(f"Buscando '{produto}' no Mercado Livre..."):
            st.session_state['resultados'] = asyncio.run(buscar_produto_ml(produto))

if len(st.session_state['resultados']) > 0:
    st.subheader("Resultados encontrados:")
    
    for i, item in enumerate(st.session_state['resultados']):
        with st.expander(f"{item['nome']} - R$ {item['preco_atual']}"):
            st.write(f"**Link:** [Ir para o site]({item['link']})")
            
            with st.form(key=f"form_{i}"):
                col1, col2 = st.columns(2)
                email_usuario = col1.text_input("Seu E-mail")
                
                try:
                    preco_limpo = float(item['preco_atual'].replace('R$', '').replace('.', '').replace(',', '.').strip())
                    valor_sugerido = preco_limpo * 0.9 # Sugere 10% desconto
                except:
                    valor_sugerido = 0.0
                    
                preco_alvo = col2.number_input("Me avise se baixar para (R$):", value=valor_sugerido)
                
                botao_salvar = st.form_submit_button("Criar Alerta 🔔")
                
                if botao_salvar:
                    if email_usuario:
                        salvar_no_banco(item['nome'], item['link'], email_usuario, preco_alvo)
                        st.success(f"✅ Alerta Criado! Avisaremos em {email_usuario}")
                    else:
                        st.error("Preencha o e-mail!")