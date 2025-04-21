import streamlit as st
import requests
import pandas as pd
from streamlit_sortables import sort_items
from datetime import datetime

st.set_page_config(page_title="Void Prospect", layout="wide")

st.markdown("""
    <style>
        .block-container {
            padding-top: 2rem;
        }
        .stRadio > div {
            flex-direction: row;
        }
        .funil-col {
            border: 1px solid #444;
            border-radius: 8px;
            padding: 16px;
            min-height: 300px;
            background-color: #1e1e1e;
        }
        .funil-titulo {
            color: #00bcd4;
            font-weight: bold;
            margin-bottom: 12px;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

API_URL = "https://script.google.com/macros/s/AKfycbzjbQbQD1mcSc848eCnKlcSOLYwYrBLi_BdsGHAfbl1INO5IGthVUL1hugzu_xtvInETQ/exec"

# NAVIGAÇÃO
aba = st.radio("🔘 Navegação", ["📩 Cadastro de Leads", "🎯 Funil de Vendas", "📈 Dashboard"])

# FUNÇÃO - LISTAR LEADS
def listar_leads():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            st.error("Erro ao carregar dados da planilha.")
            return pd.DataFrame()
    except:
        st.error("Erro de conexão com a API.")
        return pd.DataFrame()

# FUNÇÃO - CADASTRAR LEAD
def cadastrar_lead(dados):
    try:
        r = requests.post(API_URL, json=dados)
        return r.text == "OK"
    except:
        return False

# ABA 1: CADASTRO
if aba == "📩 Cadastro de Leads":
    st.markdown("## Novo Lead")
    with st.form("cadastro"):
        col1, col2, col3 = st.columns(3)
        with col1:
            nome = st.text_input("Nome")
            whatsapp = st.text_input("WhatsApp")
            instagram = st.text_input("Instagram")
        with col2:
            nichos = ["Nutricionistas", "Estúdios", "Consultórios", "Clínicas", "Outro"]
            nicho = st.selectbox("Nicho", nichos)
            if nicho == "Outro":
                nicho = st.text_input("Informe o nicho")
            obs = st.text_input("Observações")
        with col3:
            neutra = st.text_area("Mensagem Neutra")
            informal = st.text_area("Mensagem Informal")
            inst = st.text_area("Mensagem Institucional")
        
        status = "Novo"
        data = datetime.today().strftime("%d/%m/%Y")
        enviar = st.form_submit_button("Cadastrar Lead")

        if enviar:
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
                "data": data
            }
            if cadastrar_lead(payload):
                st.success("Lead cadastrado com sucesso!")
            else:
                st.error("Erro ao cadastrar o lead.")

# FUNIL DE VENDAS COM DRAG AND DROP
elif aba == "📍 Funil de Vendas":

    st.markdown("## 🔴 Funil de Vendas com Drag & Drop")

    fases = ["Novo", "Contatado", "Aguardando resposta", "Fechado"]

    # Dados organizados por fase
    drag_data = {}
    for status in fases:
        if status in [lead["status"] for lead in leads]:
            drag_data[status] = sort_items(
                [lead for lead in leads if lead["status"] == status],
                direction="vertical",
                key="status",
                label="nome"
            )
        else:
            drag_data[status] = []

    result = dnd_grid(
        drag_data,
        layout=fases,
        spacing=20,
        dot_color="#FA5252",
        background="#1c1c1e",
        columns=4
    )

    # Atualiza status se houver alteração
    if result:
        for novo_status, cards in result.items():
            for card in cards:
                for lead in leads:
                    if lead["nome"] == card["nome"]:
                        lead["status"] = novo_status
        atualizar_planilha(leads)

# ABA 3: DASHBOARD
elif aba == "📈 Dashboard":
    st.markdown("## 📊 Análise de Leads")
    df = listar_leads()
    if df.empty:
        st.warning("Sem dados.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total de Leads", len(df))
        with col2:
            st.metric("Leads Fechados", len(df[df["status"] == "Fechado"]))

        st.markdown("### Leads por Status")
        status_contagem = df["status"].value_counts().reset_index()
        status_contagem.columns = ["Status", "Quantidade"]
        tipo = st.selectbox("Tipo de Gráfico", ["Barra", "Pizza", "Linha"])
        
        if tipo == "Barra":
            st.bar_chart(status_contagem.set_index("Status"))
        elif tipo == "Pizza":
            st.pyplot(status_contagem.plot.pie(y="Quantidade", labels=status_contagem["Status"], autopct="%1.1f%%", figsize=(5, 5)).figure)
        elif tipo == "Linha":
            st.line_chart(status_contagem.set_index("Status"))
