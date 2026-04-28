import streamlit as st
import requests
from datetime import datetime

# ---------- GEMINI ----------
def chamar_gemini(prompt, api_key):
    if not api_key:
        return "Erro: GEMINI_API_KEY não configurada nos Secrets."

    url_list = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    modelo_final = "models/gemini-1.5-flash"

    try:
        res = requests.get(url_list, timeout=10)
        if res.status_code == 200:
            for m in res.json().get("models", []):
                if "generateContent" in m.get("supportedGenerationMethods", []):
                    modelo_final = m["name"]
                    if "flash" in m["name"]:
                        break
    except:
        pass

    url_chat = f"https://generativelanguage.googleapis.com/v1beta/{modelo_final}:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        r = requests.post(url_chat, json=payload, timeout=30)
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        return f"Erro Gemini {r.status_code}: {r.text}"
    except Exception as e:
        return f"Erro ao conectar com Gemini: {str(e)}"


# ---------- PLANILHA ----------
def salvar_planilha(dados, webhook_url):
    try:
        resposta = requests.post(webhook_url, json=dados, timeout=20)
        if resposta.status_code == 200:
            return True
        return False
    except:
        return False


# ---------- CASOS ----------
casos = {
    "Caso 1 - Ambiguidade: prazo indefinido": {
        "tipo": "Ambiguidade",
        "texto": "Fale com o cliente quando puder.",
        "problema": "A frase não informa prazo. O leitor não sabe se deve falar hoje, amanhã ou em outro momento."
    },
    "Caso 2 - Ambiguidade: urgência vaga": {
        "tipo": "Ambiguidade",
        "texto": "Preciso do relatório rápido.",
        "problema": "A palavra 'rápido' é subjetiva. Pode significar em minutos, horas ou até no fim do dia."
    },
    "Caso 3 - Ambiguidade: quantidade imprecisa": {
        "tipo": "Ambiguidade",
        "texto": "Quase todo mundo confirmou presença.",
        "problema": "A frase não apresenta quantidade exata. Em ambiente profissional, números evitam dúvida."
    },
    "Caso 4 - Ambiguidade: tempo indefinido": {
        "tipo": "Ambiguidade",
        "texto": "Vamos resolver isso depois.",
        "problema": "A palavra 'depois' não define quando a ação será feita, gerando insegurança e atraso."
    },
    "Caso 5 - Ambiguidade: frequência indefinida": {
        "tipo": "Ambiguidade",
        "texto": "O produto está em falta às vezes.",
        "problema": "A expressão 'às vezes' não indica frequência. Falta precisão para orientar decisões."
    },
    "Caso 6 - Público: Diretoria": {
        "tipo": "Adaptação de linguagem",
        "texto": "A equipe teve alguns problemas operacionais e estamos ajustando algumas coisas.",
        "problema": "Para a diretoria, o texto precisa focar em resultado, impacto, dados e decisão. Está vago demais."
    },
    "Caso 7 - Público: Cliente": {
        "tipo": "Adaptação de linguagem",
        "texto": "Devido a inconsistências sistêmicas na base operacional, houve uma intercorrência.",
        "problema": "Para clientes, a linguagem deve ser clara, educada e compreensível. O texto usa termos técnicos demais."
    },
    "Caso 8 - Público: Equipe interna": {
        "tipo": "Adaptação de linguagem",
        "texto": "Solicito que os procedimentos sejam realizados conforme alinhamento estratégico prévio.",
        "problema": "Para colegas de equipe, o texto pode ser mais direto, colaborativo e prático, sem perder profissionalismo."
    },
    "Caso 9 - Público: Fornecedor": {
        "tipo": "Adaptação de linguagem",
        "texto": "Vê aí quando consegue entregar.",
        "problema": "Para fornecedores, a comunicação deve ser objetiva, formal e clara quanto a prazos e expectativas."
    }
}


# ---------- INTERFACE ----------
st.set_page_config(
    page_title="Consultoria IA - Comunicação Escrita",
    page_icon="✍️",
    layout="wide"
)

st.title("✍️ Consultoria IA - Comunicação Escrita Profissional")
st.write("Treinamento prático sobre clareza, objetividade, ambiguidade e adaptação da linguagem ao público.")

api_key = st.secrets.get("GEMINI_API_KEY")
webhook_url = st.secrets.get("SHEETS_WEBHOOK_URL")

