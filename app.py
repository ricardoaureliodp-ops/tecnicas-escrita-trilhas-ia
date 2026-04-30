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
        return resposta.status_code == 200
    except:
        return False


# ---------- CASOS ----------
casos = [
    {
        "nome": "Caso 1 - Ambiguidade: prazo indefinido",
        "texto": "Fale com o cliente quando puder.",
        "problema": "A frase não informa prazo. O leitor não sabe se deve falar hoje, amanhã ou em outro momento."
    },
    {
        "nome": "Caso 2 - Ambiguidade: urgência vaga",
        "texto": "Preciso do relatório rápido.",
        "problema": "A palavra 'rápido' é subjetiva. Pode significar em minutos, horas ou até no fim do dia."
    },
    {
        "nome": "Caso 3 - Ambiguidade: quantidade imprecisa",
        "texto": "Quase todo mundo confirmou presença.",
        "problema": "A frase não apresenta quantidade exata. Em ambiente profissional, números evitam dúvida."
    },
    {
        "nome": "Caso 4 - Ambiguidade: tempo indefinido",
        "texto": "Vamos resolver isso depois.",
        "problema": "A palavra 'depois' não define quando a ação será feita, gerando insegurança e atraso."
    },
    {
        "nome": "Caso 5 - Ambiguidade: frequência indefinida",
        "texto": "O produto está em falta às vezes.",
        "problema": "A expressão 'às vezes' não indica frequência. Falta precisão para orientar decisões."
    },
    {
        "nome": "Caso 6 - Público: Diretoria",
        "texto": "A equipe teve alguns problemas operacionais e estamos ajustando algumas coisas.",
        "problema": "Para a diretoria, o texto precisa focar em resultado, impacto, dados e decisão. Está vago demais."
    },
    {
        "nome": "Caso 7 - Público: Cliente",
        "texto": "Devido a inconsistências sistêmicas na base operacional, houve uma intercorrência.",
        "problema": "Para clientes, a linguagem deve ser clara, educada e compreensível. O texto usa termos técnicos demais."
    },
    {
        "nome": "Caso 8 - Público: Equipe interna",
        "texto": "Solicito que os procedimentos sejam realizados conforme alinhamento estratégico prévio.",
        "problema": "Para colegas de equipe, o texto pode ser mais direto, colaborativo e prático, sem perder profissionalismo."
    },
    {
        "nome": "Caso 9 - Público: Fornecedor",
        "texto": "Vê aí quando consegue entregar.",
        "problema": "Para fornecedores, a comunicação deve ser objetiva, formal e clara quanto a prazos e expectativas."
    }
]


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


# ---------- ESTADOS ----------
if "indice_caso" not in st.session_state:
    st.session_state.indice_caso = 0

if "tentativa" not in st.session_state:
    st.session_state.tentativa = 1

if "resposta_temp" not in st.session_state:
    st.session_state.resposta_temp = ""

if "ultimo_feedback" not in st.session_state:
    st.session_state.ultimo_feedback = ""

if "caso_finalizado" not in st.session_state:
    st.session_state.caso_finalizado = False

if "atividade_finalizada" not in st.session_state:
    st.session_state.atividade_finalizada = False


# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("👤 Identificação")
    nome = st.text_input("Nome do aluno:")

    if st.button("Reiniciar atividade"):
        st.session_state.clear()
        st.rerun()


# ---------- JOGO ----------
if not nome:
    st.warning("👈 Digite seu nome na barra lateral para começar.")

