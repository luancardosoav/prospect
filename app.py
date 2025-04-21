import streamlit as st
import requests
import pandas as pd
from streamlit_sortables import sort_items
from datetime import datetime

st.set_page_config(layout="wide", page_title="Void Prospect")
st.markdown("<style>body { background-color: #111; color: white; }</style>", unsafe_allow_html=True)

# Funções
API_URL = "https://script.google.com/macros/s/AKfycbzjbQbQD1mcSc848eCnKlcSOLYwYrBLi_BdsGHAfbl1INO5IGthVUL1hugzu_xtvInETQ/exec"

def carregar_leads():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            st.error("Erro ao carregar os leads.")
            return pd.DataFrame()
    except Exception as e:
        st.error("Erro ao conectar com a API.")
        return pd.DataFrame()

def atualizar_status_lead(nome, novo_status):
    try:
        response = requests.post(API_URL, json={"update": True, "nome": nome, "status": novo_status})
        if response.status_code != 200:
            st.error("Erro ao atualizar o status.")
    except Exception as e:
        st.error("Erro ao atualizar o status.")

# Layout de navegação
aba = st.radio("📬 Navegação", ["Cadastro de Leads", "📍 Funil de Vendas com Drag & Drop", "📊 Dashboard"], horizontal=True)

if aba == "Cadastro de Leads":
    st.title("Cadastro de Leads")
    with st.form("cadastro_form"):
        nome = st.text_input("Nome")
        whatsapp = st.text_input("WhatsApp")
        instagram = st.text_input("Instagram")
        nicho = st.text_input("Nicho")
        obs = st.text_area("Observações")
        neutra = st.text_area("Mensagem Neutra")
        informal = st.text_area("Mensagem Informal")
        inst = st.text_area("Mensagem Institucional")
        status = st.selectbox("Status", ["Novo", "Contatado", "Aguardando resposta", "Fechado"])
        data = st.date_input("Data de Cadastro", value=datetime.today())
        submit = st.form_submit_button("Cadastrar")

    if submit:
        payload = {
            "nome": nome,
            "whatsapp": whatsapp,
            "instagram": instagram,
            "nicho": nicho,
            "obs": obs,
            "neutra": neutra,
            "informal": informal,
            "inst": inst,
            "status": status,
            "data": data.strftime("%d/%m/%Y")
        }
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            st.success("Lead cadastrado com sucesso!")
        else:
            st.error("Erro ao cadastrar o lead.")

elif aba == "📍 Funil de Vendas com Drag & Drop":
    st.markdown("## 🧲 Funil de Vendas com Drag & Drop")

    df = carregar_leads()
    if df.empty:
        st.warning("Nenhum lead encontrado.")
        st.stop()

    col1, col2, col3, col4 = st.columns(4)
    status_cols = {
        "Novo": col1,
        "Contatado": col2,
        "Aguardando resposta": col3,
        "Fechado": col4,
    }

    with col1:
        st.markdown("### Novo")
    with col2:
        st.markdown("### Contatado")
    with col3:
        st.markdown("### Aguardando resposta")
    with col4:
        st.markdown("### Fechado")

    drag_data = {}
    for status in status_cols:
        leads = df[df["status"] == status]["nome"].tolist()
        with status_cols[status]:
            drag_data[status] = sort_items(leads, direction="vertical", key=status, label="")

    for status, nomes in drag_data.items():
        for nome in nomes:
            linha = df[df["nome"] == nome]
            if not linha.empty and linha.iloc[0]["status"] != status:
                atualizar_status_lead(nome, status)

elif aba == "📊 Dashboard":
    st.title("Dashboard")
    df = carregar_leads()
    if df.empty:
        st.warning("Nenhum lead encontrado.")
    else:
        st.write("Total de Leads:", len(df))
        st.bar_chart(df["status"].value_counts())
