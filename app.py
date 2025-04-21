from datetime import datetime
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from streamlit_extras.stylable_container import stylable_container
from streamlit_sortables import sort_items

# URL da API do Google Apps Script
API_URL = "https://script.google.com/macros/s/AKfycbzjbQbQD1mcSc848eCnKlcSOLYwYrBLi_BdsGHAfbI1INO5IGthVUL1hugzu_xtvInETQ/exec"

st.set_page_config(page_title="Void Prospect", layout="wide", page_icon="📋")
st.markdown("<h1 style='color: white;'>Void Prospect</h1>", unsafe_allow_html=True)

menu = st.radio("📍 Navegação", ["Cadastro de Leads", "Funil de Vendas", "Dashboard"], horizontal=True)

# 🔍 Função para buscar dados
def get_leads():
    try:
        res = requests.get(API_URL)
        return res.json()
    except:
        return []

# 📋 Aba 1 - Cadastro
if menu == "Cadastro de Leads":
    st.subheader("📋 Cadastro de Leads")
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Nome")
        whatsapp = st.text_input("WhatsApp")
        instagram = st.text_input("Instagram")
        nicho = st.text_input("Nicho")
        obs = st.text_area("Observações")
    with col2:
        neutra = st.text_area("Mensagem Neutra")
        informal = st.text_area("Mensagem Informal")
        inst = st.text_area("Mensagem Institucional")
        status = st.selectbox("Status", ["Novo", "Contatado", "Aguardando resposta", "Fechado"])
        data = st.date_input("Data de Cadastro", value=datetime.now()).strftime("%Y-%m-%d")

    if st.button("Cadastrar"):
        lead = {
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
        try:
            r = requests.post(API_URL, json=lead)
            if r.text == "OK":
                st.success("Lead cadastrado com sucesso!")
            else:
                st.error("Erro ao cadastrar lead.")
        except:
            st.error("Erro de conexão com a API.")

# 🧩 Aba 2 - Funil
elif menu == "Funil de Vendas":
    st.subheader("🎯 Funil de Vendas com Drag & Drop")

    leads = get_leads()
    if not leads:
        st.warning("Nenhum lead encontrado.")
    else:
        fases = ["Novo", "Contatado", "Aguardando resposta", "Fechado"]
        colunas = st.columns(len(fases))

        status_map = {f: [] for f in fases}
        for lead in leads:
            status_map.get(lead["status"], []).append(lead["nome"])

        new_order = {}
        for i, fase in enumerate(fases):
            with stylable_container(
                key=f"col_{fase}",
                css_styles="""
                    border: 1px solid #444;
                    border-radius: 8px;
                    padding: 10px;
                    background-color: #202020;
                    margin: 5px;
                """):
                colunas[i].markdown(f"### {fase}")
                new_order[fase] = sort_items(status_map[fase], direction="vertical", key=f"sort_{fase}")

        st.markdown("<small>🔁 Em breve será possível mover e atualizar os status em tempo real.</small>", unsafe_allow_html=True)

# 📊 Aba 3 - Dashboard
elif menu == "Dashboard":
    st.subheader("📊 Dashboard de Análise de Leads")

    leads = get_leads()
    if not leads:
        st.warning("Nenhum dado disponível para análise.")
    else:
        df = pd.DataFrame(leads)

        col1, col2 = st.columns(2)
        with col1:
            tipo = st.selectbox("Selecionar tipo de gráfico", ["Barra", "Pizza", "Linha"])
        with col2:
            st.metric("Total de Leads", len(df))
            st.metric("Leads Novos", (df["status"] == "Novo").sum())

        base = df["status"].value_counts().reset_index()
        base.columns = ["Status", "Quantidade"]

        if tipo == "Barra":
            fig = px.bar(base, x="Status", y="Quantidade", color="Status", title="Leads por Status")
        elif tipo == "Pizza":
            fig = px.pie(base, names="Status", values="Quantidade", title="Distribuição por Status")
        else:
            df_sorted = df.groupby("data")["nome"].count().reset_index(name="Leads")
            fig = px.line(df_sorted, x="data", y="Leads", title="Leads por Data")

        st.plotly_chart(fig, use_container_width=True)
