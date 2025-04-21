import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Void Prospect", page_icon="📽️", layout="wide")
st.markdown("<h1 style='text-align: center;'>📽️ Void Prospect</h1>", unsafe_allow_html=True)
st.markdown("---")

API_URL = "https://script.google.com/macros/library/d/1pQ4UXYHljUz0zKk8-gxmwPT5crGUcdikZaGuwJoKB_szGAqUuX2IbJnY/1"

aba = st.radio("Navegação", ["📥 Cadastro de Leads", "📊 Funil de Vendas", "📈 Dashboard"], horizontal=True)

if "nichos" not in st.session_state:
    st.session_state.nichos = [
        "Clínicas odontológicas", "Nutricionistas", "Personal trainers",
        "Lojas físicas", "Restaurantes", "Salões de beleza",
        "Artesãos", "Estúdios de tatuagem", "Arquitetos", "E-commerces locais"
    ]

def gerar_mensagem(nicho, tipo):
    base = {
        "neutro": "Oi, tudo bem? Vi teu negócio de {} e pensei em como vídeos podem destacar o teu trabalho.",
        "informal": "E aí! Vi que tu trabalha com {} e já imaginei uns vídeos massa pra atrair mais clientes.",
        "institucional": "Olá! Seu negócio no segmento de {} tem grande potencial para crescer com vídeos estratégicos."
    }
    return base[tipo].format(nicho.lower())

def buscar_leads():
    try:
        r = requests.get(API_URL)
        if r.status_code == 200:
            return pd.DataFrame(r.json())
        else:
            st.error("Erro ao buscar dados.")
            return pd.DataFrame()
    except:
        st.error("Erro de conexão com a API.")
        return pd.DataFrame()

# 📥 Cadastro
if aba == "📥 Cadastro de Leads":
    st.subheader("➕ Novo Lead")

    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Nome do Lead")
        whatsapp = st.text_input("WhatsApp (apenas números)", max_chars=15)
        instagram = st.text_input("Instagram ou site")
        observacoes = st.text_area("Observações")

    with col2:
        tipo_nicho = st.selectbox("Escolha ou adicione um nicho", st.session_state.nichos + ["➕ Adicionar novo nicho"])
        if tipo_nicho == "➕ Adicionar novo nicho":
            novo = st.text_input("Digite o novo nicho")
            if novo and novo not in st.session_state.nichos:
                st.session_state.nichos.append(novo)
                tipo_nicho = novo

        status = st.selectbox("Status", ["Novo", "Contatado", "Aguardando resposta", "Fechado"])
        data = datetime.now().strftime("%d/%m/%Y")

    st.divider()
    st.markdown("### 💬 Mensagens sugeridas")

    coln1, coln2, coln3 = st.columns(3)
    with coln1:
        msg_neutra = st.text_area("📌 Neutro", value=gerar_mensagem(tipo_nicho, "neutro"), height=100)
        if st.button("🔁 Gerar nova (Neutro)"):
            st.experimental_rerun()

    with coln2:
        msg_informal = st.text_area("😎 Informal", value=gerar_mensagem(tipo_nicho, "informal"), height=100)
        if st.button("🔁 Gerar nova (Informal)"):
            st.experimental_rerun()

    with coln3:
        msg_inst = st.text_area("🏢 Institucional", value=gerar_mensagem(tipo_nicho, "institucional"), height=100)
        if st.button("🔁 Gerar nova (Institucional)"):
            st.experimental_rerun()

    if st.button("💾 Salvar Lead"):
        if nome and whatsapp and tipo_nicho:
            payload = {
                "nome": nome,
                "whatsapp": whatsapp,
                "instagram": instagram,
                "nicho": tipo_nicho,
                "obs": observacoes,
                "neutra": msg_neutra,
                "informal": msg_informal,
                "inst": msg_inst,
                "status": status,
                "data": data
            }
            r = requests.post(API_URL, json=payload)
            if r.status_code == 200:
                st.success("Lead salvo com sucesso!")
                st.experimental_rerun()
            else:
                st.error("Erro ao salvar lead.")
        else:
            st.warning("Preencha nome, WhatsApp e nicho.")

# 📊 Funil de Vendas
elif aba == "📊 Funil de Vendas":
    st.subheader("🔁 Funil de Vendas")
    df = buscar_leads()

    if not df.empty:
        funil_cols = ["Novo", "Contatado", "Aguardando resposta", "Fechado"]
        cols = st.columns(len(funil_cols))
        for i, etapa in enumerate(funil_cols):
            with cols[i]:
                st.markdown(f"### {etapa}")
                leads = df[df["status"] == etapa]
                for idx, row in leads.iterrows():
                    st.write(f"🟦 {row['nome']}")

        st.caption("⚠️ Em breve: arrastar para trocar de fase direto aqui.")

# 📈 Dashboard
elif aba == "📈 Dashboard":
    st.subheader("📊 Análise de Leads")
    df = buscar_leads()

    if not df.empty:
        st.markdown("### Leads por Status")
        tipo1 = st.selectbox("Tipo de gráfico", ["Barras", "Pizza", "Linha"], key="tipo1")
        df1 = df["status"].value_counts().reset_index()
        df1.columns = ["status", "quantidade"]

        if tipo1 == "Barras":
            st.plotly_chart(px.bar(df1, x="status", y="quantidade", color="status"))
        elif tipo1 == "Pizza":
            st.plotly_chart(px.pie(df1, names="status", values="quantidade"))
        else:
            st.plotly_chart(px.line(df1, x="status", y="quantidade"))

        st.markdown("### Leads por Nicho")
        tipo2 = st.selectbox("Tipo de gráfico", ["Barras", "Pizza", "Linha"], key="tipo2")
        df2 = df["nicho"].value_counts().reset_index()
        df2.columns = ["nicho", "quantidade"]

        if tipo2 == "Barras":
            st.plotly_chart(px.bar(df2, x="nicho", y="quantidade", color="nicho"))
        elif tipo2 == "Pizza":
            st.plotly_chart(px.pie(df2, names="nicho", values="quantidade"))
        else:
            st.plotly_chart(px.line(df2, x="nicho", y="quantidade"))
