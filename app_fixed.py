import streamlit as st
import re
import json
import time
import io
import asyncio
from datetime import datetime
from service.azure_vision import extrair_texto_pdf
from agents.scraper_linkedin import get_linkedin_profile
from agents.relatorio import gerar_relatorio_preparacao_vaga
from llama_index.core.agent.workflow import ReActAgent

MAX_FILE_SIZE_MB = 2


def pagina_busca_vagas():
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    st.title("🔍 Busca de Vagas")

    # Garantir que temos todas as variáveis de estado necessárias
    if "relatorio_ativo" not in st.session_state:
        st.session_state.relatorio_ativo = None

    if "relatorios" not in st.session_state:
        st.session_state.relatorios = {}

    if "vagas_validas" not in st.session_state:
        st.session_state.vagas_validas = []

    if "dados_candidato" not in st.session_state:
        st.error("Você precisa preencher o formulário primeiro.")
        if st.button("Voltar ao formulário"):
            st.session_state.pagina = "cadastro"
            st.rerun()
        return

    dados = st.session_state.dados_candidato

    with st.expander("Dados do candidato"):
        st.json(dados)

    if st.button("Buscar vagas compatíveis"):
        with st.spinner("Buscando vagas... Isso pode demorar alguns minutos."):
            # Corrigindo o import para a versão atual do LlamaIndex

            from tools.procurar_vagas import tool_procurar_vagas
            from service.azure_llm import llm

            agent = ReActAgent(
                llm=llm,
                system_prompt="Você é um assistente de busca de vagas de emprego. Encontre vagas de emprego adequadas.",
                tools=[tool_procurar_vagas],
                verbose=True,
            )

            areas = ", ".join(dados["areas"])
            setores = ", ".join(dados["setores"])

            consulta = f"""
            Com base no perfil abaixo, encontre vagas de emprego adequadas:
            
            Nome: {dados['nome']}
            Curso: {dados['curso']} ({dados['semestre']})
            Áreas de interesse: {areas}
            Setores de interesse: {setores}
            
            Resumo do currículo:
            {dados['curriculo_texto']}...
            
            Perfil LinkedIn:
            {dados['linkedin_dados']}...
            
            Encontre vagas adequadas para este perfil e formate-as de modo organizado.
            """

            try:

                async def run_agent_async():
                    return await agent.run(user_msg=consulta)

                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                resposta = loop.run_until_complete(run_agent_async())

                st.info("Resposta recebida. Processando resultados...")

                if resposta:
                    st.subheader("Vagas recomendadas")

                    # Extrair o texto da resposta de forma mais robusta
                    if hasattr(resposta, "response"):
                        resposta_text = resposta.response
                    elif isinstance(resposta, dict) and "content" in resposta:
                        resposta_text = resposta["content"]
                    elif hasattr(resposta, "content"):
                        resposta_text = resposta.content
                    elif isinstance(resposta, str):
                        resposta_text = resposta
                    elif hasattr(resposta, "message") and hasattr(
                        resposta.message, "content"
                    ):
                        resposta_text = resposta.message.content
                    elif hasattr(resposta, "content") and resposta.content:
                        resposta_text = resposta.content
                    else:
                        resposta_text = str(resposta)

                    # Garantir que temos uma string para trabalhar
                    if not isinstance(resposta_text, str):
                        resposta_text = str(resposta_text)

                    # Verificar se a resposta tem conteúdo útil
                    if not resposta_text or len(resposta_text.strip()) < 50:
                        st.warning(
                            "A resposta não contém vagas suficientes. Tentando buscar novamente..."
                        )
                        # Armazenar no log para debug
                        print(f"Resposta muito curta recebida: {resposta_text}")

                    st.markdown("### Vagas recomendadas:")
                    st.markdown(
                        "Clique em uma vaga para gerar o relatório de preparação."
                    )

                    # Melhoria: usar um separador mais robusto para dividir as vagas
                    # Filtrar entradas vazias ou que sejam apenas espaços em branco
                    vagas_list = [
                        vaga
                        for vaga in resposta_text.strip().split("---")
                        if vaga.strip()
                    ]
                    if not vagas_list:
                        # Tentar um método alternativo de divisão se o primeiro não funcionar
                        vagas_list = [
                            vaga
                            for vaga in resposta_text.strip().split("## ")
                            if vaga.strip()
                        ]
                        # Adicionar o prefixo "## " de volta às vagas exceto à primeira
                        if len(vagas_list) > 1:
                            vagas_list = [vagas_list[0]] + [
                                f"## {vaga}" for vaga in vagas_list[1:]
                            ]

                    # Se ainda não houver vagas válidas, tentar uma divisão simples por linhas em branco
                    if not vagas_list:
                        import re

                        # Dividir por 2 ou mais linhas em branco consecutivas
                        vagas_list = [
                            vaga
                            for vaga in re.split(r"\n{2,}", resposta_text)
                            if vaga.strip()
                        ]

                    # Armazenar vagas válidas na sessão para acesso posterior
                    st.session_state.vagas_validas = vagas_list

                    # Criar uma chave para controlar qual relatório está sendo mostrado
                    if "relatorio_ativo" not in st.session_state:
                        st.session_state.relatorio_ativo = None

                    # Criar um dicionário para armazenar relatórios gerados
                    if "relatorios" not in st.session_state:
                        st.session_state.relatorios = {}

                    for i, vaga in enumerate(vagas_list):
                        if not vaga.strip():  # Skip empty strings
                            continue

                        # Define vaga_id BEFORE using it in the expander
                        vaga_id = f"vaga_{i}"

                        # Usar um título mais informativo se possível
                        titulo = f"Vaga {i + 1}"
                        try:
                            # Tentar extrair o título da vaga do markdown
                            linhas = vaga.split("\n")
                            for linha in linhas[:3]:  # Olhar apenas as primeiras linhas
                                if linha.strip().startswith("#") or "**" in linha:
                                    titulo = f"Vaga {i + 1}: {linha.strip('#').strip().replace('*', '')}"
                                    break
                        except:
                            pass

                        # Now vaga_id is defined and can be used in the expander check
                        with st.expander(
                            titulo,
                            expanded=(st.session_state.relatorio_ativo == vaga_id),
                        ):
                            st.markdown(vaga)

                            # Verificar se já temos relatório para esta vaga
                            tem_relatorio = vaga_id in st.session_state.relatorios

                            # Container para ações
                            action_col1, action_col2 = st.columns([1, 3])

                            with action_col1:
                                # Botão para gerar relatório - mostrar apenas se não tiver relatório
                                if not tem_relatorio:
                                    if st.button(
                                        "📄 Gerar relatório",
                                        key=f"btn_{vaga_id}",
                                        use_container_width=True,
                                    ):
                                        # Flag para indicar que devemos mostrar a geração do relatório
                                        st.session_state.gerando_relatorio = vaga_id
                                        st.session_state.relatorio_ativo = vaga_id
                                        # Força rerun uma única vez para iniciar geração
                                        st.rerun()
                                else:
                                    # Botão para mostrar/esconder relatório existente
                                    mostrar_texto = (
                                        "📄 Ver relatório"
                                        if st.session_state.relatorio_ativo != vaga_id
                                        else "🔄 Atualizar"
                                    )
                                    if st.button(
                                        mostrar_texto,
                                        key=f"show_{vaga_id}",
                                        use_container_width=True,
                                    ):
                                        st.session_state.relatorio_ativo = vaga_id
                                        st.rerun()

                            with action_col2:
                                # Espaço ou outras ações futuras
                                pass

                            # Verifica se estamos gerando relatório para esta vaga específica
                            if (
                                "gerando_relatorio" in st.session_state
                                and st.session_state.gerando_relatorio == vaga_id
                            ):
                                # Mostrar indicador de carregamento
                                with st.spinner("Gerando relatório..."):
                                    # Preparar dados para o relatório
                                    perfil = f"""
                                    Nome: {dados['nome']}
                                    Curso: {dados['curso']} ({dados['semestre']})
                                    Áreas de interesse: {', '.join(dados['areas'])}
                                    Setores de interesse: {', '.join(dados['setores'])}
                                    Resumo do currículo:
                                    {dados['curriculo_texto']}
                                    Perfil LinkedIn:
                                    {dados['linkedin_dados']}
                                    """

                                    try:
                                        relatorio = gerar_relatorio_preparacao_vaga(
                                            vaga=vaga,
                                            perfil_candidato=perfil,
                                        )
                                        # Armazenar o relatório gerado
                                        st.session_state.relatorios[vaga_id] = relatorio
                                        # Limpar flag de geração
                                        st.session_state.gerando_relatorio = None
                                        st.success("Relatório gerado com sucesso!")
                                    except Exception as e:
                                        import traceback

                                        st.error(f"Erro ao gerar relatório: {str(e)}")
                                        st.code(traceback.format_exc())
                                        # Limpar flag de geração mesmo em caso de erro
                                        st.session_state.gerando_relatorio = None

                            # Se esta for a vaga ativa e temos um relatório, mostrar o relatório
                            if (
                                st.session_state.relatorio_ativo == vaga_id
                                and vaga_id in st.session_state.relatorios
                            ):
                                with st.container():
                                    st.markdown("### 📁 Relatório de Preparação")
                                    st.markdown(st.session_state.relatorios[vaga_id])

                                    # Botão para download
                                    relatorio_bytes = st.session_state.relatorios[
                                        vaga_id
                                    ].encode("utf-8")
                                    st.download_button(
                                        label="📄 Baixar relatório (.txt)",
                                        data=relatorio_bytes,
                                        file_name=f"relatorio_vaga_{i+1}.txt",
                                        mime="text/plain",
                                        key=f"download_{vaga_id}",
                                    )

                else:
                    st.warning("Nenhuma vaga encontrada que corresponda ao seu perfil.")
            except Exception as e:
                import traceback

                st.error(f"Erro ao buscar vagas: {str(e)}")
                st.error("Detalhes do erro:")
                st.code(traceback.format_exc())

            # Adicionar botões de ação em uma linha
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Realizar nova busca"):
                    # Limpar resultados anteriores mas manter dados do candidato
                    if "vagas_validas" in st.session_state:
                        st.session_state.vagas_validas = []
                    if "relatorios" in st.session_state:
                        st.session_state.relatorios = {}
                    if "relatorio_ativo" in st.session_state:
                        st.session_state.relatorio_ativo = None
                    st.rerun()

            with col2:
                if st.button("Voltar ao formulário"):
                    # Retornar à página de cadastro
                    st.session_state.pagina = "cadastro"
                    st.rerun()


