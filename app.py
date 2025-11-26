import streamlit as st
import asyncio
import sys
from buscador import buscar_produto_ml

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

st.set_page_config(page_title="Monitor de Preços", page_icon="🕵️")

st.title("🕵️ Buscador de Ofertas")
st.write("Encontre o produto e crie um alerta de preço.")

produto = st.text_input("Qual produto você quer monitorar?", placeholder="Ex: Monitor Gamer, Crocs...")

if st.button("Pesquisar"):
    if not produto:
        st.warning("Por favor, digite o nome de um produto.")
    else:
        with st.spinner(f"O robô está buscando '{produto}' no Mercado Livre..."):
            resultados = asyncio.run(buscar_produto_ml(produto))
        
        if len(resultados) == 0:
            st.error("Não encontramos nada ou ocorreu um erro de conexão.")
        else:
            st.success(f"Encontramos {len(resultados)} produtos!")
            
            for item in resultados:
                with st.container():
                    st.subheader(item['nome'])
                    st.write(f"**Preço Atual:** {item['preco_atual']}")
                    st.write(f"[Ver no Mercado Livre]({item['link']})")
                    st.divider()