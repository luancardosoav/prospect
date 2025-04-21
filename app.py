import streamlit as st
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Teste de Acesso - Void", page_icon="🔐", layout="wide")
st.title("🔍 Teste de acesso da conta de serviço ao Google Sheets")

try:
    # Autenticação
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = json.loads(st.secrets["google"]["credentials"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    # Listar planilhas acessíveis
    planilhas = client.openall()
    st.success("✅ Conexão com Google Sheets realizada com sucesso!")
    st.markdown("### 📋 Planilhas acessíveis pela conta de serviço:")
    for p in planilhas:
        st.write("🔹", p.title)

except Exception as e:
    st.error(f"❌ Erro ao conectar com a conta de serviço ou acessar as planilhas: {e}")
