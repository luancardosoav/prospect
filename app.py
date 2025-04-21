import streamlit as st
import pandas as pd
import pygsheets
import json
from datetime import datetime

st.set_page_config(page_title="Void CRM", page_icon="📽️", layout="wide")
st.markdown("<h1 style='text-align: center;'>📲 Void - Prospecção Inteligente</h1>", unsafe_allow_html=True)

# Conexão com pygsheets
@st.cache_resource
def connect_sheet():
    creds_dict = json.loads(st.secrets["google"]["credentials"])
    gc = pygsheets.authorize(custom_credentials=pygsheets.authorize(client_secret=creds_dict, no_cache=True))
    sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1DLB07ODbEYqByMG-FjUcxITtFxt9HD7wvJmnPrZzOBM/edit")
    wks = sh[0]  # Primeira aba
    return wks

sheet = connect_sheet()

def salvar_lead(data):
    sheet.append_table(data, start="A2", dimension="ROWS", overwrite=False)

st.subheader("➕ Novo Lead")

col1, col2 = st.columns(2)
with col1:
    nome = st.text_input("Nome do Lead")
    whatsapp = st.text_input("WhatsApp (apenas números)", max_chars=15)
    instagram = st.text_input("Instagram ou site")
    observacoes = st.text_area("Observações")

with col2:
    nicho = st.selectbox("Nicho", [
        "Clínicas odontológicas", "Nutricionistas", "Personal trainers",
        "Lojas físicas", "Restaurantes", "Salões de beleza",
        "Artesãos", "Estúdios de tatuagem", "Arquitetos", "E-commerces locais"
    ])
    status = st.selectbox("Status", ["Novo", "Contatado", "Aguardando resposta", "Fechado"])
    data = datetime.now().strftime("%d/%m/%Y")

mensagens_padrao = {
    "Clínicas odontológicas": "Oi, tudo bem? Vi tua clínica e pensei em como vídeos podem aumentar a confiança do paciente antes da consulta...",
    "Nutricionistas": "Oi! Vi teu conteúdo e pensei como vídeos poderiam te posicionar como referência na nutrição...",
    "Personal trainers": "Fala! Vi teus treinos e pensei como vídeos certos podem atrair novos alunos e reforçar tua autoridade...",
    "Lojas físicas": "Oi! Vi o perfil da tua loja e imaginei vídeos mostrando produtos, bastidores e promoções...",
    "Restaurantes": "Olá! Vídeos mostrando pratos e a experiência do restaurante atraem novos clientes todos os dias...",
    "Salões de beleza": "Oi! Mostrar transformação em vídeo atrai muito mais clientes pro teu salão...",
    "Artesãos": "Oi! Mostrar o processo de criação das tuas peças em vídeo gera conexão real com quem compra...",
    "Estúdios de tatuagem": "Fala! Mostrar o processo da tattoo, reação do cliente e tua arte em vídeo é chave pra atrair novos clientes...",
    "Arquitetos": "Oi! Mostrar projetos antes/depois, ideias e bastidores do teu trabalho em vídeo atrai muito mais atenção...",
    "E-commerces locais": "Oi! Vídeos mostrando o uso real dos teus produtos aumentam a conversão e criam autoridade..."
}

msg_neutra = mensagens_padrao.get(nicho, "")
msg_informal = msg_neutra.replace("Oi", "E aí").replace("Olá", "Fala")
msg_institucional = msg_neutra.replace("Oi", "Olá").replace("Fala", "Olá")

st.markdown("### 💬 Mensagens sugeridas")
st.code("📌 Neutro:\n" + msg_neutra)
st.code("😎 Informal:\n" + msg_informal)
st.code("🏢 Institucional:\n" + msg_institucional)

if st.button("💾 Salvar Lead"):
    if nome and whatsapp and nicho:
        salvar_lead([
            nome, whatsapp, instagram, nicho, observacoes,
            msg_neutra, msg_informal, msg_institucional,
            status, data
        ])
        st.success("Lead salvo com sucesso!")
    else:
        st.warning("Preencha nome, WhatsApp e nicho.")
