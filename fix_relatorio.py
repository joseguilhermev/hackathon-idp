"""
Este arquivo contém funções auxiliares para corrigir o problema de geração
de relatórios no aplicativo Streamlit.
"""

import streamlit as st
import traceback
from agents.relatorio import gerar_relatorio_preparacao_vaga


def gerar_e_exibir_relatorio(vaga, perfil_candidato, indice):
    """
    Função auxiliar para gerar e exibir um relatório para uma vaga

    Args:
        vaga: texto da vaga
        perfil_candidato: dados do candidato
        indice: índice da vaga

    Returns:
        True se o relatório foi gerado com sucesso, False caso contrário
    """
    try:
        # Verificar se a vaga tem conteúdo suficiente
        if not vaga or len(vaga.strip()) < 10:
            st.error(
                "Esta vaga não contém informações suficientes para gerar um relatório."
            )
            return False

        # Identificador único para esta vaga
        vaga_hash = abs(hash(vaga)) % 100000
        vaga_key = f"vaga_{indice}_{vaga_hash}"

        # Verificar se já temos um relatório em cache
        if "relatorio_cache" not in st.session_state:
            st.session_state.relatorio_cache = {}

        if vaga_key in st.session_state.relatorio_cache:
            relatorio = st.session_state.relatorio_cache[vaga_key]
            st.info("Usando relatório em cache")
        else:
            # Gerar um novo relatório
            with st.spinner("Gerando relatório personalizado..."):
                relatorio = gerar_relatorio_preparacao_vaga(
                    descricao_vaga=vaga,
                    perfil_candidato=perfil_candidato,
                )
                # Salvar no cache
                st.session_state.relatorio_cache[vaga_key] = relatorio

        # Exibir o relatório
        st.success("✅ Relatório gerado com sucesso!")
        st.markdown("### 📁 Relatório de Preparação")
        st.markdown(relatorio)

        # Botão para download do relatório
        relatorio_bytes = relatorio.encode("utf-8")
        st.download_button(
            label="📄 Baixar relatório (.txt)",
            data=relatorio_bytes,
            file_name=f"relatorio_vaga_{indice+1}.txt",
            mime="text/plain",
            key=f"download_{vaga_key}",
        )

        return True

    except Exception as e:
        st.error(f"Erro ao gerar relatório: {str(e)}")
        st.code(traceback.format_exc())
        return False
