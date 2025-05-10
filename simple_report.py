"""
Este arquivo contém função simplificada para gerar relatórios para vagas.
"""

import streamlit as st
from service.azure_llm import llm  # Importando o modelo de linguagem


def gerar_relatorio_simples(vaga, perfil_candidato):
    """
    Gera um relatório simplificado de preparação para a vaga baseado no perfil do candidato.

    Args:
        vaga (str): Descrição da vaga
        perfil_candidato (str): Dados do perfil do candidato

    Returns:
        str: Relatório formatado de preparação para a entrevista
    """
    try:
        prompt = f"""
        Você é um especialista em carreiras e orientação profissional. Gere um relatório detalhado de preparação para 
        uma entrevista de emprego com base nos dados a seguir:
        
        ### VAGA:
        {vaga}
        
        ### PERFIL DO CANDIDATO:
        {perfil_candidato}
        
        Seu relatório deve incluir:
        1. Análise de compatibilidade entre o candidato e a vaga
        2. Pontos fortes do candidato em relação à vaga
        3. Pontos de melhoria ou lacunas
        4. Sugestões de como destacar experiências relevantes
        5. Perguntas prováveis na entrevista e como respondê-las
        6. Dicas de preparação específicas para esta vaga
        
        Organize o relatório em seções claras e forneça orientações práticas.
        """

        # Chamando o modelo de linguagem para gerar o relatório
        response = llm.complete(prompt)

        # Formatando o resultado como string
        if hasattr(response, "text"):
            return response.text
        elif hasattr(response, "content"):
            return response.content
        else:
            return str(response)

    except Exception as e:
        return f"Erro ao gerar relatório: {str(e)}\n\nPor favor, tente novamente mais tarde."


def mostrar_relatorio(
    relatorio,
    titulo="Relatório de Preparação",
    incluir_download=True,
    prefixo_download="relatorio",
):
    """
    Exibe o relatório de modo simplificado

    Args:
        relatorio: texto do relatório
        titulo: título a ser exibido
        incluir_download: se deve incluir botão de download
        prefixo_download: prefixo para o nome do arquivo de download
    """
    st.success("✅ Relatório gerado com sucesso!")
    st.markdown(f"### 📁 {titulo}")
    st.markdown(relatorio)

    if incluir_download and relatorio:
        relatorio_bytes = relatorio.encode("utf-8")
        st.download_button(
            label="📄 Baixar relatório (.txt)",
            data=relatorio_bytes,
            file_name=f"{prefixo_download}.txt",
            mime="text/plain",
            key=f"download_{prefixo_download}",
        )
