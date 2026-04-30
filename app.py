import streamlit as st
import requests
from datetime import datetime

# ---------- GEMINI ----------
def chamar_gemini(prompt, api_key):
    if not api_key:
        return "ERRO_API_KEY"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        r = requests.post(url, json=payload, timeout=30)

        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]

        elif r.status_code == 503:
            return "ERRO_503"

        else:
            return f"ERRO_{r.status_code}"

    except:
        return "ERRO_CONEXAO"


# ---------- PLANILHA ----------
def salvar_planilha(dados, webhook_url):
    try:
        r = requests.post(webhook_url, json=dados, timeout=15)
        return r.status_code == 200
    except:
        return False


# ---------- CASOS ----------
casos = [
    {"nome":"Caso 1","texto":"Fale com o cliente quando puder.","problema":"Sem prazo definido"},
    {"nome":"Caso 2","texto":"Preciso do relatório rápido.","problema":"'Rápido' é subjetivo"},
    {"nome":"Caso 3","texto":"Quase todo mundo confirmou.","problema":"Sem número exato"},
]


# ---------- CONFIG ----------
st.set_page_config(page_title="Consultoria IA", layout="wide")

# ---------- ESTADOS ----------
if "indice" not in st.session_state:
    st.session_state.indice = 0
if "tentativa" not in st.session_state:
    st.session_state.tentativa = 1
if "finalizado" not in st.session_state:
    st.session_state.finalizado = False

# ---------- SIDEBAR ----------
nome = st.sidebar.text_input("Nome do aluno")

api_key = st.secrets.get("GEMINI_API_KEY")
webhook = st.secrets.get("SHEETS_WEBHOOK_URL")

# ---------- JOGO ----------
if nome:

    caso = casos[st.session_state.indice]

    st.title("Consultoria IA")

    st.write(f"### {caso['nome']}")
    st.warning(caso["texto"])
    st.info(caso["problema"])

    st.write(f"**Tentativa:** {st.session_state.tentativa}")

    if not st.session_state.finalizado:

        resposta = st.text_area("Reescreva o texto:")

        col1, col2 = st.columns(2)

        enviar = col1.button("Enviar")
        limpar = col2.button("Refazer")

        if limpar:
            st.rerun()

        if enviar:

            if not resposta.strip():
                st.warning("Digite algo.")
            else:

                with st.spinner("Analisando..."):

                    prompt = f"""
Avalie o texto abaixo profissionalmente.

Texto original:
{caso["texto"]}

Texto aluno:
{resposta}

Se estiver bom diga:
Status: Satisfatório

Se não:
Status: Precisa melhorar
"""

                    feedback = chamar_gemini(prompt, api_key)

                    # ---------- TRATAMENTO DE ERRO ----------
                    if feedback in ["ERRO_503", "ERRO_CONEXAO"]:

                        st.error("⚠️ A IA está sobrecarregada. Tente novamente em instantes.")
                        st.info("👉 Sua tentativa NÃO foi contabilizada.")

                    elif "ERRO_" in feedback:

                        st.error("Erro na IA. Tente novamente.")
                        st.info("👉 Sua tentativa NÃO foi contabilizada.")

                    else:
                        # ---------- FLUXO NORMAL ----------
                        st.write("### Retorno da IA")
                        st.write(feedback)

                        status = "Satisfatório" if "Satisfatório" in feedback else "Precisa melhorar"

                        # salva
                        dados = {
                            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "nome": nome,
                            "caso": caso["nome"],
                            "texto": resposta,
                            "feedback": feedback,
                            "tentativa": st.session_state.tentativa,
                            "status": status
                        }

                        salvar_planilha(dados, webhook)

                        if status == "Satisfatório":
                            st.success("✔ Resposta aprovada")
                            st.session_state.finalizado = True

                        elif st.session_state.tentativa >= 3:
                            st.warning("Encerrado com orientação")
                            st.session_state.finalizado = True

                        else:
                            st.session_state.tentativa += 1

    # ---------- PRÓXIMO CASO ----------
    if st.session_state.finalizado:

        if st.button("➡️ Próximo caso"):
            st.session_state.indice += 1
            st.session_state.tentativa = 1
            st.session_state.finalizado = False
            st.rerun()
