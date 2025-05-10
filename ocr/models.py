class OCRDocumentoFalhaException(Exception):
    def __init__(self, mensagem: str):
        self.mensagem = mensagem


class OCRDocumentoFalhaAzureException(Exception):
    def __init__(self, mensagem: str):
        self.mensagem = mensagem
