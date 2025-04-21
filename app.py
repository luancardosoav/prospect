import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_sortables import sort_items

st.set_page_config(page_title="Void Prospect", page_icon="📽️", layout="wide")
st.markdown("<h1 style='text-align: center;'>📽️ Void Prospect</h1>", unsafe_allow_html=True)
st.markdown("---")

API_URL = "https://script.google.com/macros/s/AKfycbzjbQbQD1mcSc848eCnKlcSOLYwYrBLi_BdsGHAfbl1INO5IGthVUL1hugzu_xtvInETQ/exec"

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

@st.cache_data(ttl=60)
def buscar_leads():
    try:
        r = requests.get(API_URL, timeout=10)
        if r.status_code == 200:
            return pd.DataFrame(r.json())
        else:
            return pd.DataFrame()
    except:
        return pd.DataFrame()

# 📥 Cadastro de Leads
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
            try:
                r = requests.post(API_URL, json=payload, timeout=10)
                if r.status_code == 200:
                    st.success("Lead salvo com sucesso!")
                    st.experimental_rerun()
                else:
                    st.error("Erro ao salvar lead.")
            except:
                st.error("Erro de conexão com a API.")
        else:
            st.warning("Preencha nome, WhatsApp e nicho.")
            # 📊 Funil de Vendas com Drag & Drop e Visual
elif aba == "📊 Funil de Vendas":
    st.subheader("🧲 Funil de Vendas com Drag & Drop")
    df = buscar_leads()

    if df.empty:
        st.info("Nenhum lead encontrado ou erro ao carregar.")
    else:
        fases = ["Novo", "Contatado", "Aguardando resposta", "Fechado"]
        fase_to_leads = {fase: df[df["status"] == fase]["nome"].tolist() for fase in fases}
        st.write("💡 Arraste os cards entre colunas para atualizar o status.")
        cols = st.columns(len(fases))
        novos_status = {}

        for i, fase in enumerate(fases):
            with cols[i]:
                st.markdown(f"<div style='padding:10px; background-color:#1e1e1e; border:1px solid #444; border-radius:8px; min-height:300px'>", unsafe_allow_html=True)
                st.markdown(f"<h4 style='text-align:center; color:#00bfff'>{fase}</h4>", unsafe_allow_html=True)
                updated = sort_items(fase_to_leads[fase], key=f"fase_{fase}")
                novos_status[fase] = updated
                st.markdown("</div>", unsafe_allow_html=True)

        for fase, lista in novos_status.items():
            for nome in lista:
                atual = df[df["nome"] == nome]["status"].values
                if len(atual) > 0 and atual[0] != fase:
                    linha = df[df["nome"] == nome].iloc[0]
                    payload = {
                        "nome": linha["nome"],
                        "whatsapp": linha["whatsapp"],
                        "instagram": linha["instagram"],
                        "nicho": linha["nicho"],
                        "obs": linha["obs"],
                        "neutra": linha["neutra"],
                        "informal": linha["informal"],
                        "inst": linha["inst"],
                        "status": fase,
                        "data": linha["data"]
                    }
                    try:
                        requests.post(API_URL, json=payload, timeout=10)
                    except:
                        st.error(f"Erro ao atualizar {nome}")

# 📈 Dashboard
elif aba == "📈 Dashboard":
    st.subheader("📊 Análise de Leads")
    df = buscar_leads()

    if df.empty:
        st.info("Nenhum dado disponível.")
    else:
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
