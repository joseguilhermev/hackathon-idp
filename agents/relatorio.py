from service.azure_llm import llm


def gerar_relatorio_preparacao_vaga(
    descricao_vaga: str, perfil_candidato: str, instrucoes_sistema: str = None
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
        # Construindo as mensagens para o modelo de linguagem
        mensagens = [
            {"role": "system", "content": instrucoes_sistema},
            {
                "role": "user",
                "content": f"Descrição da vaga:\n{descricao_vaga}\n\nPerfil do candidato:\n{perfil_candidato}",
            },
        ]

        # Chamando o modelo LLM para gerar o relatório
        resposta = llm.chat(messages=mensagens)

        if (
            not resposta
            or not hasattr(resposta, "message")
            or not hasattr(resposta.message, "content")
        ):
            return "Erro: Não foi possível gerar um relatório devido a um problema de comunicação com o modelo de linguagem."

        return resposta.message.content
    except Exception as e:
        import traceback

        error_msg = f"Erro ao gerar relatório: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return f"Erro ao gerar o relatório: {str(e)}. Por favor, tente novamente mais tarde."