with st.sidebar:
    st.header("👤 Identificação")
    nome = st.text_input("Nome do aluno:")

    if st.button("Reiniciar atividade"):
        st.session_state.clear()
        st.rerun()

if "tentativas" not in st.session_state:
    st.session_state.tentativas = {}

if nome:
    caso_escolhido = st.selectbox("Escolha o caso:", list(casos.keys()))
    caso = casos[caso_escolhido]

    if caso_escolhido not in st.session_state.tentativas:
        st.session_state.tentativas[caso_escolhido] = 1

    tentativa = st.session_state.tentativas[caso_escolhido]

    st.subheader("📌 Texto inicial com problema")
    st.warning(caso["texto"])

    st.subheader("🔎 Explicação do problema")
    st.info(caso["problema"])

    st.write(f"### Tentativa atual: {tentativa}")

    resposta_aluno = st.text_area(
        "Reescreva o texto de forma mais clara, profissional e adequada:",
        height=160
    )

    if st.button("Enviar para análise da consultoria IA"):
        if not resposta_aluno.strip():
            st.warning("Digite sua reformulação antes de enviar.")
        else:
            with st.spinner("A consultoria IA está analisando sua resposta..."):

                prompt = f"""
Você é um consultor especialista em comunicação empresarial escrita.

Seu papel é avaliar e orientar funcionários administrativos que precisam melhorar a clareza e o profissionalismo da comunicação.

IMPORTANTE:
- Seja educado, profissional e construtivo.
- Use linguagem não violenta.
- Seja firme quanto à qualidade da comunicação.
- NÃO reescreva o texto nas tentativas 1 e 2.
- NÃO entregue resposta pronta nas tentativas 1 e 2.
- Na tentativa 3, se ainda estiver inadequado, apresente uma melhor alternativa e peça para o aluno refazer de acordo com a orientação.

OBJETIVO DO EXERCÍCIO:
O aluno deve reformular o texto apresentado, eliminando ambiguidade ou ajustando a linguagem ao público correto.

TENTATIVA ATUAL:
{tentativa}

CRITÉRIOS DE AVALIAÇÃO:
- Clareza
- Objetividade
- Coerência
- Adequação ao público
- Tom profissional
- Precisão da informação

TEXTO INICIAL COM PROBLEMA:
{caso["texto"]}

PROBLEMA APRESENTADO AO ALUNO:
{caso["problema"]}

TEXTO REFEITO PELO ALUNO:
{resposta_aluno}

REGRAS DE RETORNO:
Se estiver satisfatório:
- Elogie de forma profissional.
- Informe que atende aos requisitos mínimos.
- Escreva claramente: Status: Satisfatório

Se não estiver satisfatório na tentativa 1 ou 2:
- Explique o que ainda precisa melhorar.
- Dê orientação clara.
- Não dê texto pronto.
- Escreva claramente: Status: Precisa melhorar

Se não estiver satisfatório na tentativa 3:
- Explique o problema.
- Mostre uma versão recomendada.
- Peça para o aluno refazer seguindo a orientação.
- Escreva claramente: Status: Precisa melhorar

FORMATO DA RESPOSTA:

Avaliação:
- ...

Sugestão da IA:
- ...

Status:
- Satisfatório ou Precisa melhorar
"""

                feedback = chamar_gemini(prompt, api_key)

                st.subheader("📋 Retorno da Consultoria IA")
                st.write(feedback)

                status = "Precisa melhorar"
                if "status: satisfatório" in feedback.lower() or "status:\n- satisfatório" in feedback.lower():
                    status = "Satisfatório"

                dados = {
                    "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "nome": nome,
                    "caso": caso_escolhido,
                    "texto_inicial": caso["texto"],
                    "texto_aluno": resposta_aluno,
                    "sugestao_ia": feedback,
                    "tentativa": tentativa,
                    "status": status
                }

                salvou = salvar_planilha(dados, webhook_url)

                if salvou:
                    st.success("Resposta salva na planilha.")
                else:
                    st.error("Erro ao salvar na planilha.")

                if status != "Satisfatório":
                    st.session_state.tentativas[caso_escolhido] += 1
                else:
                    st.success("Atividade considerada satisfatória para este caso.")
else:
    st.warning("👈 Digite seu nome na barra lateral para começar.")
