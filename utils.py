import streamlit as st


def gerar_chave_segura(texto):
    """
    Gera uma chave segura para uso em componentes Streamlit
    a partir de um texto, evitando problemas com o hash()

    Args:
        texto: Texto para gerar a chave

    Returns:
        Uma string que pode ser usada como chave
    """
    if not texto:
        return "empty"

    # Usar apenas os primeiros 100 caracteres para evitar problemas com textos muito longos
    resumo = texto[:100] if len(texto) > 100 else texto
    # Substituir caracteres problemáticos
    resumo = resumo.replace(" ", "_").replace("\n", "").replace(":", "")
    # Adicionar um hash numérico para garantir unicidade
    valor_hash = abs(hash(texto)) % 10000

    return f"{resumo}_{valor_hash}"


def mostrar_relatorio_em_expander(expander, relatorio, titulo_download, key_prefix):
    """
    Exibe um relatório dentro de um expander do Streamlit

    Args:
        expander: o expander do Streamlit
        relatorio: o texto do relatório
        titulo_download: título do arquivo para download
        key_prefix: prefixo para chaves de componentes
    """
    with expander:
        st.success("Relatório gerado com sucesso!")
        st.markdown("### 📁 Relatório de Preparação")
        st.markdown(relatorio)

        # Verificar se há relatório para download
        if relatorio and len(relatorio) > 0:
            # Gerar download em txt
            relatorio_bytes = relatorio.encode("utf-8")
            st.download_button(
                label="📄 Baixar relatório (.txt)",
                data=relatorio_bytes,
                file_name=f"{titulo_download}.txt",
                mime="text/plain",
                key=f"download_{key_prefix}",
            )