def main():
    st.set_page_config(page_title="Formulário de Cadastro", layout="wide")

    # Inicializa o estado da sessão
    if "pagina" not in st.session_state:
        st.session_state.pagina = "cadastro"

    # Inicializar outras variáveis de estado necessárias
    if "dados_candidato" not in st.session_state:
        st.session_state.dados_candidato = None

    if "vagas_validas" not in st.session_state:
        st.session_state.vagas_validas = []

    if "relatorios" not in st.session_state:
        st.session_state.relatorios = {}

    if "relatorio_ativo" not in st.session_state:
        st.session_state.relatorio_ativo = None

    # Exibe a página adequada
    if st.session_state.pagina == "cadastro":
        st.title("📋 Formulário de Cadastro")
        st.markdown("Campos marcados com * são obrigatórios.")

        # === Dados Pessoais ===
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Completo *")
        with col2:
            curso = st.text_input("Curso *")
            semestre = st.selectbox(
                "Semestre *",
                options=[f"{i}º Semestre" for i in range(1, 13)] + ["Formado"],
            )

        # === Interesses Profissionais ===
        st.subheader("🎯 Interesses Profissionais")
        a1, a2 = st.columns([3, 2])
        with a1:
            areas_interesse = st.multiselect(
                "Áreas de Interesse *",
                options=[
                    "Desenvolvimento de Software",
                    "Análise de Dados",
                    "Inteligência Artificial",
                    "Segurança da Informação",
                    "DevOps",
                    "UX/UI Design",
                    "Gestão de Projetos",
                    "QA/Testes",
                    "Outro",
                ],
            )
        with a2:
            # campo "Outro" só aparece quando selecionado
            if "Outro" in areas_interesse:
                outra_area = st.text_input("Especifique outra área *")
            else:
                outra_area = ""

        s1, s2 = st.columns([3, 2])
        with s1:
            setores_interesse = st.multiselect(
                "Setores de Interesse *",
                options=[
                    "Finanças",
                    "Saúde",
                    "Educação",
                    "Varejo",
                    "E-commerce",
                    "Tecnologia",
                    "Indústria",
                    "Consultoria",
                    "Governo",
                    "Outro",
                ],
            )
        with s2:
            if "Outro" in setores_interesse:
                outro_setor = st.text_input("Especifique outro setor *")
            else:
                outro_setor = ""

        # === Documentos e Links ===
        st.subheader("📄 Documentos e Links")
        curriculo = st.file_uploader("Currículo (PDF) *", type=["pdf"])
        linkedin_url = st.text_input(
            "URL do LinkedIn *", placeholder="https://linkedin.com/in/usuario"
        )

        concordo = st.checkbox("Li e concordo com a política de privacidade *")

        # === Botão de Enviar ===
        if st.button("Enviar"):
            erros = []

            # Validações
            if not nome:
                erros.append("Nome Completo")
            if not curso:
                erros.append("Curso")
            if not areas_interesse:
                erros.append("Áreas de Interesse")
            if "Outro" in areas_interesse and not outra_area:
                erros.append("Especifique outra área")
            if not setores_interesse:
                erros.append("Setores de Interesse")
            if "Outro" in setores_interesse and not outro_setor:
                erros.append("Especifique outro setor")
            if not curriculo:
                erros.append("Currículo")
            else:
                tamanho_mb = len(curriculo.getbuffer()) / (1024**2)
                if tamanho_mb > MAX_FILE_SIZE_MB:
                    erros.append(f"Currículo excede {MAX_FILE_SIZE_MB} MB")
            if not linkedin_url:
                erros.append("URL do LinkedIn")
            if not concordo:
                erros.append("Política de privacidade")

            if erros:
                st.error("Corrija os campos: " + "; ".join(erros))
            else:
                with st.spinner("Processando documentos..."):
                    # Prepara listas finais
                    areas_final = [a for a in areas_interesse if a != "Outro"]
                    if outra_area:
                        areas_final.append(outra_area)

                    setores_final = [s for s in setores_interesse if s != "Outro"]
                    if outro_setor:
                        setores_final.append(outro_setor)

                    # Extrai texto do currículo PDF
                    curriculo_bytes = curriculo.getvalue()
                    curriculo_texto = extrair_texto_pdf(curriculo_bytes)

                    # Extrai informações do LinkedIn
                    try:
                        linkedin_dados = get_linkedin_profile(linkedin_url)
                    except Exception as e:
                        linkedin_dados = f"Erro ao extrair dados do LinkedIn: {str(e)}"

                    # Monta dicionário e gera JSON
                    dados = {
                        "nome": nome,
                        "curso": curso,
                        "semestre": semestre,
                        "areas": areas_final,
                        "setores": setores_final,
                        "linkedin": linkedin_url,
                        "linkedin_dados": linkedin_dados,
                        "arquivo": curriculo.name,
                        "curriculo_texto": curriculo_texto,
                        "timestamp": datetime.now().isoformat(),
                    }
                    dados_json = json.dumps(dados, ensure_ascii=False, indent=2)

                    # Salva os dados na sessão
                    st.session_state.dados_candidato = dados

                    # Mostra o JSON
                    st.success("Dados coletados com sucesso!")
                    st.json(dados)

                    # Redireciona para a página de busca de vagas
                    st.session_state.pagina = "busca_vagas"
                    st.rerun()

    # Switch between pages
    elif st.session_state.pagina == "busca_vagas":
        pagina_busca_vagas()


if __name__ == "__main__":
    main()