else:
    total_casos = len(casos)

    if st.session_state.atividade_finalizada:
        st.success("🎉 Parabéns! Você concluiu todos os casos da atividade.")
        st.info("Suas respostas foram registradas na planilha.")
    else:
        caso = casos[st.session_state.indice_caso]

        st.progress((st.session_state.indice_caso) / total_casos)
        st.write(f"### Progresso: Caso {st.session_state.indice_caso + 1} de {total_casos}")

        st.subheader(f"📚 {caso['nome']}")

        st.subheader("📌 Texto inicial com problema")
        st.warning(caso["texto"])

        st.subheader("🔎 Explicação do problema")
        st.info(caso["problema"])

        st.write(f"### Tentativa atual: {st.session_state.tentativa}")

        if st.session_state.caso_finalizado:
            st.success("✅ Este caso foi encerrado. Clique em **Próximo caso** para continuar.")
        elif st.session_state.tentativa == 1:
            st.info("🟢 Primeira tentativa: reformule o texto com clareza e profissionalismo.")
        elif st.session_state.tentativa == 2:
            st.warning("🟡 Segunda tentativa: atenção aos pontos apontados pela IA. Ainda não será entregue resposta pronta.")
        elif st.session_state.tentativa == 3:
            st.error("🔴 Terceira tentativa: se ainda não estiver adequado, a IA apresentará a versão recomendada e este caso será encerrado.")

        if not st.session_state.caso_finalizado:
            resposta_aluno = st.text_area(
                "Reescreva o texto de forma mais clara, profissional e adequada:",
                value=st.session_state.resposta_temp,
                height=160,
                key=f"texto_caso_{st.session_state.indice_caso}_tentativa_{st.session_state.tentativa}"
            )

            col1, col2 = st.columns([1, 1])

            with col1:
                enviar = st.button("📩 Enviar para análise da consultoria IA")

            with col2:
                refazer = st.button("🔄 Refazer tentativa")

            if refazer:
                st.session_state.resposta_temp = ""
                st.rerun()

            if enviar:
                if not resposta_aluno.strip():
                    st.warning("Digite sua reformulação antes de enviar.")
                else:
                    st.session_state.resposta_temp = resposta_aluno

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
- Na tentativa 3, se ainda estiver inadequado, apresente uma versão recomendada e informe que o aluno deve seguir para o próximo caso após revisar a orientação.

OBJETIVO DO EXERCÍCIO:
O aluno deve reformular o texto apresentado, eliminando ambiguidade ou ajustando a linguagem ao público correto.

TENTATIVA ATUAL:
{st.session_state.tentativa}

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

Se for tentativa 3:
- Avalie a resposta.
- Se ainda não estiver satisfatória, mostre uma versão recomendada.
- Explique por que a versão recomendada é melhor.
- Peça para o aluno seguir para o próximo caso.
- Escreva claramente: Status: Encerrado com orientação

FORMATO DA RESPOSTA:

Avaliação:
- ...

Sugestão da IA:
- ...

Versão recomendada:
- Somente preencher na terceira tentativa, se necessário.

Status:
- Satisfatório, Precisa melhorar ou Encerrado com orientação
"""

                        feedback = chamar_gemini(prompt, api_key)
                        st.session_state.ultimo_feedback = feedback

                        st.subheader("📋 Retorno da Consultoria IA")
                        st.write(feedback)

                        feedback_lower = feedback.lower()

                        if "status: satisfatório" in feedback_lower or "status:\n- satisfatório" in feedback_lower:
                            status = "Satisfatório"
                        elif st.session_state.tentativa >= 3:
                            status = "Encerrado com orientação"
                        else:
                            status = "Precisa melhorar"

                        dados = {
                            "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                            "nome": nome,
                            "caso": caso["nome"],
                            "texto_inicial": caso["texto"],
                            "texto_aluno": resposta_aluno,
                            "sugestao_ia": feedback,
                            "tentativa": st.session_state.tentativa,
                            "status": status
                        }

                        salvou = salvar_planilha(dados, webhook_url)

                        if salvou:
                            st.success("Resposta salva na planilha.")
                        else:
                            st.error("Erro ao salvar na planilha.")

                        if status == "Satisfatório":
                            st.session_state.caso_finalizado = True
                            st.success("✅ Resposta satisfatória. Clique em **Próximo caso** para continuar.")

                        elif st.session_state.tentativa >= 3:
                            st.session_state.caso_finalizado = True
                            st.warning("📌 Este caso foi encerrado com orientação. Clique em **Próximo caso** para continuar.")

                        else:
                            st.session_state.tentativa += 1
                            if st.session_state.tentativa == 2:
                                st.warning("Clique em **Refazer tentativa** para limpar o campo e escrever sua segunda tentativa.")
                            elif st.session_state.tentativa == 3:
                                st.warning("Clique em **Refazer tentativa** para limpar o campo e escrever sua terceira tentativa. Na terceira, a IA poderá apresentar uma versão recomendada.")

        if st.session_state.ultimo_feedback:
            st.divider()
            st.subheader("🧾 Último retorno recebido")
            st.write(st.session_state.ultimo_feedback)

        if st.session_state.caso_finalizado:
            st.divider()

            if st.session_state.indice_caso < total_casos - 1:
                if st.button("➡️ Próximo caso"):
                    st.session_state.indice_caso += 1
                    st.session_state.tentativa = 1
                    st.session_state.resposta_temp = ""
                    st.session_state.ultimo_feedback = ""
                    st.session_state.caso_finalizado = False
                    st.rerun()
            else:
                if st.button("🏁 Finalizar atividade"):
                    st.session_state.atividade_finalizada = True
                    st.rerun()
