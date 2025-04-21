
import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime
from streamlit_extras.stylable_container import stylable_container
from streamlit_dnd_card import dnd_grid, sort_items

# URL da API Google Apps Script
API_URL = "https://script.google.com/macros/s/AKfycbzjbQbQD1mcSc848eCnKlcSOLYwYrBLi_BdsGHAfbl1INO5IGthVUL1hugzu_xtvInETQ/exec"

# Funções auxiliares
def carregar_dados():
    try:
        resposta = requests.get(API_URL)
        if resposta.status_code == 200:
            return resposta.json()
        else:
            return []
    except:
        return []

def cadastrar_lead(dados):
    try:
        resposta = requests.post(API_URL, json=dados)
        return resposta.status_code == 200
    except:
        return False

def atualizar_planilha(leads):
    try:
        requests.post(API_URL, json={"leads": leads})
    except:
        pass

# Configuração da página
st.set_page_config(page_title="Void Prospect", layout="wide")
st.markdown("<h1 style='color:white;'>Void Prospect</h1>", unsafe_allow_html=True)

# Navegação principal
aba = st.radio("Navegação", ["📬 Cadastro de Leads", "📍 Funil de Vendas", "📈 Dashboard"], horizontal=True)

# Carregamento inicial de dados
leads = carregar_dados()

# AGENDA 1 - Cadastro
if aba == "📬 Cadastro de Leads":
    st.subheader("Cadastro de Leads")
    with st.form("formulario_lead"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome")
            whatsapp = st.text_input("WhatsApp")
            instagram = st.text_input("Instagram")
            nicho = st.text_input("Nicho")
        with col2:
            obs = st.text_area("Observações")
            neutra = st.text_area("Mensagem Neutra")
            informal = st.text_area("Mensagem Informal")
            inst = st.text_area("Mensagem Institucional")
        status = st.selectbox("Status", ["Novo", "Contatado", "Aguardando resposta", "Fechado"])
        data = st.date_input("Data de Cadastro", value=datetime.today()).strftime("%Y/%m/%d")
        enviado = st.form_submit_button("Cadastrar")

    if enviado:
        novo = {
            "nome": nome,
            "whatsapp": whatsapp,
            "instagram": instagram,
            "nicho": nicho,
            "obs": obs,
            "neutra": neutra,
            "informal": informal,
            "inst": inst,
            "status": status,
            "data": data
        }
        sucesso = cadastrar_lead(novo)
        if sucesso:
            st.success("Lead cadastrado com sucesso!")
        else:
            st.error("Erro ao cadastrar.")

# AGENDA 2 - Funil de Vendas com Drag and Drop
elif aba == "📍 Funil de Vendas":
    st.markdown("## 🎯 Funil de Vendas com Drag & Drop")

    fases = ["Novo", "Contatado", "Aguardando resposta", "Fechado"]
    drag_data = {fase: [] for fase in fases}
    for lead in leads:
        status = lead.get("status", "Novo")
        if status not in drag_data:
            drag_data[status] = []
        drag_data[status].append({
            "nome": lead["nome"],
            "data": lead["data"],
            "status": status
        })

    # Estilo visual
    st.markdown("""
    <style>
    .st-dnd-container { gap: 32px !important; }
    .st-dnd-card { background-color: #111; color: white; border-radius: 8px; margin-bottom: 6px; padding: 8px; }
    .st-dnd-header { font-weight: bold; color: #00BFFF; font-size: 18px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

    result = dnd_grid(
        drag_data,
        layout=fases,
        columns=4,
        spacing=30,
        show_labels=True,
        label_style={"font-weight": "bold", "color": "#00BFFF"},
        card_style={"border-radius": "6px", "padding": "8px", "background-color": "#262730"},
        container_style={"background-color": "#1e1e1e", "padding": "12px"},
        draggable=True
    )

    # Atualizar o status
    if result:
        for novo_status, cards in result.items():
            for card in cards:
                for lead in leads:
                    if lead["nome"] == card["nome"]:
                        lead["status"] = novo_status
        atualizar_planilha(leads)

# AGENDA 3 - Dashboard
elif aba == "📈 Dashboard":
    st.markdown("## 📊 Dashboard de Análise de Leads")

    df = pd.DataFrame(leads)
    if df.empty:
        st.info("Nenhum dado encontrado.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(px.pie(df, names="status", title="Distribuição de Leads"))
        with col2:
            st.plotly_chart(px.bar(df, x="nicho", title="Leads por Nicho", color="status"))
