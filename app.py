import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Void Prospect", page_icon="📽️", layout="wide")
st.markdown("<h1 style='text-align: center;'>📽️ Void Prospect</h1>", unsafe_allow_html=True)
st.markdown("---")

aba = st.radio("Navegação", ["📥 Cadastro de Leads", "📊 Funil de Vendas", "📈 Dashboard"], horizontal=True)

# Lista inicial de nichos
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

# 📥 Aba 1: Cadastro
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
            st.success("Lead salvo com sucesso!")  # Aqui entraria o envio real
            st.experimental_rerun()
        else:
            st.warning("Preencha nome, WhatsApp e nicho.")

# 📊 Aba 2: Funil de Vendas
elif aba == "📊 Funil de Vendas":
    st.subheader("🔁 Funil de Vendas")
    funil = {
        "Novo": ["Lead 1", "Lead 2"],
        "Contatado": ["Lead 3"],
        "Aguardando resposta": ["Lead 4", "Lead 5"],
        "Fechado": ["Lead 6"]
    }

    cols = st.columns(len(funil))
    for i, etapa in enumerate(funil.keys()):
        with cols[i]:
            st.markdown(f"### {etapa}")
            for lead in funil[etapa]:
                st.markdown(f"🟦 {lead}")

# 📈 Aba 3: Dashboard
elif aba == "📈 Dashboard":
    st.subheader("📊 Análise de Leads")

    resumo = {
        "Total de Leads": 23,
        "Fechados": 6,
        "Contatados": 5,
        "Aguardando resposta": 8,
        "Novos": 4
    }

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("📋 Total", resumo["Total de Leads"])
    col2.metric("✅ Fechados", resumo["Fechados"])
    col3.metric("📞 Contatados", resumo["Contatados"])
    col4.metric("⏳ Aguardando", resumo["Aguardando resposta"])
    col5.metric("🆕 Novos", resumo["Novos"])
