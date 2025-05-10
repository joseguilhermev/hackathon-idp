from service.azure_llm import llm


def gerar_relatorio_preparacao_vaga(
    vaga: str, perfil_candidato: str, instrucoes_sistema: str = None
) -> str:
    if not instrucoes_sistema:
        instrucoes_sistema = """
        Você é um assistente especializado em preparação para entrevistas de emprego.
        
        Analise a descrição da vaga e o perfil do candidato, e forneça um relatório de preparação em formato markdown que inclua:
        1. Correspondência entre habilidades do candidato e requisitos da vaga
        2. Possíveis perguntas de entrevista que podem ser feitas
        3. Pontos que o candidato pode melhorar ou enfatizar
        4. Sugestões de tópicos para pesquisar sobre a empresa
        
        Formate sua resposta de modo organizado e direto, sem introduções longas.
        """
    try:
        # Construir prompt concatenando instruções do sistema e conteúdo do usuário
        prompt = (
            instrucoes_sistema
            + f"\nDescrição da vaga:\n{vaga}\nPerfil do candidato:\n{perfil_candidato}"
        )
        # Chamando o modelo LLM para gerar o relatório via complete
        resposta = llm.complete(prompt)
        # Extrair conteúdo da resposta
        if hasattr(resposta, "text"):
            return resposta.text
        elif hasattr(resposta, "content"):
            return resposta.content
        else:
            return str(resposta)
    except Exception as e:
        import traceback

        error_msg = f"Erro ao gerar relatório: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return f"Erro ao gerar o relatório: {str(e)}. Por favor, tente novamente mais tarde."
