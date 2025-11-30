import streamlit as st
import asyncio
import sys
from buscador import buscar_todos_sites
from database import salvar_no_banco, criar_tabela

st.set_page_config(page_title="Avisa Eu", page_icon="🕵️", layout="centered")

# --- LÓGICA TEMA ---
if 'is_dark_mode' not in st.session_state: st.session_state['is_dark_mode'] = True 

col_header, col_toggle = st.columns([4, 1])
with col_header: st.title("Avisa Eu - Seu melhor amigo")
with col_toggle:
    st.write("") 
    modo_escuro = st.toggle("Dark Mode", value=st.session_state['is_dark_mode'])
    st.session_state['is_dark_mode'] = modo_escuro

# --- CORES ---
if modo_escuro:
    cor_fundo_app = "#0e1117"
    cor_fundo_card = "#262730"
    cor_texto = "#ffffff"
    cor_borda = "#4e4e4e"
    cor_preco = "#00e676"
    cor_input_bg = "#262730"
else:
    cor_fundo_app = "#ffffff"
    cor_fundo_card = "#f0f2f6"
    cor_texto = "#000000"
    cor_borda = "#d6d6d6"
    cor_preco = "#008000"
    cor_input_bg = "#ffffff"

# --- CSS VISUAL ---
st.markdown(f"""
<style>
    .stApp {{ background-color: {cor_fundo_app}; color: {cor_texto}; }}
    
    .stTextInput input, .stNumberInput input {{
        color: {cor_texto} !important;
        background-color: {cor_input_bg} !important;
    }}
    
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    [data-testid="InputInstructions"] {{display: none;}}
    
    /* CARTÃO DE PRODUTO */
    .product-card {{
        background-color: {cor_fundo_card};
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        border: 1px solid {cor_borda};
        display: flex;
        gap: 20px;
        align-items: center;
        position: relative;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }}
    .product-card:hover {{ transform: scale(1.01); border-color: #ff4b4b; }}
    
    .loja-tag {{
        position: absolute;
        bottom: 10px;
        right: 10px;
        background-color: #ff4b4b;
        color: white;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
    }}
    
    .product-img {{
        width: 100px;
        height: 100px;
        object-fit: contain;
        background-color: white;
        border-radius: 8px;
        padding: 5px;
    }}

    .product-info {{ flex: 1; }}
    .product-title {{ font-size: 15px; font-weight: bold; color: {cor_texto}; margin-bottom: 5px; line-height: 1.4; }}
    .product-price {{ font-size: 20px; color: {cor_preco}; font-weight: bold; }}
    
    /* CORREÇÃO DO BOTÃO DE BUSCA */
    div[data-testid="stFormSubmitButton"] > button {{
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        border: none;
        padding: 0.5rem;
        border-radius: 8px;
        font-weight: bold;
        transition: 0.3s;
    }}
    div[data-testid="stFormSubmitButton"] > button:hover {{
        background-color: #ff1c1c;
        color: white;
    }}
    
</style>
""", unsafe_allow_html=True)

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

criar_tabela()
st.caption("Sites: ML, Kabum, Magalu, Pichau, Dafiti, Boticário, Brastemp")
st.markdown("---")

if 'resultados' not in st.session_state: st.session_state['resultados'] = []

# --- FORMULÁRIO DE BUSCA ---
with st.form(key="search_form", border=False):
    c1, c2 = st.columns([3, 1], gap="small")
    with c1:
        produto = st.text_input("O que você procura?", placeholder="Ex: Monitor 144hz, Tênis Nike...", label_visibility="collapsed")
    with c2:
        buscar = st.form_submit_button("🔎 BUSCAR")

if buscar:
    if not produto:
        st.warning("Digite algo.")
    else:
        with st.spinner(f"Ativando robôs para '{produto}'..."):
            st.session_state['resultados'] = asyncio.run(buscar_todos_sites(produto))

if len(st.session_state['resultados']) > 0:
    st.subheader(f"Achamos {len(st.session_state['resultados'])} ofertas:")
    for i, item in enumerate(st.session_state['resultados']):
        with st.container():
            st.markdown(f"""
            <div class="product-card">
                <div class="loja-tag">{item['loja']}</div>
                <img src="{item['imagem']}" class="product-img">
                <div class="product-info">
                    <div class="product-title">{item['nome']}</div>
                    <div class="product-price">{item['preco_atual']}</div>
                    <a href="{item['link']}" target="_blank" style="text-decoration:none; color: #4da6ff; font-weight:bold;">🔗 Ver Oferta</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
            with st.expander(f"🔔 Criar Alerta"):
                with st.form(key=f"form_{i}"):
                    c1, c2 = st.columns(2)
                    email_usuario = c1.text_input("Seu E-mail")
                    try: val_sug = item['preco_num'] - 1.0 
                    except: val_sug = 0.0
                    preco_alvo = c2.number_input("Avise se baixar de (R$):", value=val_sug)
                    if st.form_submit_button("Salvar Alerta"):
                        if email_usuario:
                            salvar_no_banco(item['nome'], item['link'], email_usuario, preco_alvo, item['imagem'])
                            st.success(f"Feito!")
                        else: st.error("Faltou o e-mail.")
elif buscar: st.info("Nada encontrado.")