import io
import time

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import Line
from azure.cognitiveservices.vision.computervision.models import (
    OperationStatusCodes,
    ReadOperationResult,
)
from msrest.authentication import CognitiveServicesCredentials
from pydantic import BaseModel, ConfigDict

from config.properties import (
    AZURE_COMPUTER_VISION_API_KEY,
    AZURE_COMPUTER_VISION_ENDPOINT,
)
from ocr.models import OCRDocumentoFalhaAzureException

azure_vision_client = ComputerVisionClient(
    AZURE_COMPUTER_VISION_ENDPOINT,
    CognitiveServicesCredentials(AZURE_COMPUTER_VISION_API_KEY),
)


def ocr(content: bytes) -> tuple[ReadOperationResult, list[str]]:
    content_ = io.BytesIO(content)

    read_response = azure_vision_client.read_in_stream(
        content_, raw=True, language="pt"
    )
    read_operation_location = read_response.headers["Operation-Location"]
    operation_id = read_operation_location.split("/")[-1]

    while True:
        read_result: ReadOperationResult = azure_vision_client.get_read_result(
            operation_id
        )
        if read_result.status not in ["notStarted", "running"]:
            break
        time.sleep(1)

    if read_result.status != OperationStatusCodes.succeeded:
        raise OCRDocumentoFalhaAzureException(
            f"Erro ao realizar OCR: {read_result.status}"
        )

    textos_das_paginas = _obter_paginas_do_resultado(read_result)

    return read_result, textos_das_paginas


def extrair_texto_pdf(conteudo_pdf):
    _, paginas = ocr(conteudo_pdf)
    texto_completo = "\n".join(paginas)
    return texto_completo


def _obter_paginas_do_resultado(
    resultado_bruto, tolerancia_vertical=(1 / 3)
) -> list[str]:
    pages = resultado_bruto.analyze_result.read_results
    textos_das_paginas = []

    for page in pages:
        linhas = _agrupar_linhas_por_posicao_vertical(page.lines, tolerancia_vertical)
        texto_da_pagina = _extrair_texto_das_linhas(linhas)
        textos_das_paginas.append(texto_da_pagina)

    return textos_das_paginas


def _agrupar_linhas_por_posicao_vertical(lines, tolerancia_vertical):
    linhas: list[Linha] = []
    for line in lines:
        centro_y = _calcular_centro_y(line.bounding_box)
        tolerancia = _calcular_tolerancia(line.bounding_box, tolerancia_vertical)
        _adicionar_line_nas_linhas(linhas, line, centro_y, tolerancia)
    _ordenar_linhas_e_palavras(linhas)
    return linhas


def _calcular_centro_y(bbox):
    return (bbox[1] + bbox[5]) / 2


def _calcular_tolerancia(bbox, tolerancia_vertical):
    altura = abs(bbox[5] - bbox[1])
    return altura * tolerancia_vertical


def _adicionar_line_nas_linhas(linhas, linha, centro_y, tolerancia):
    for linha_existente in linhas:
        if abs(linha_existente.centro_y - centro_y) <= tolerancia:
            linha_existente.palavras.append(linha)
            return
    linhas.append(Linha(centro_y=centro_y, palavras=[linha]))


def _ordenar_linhas_e_palavras(linhas):
    for linha in linhas:
        linha.palavras.sort(key=lambda palavra: palavra.bounding_box[0])
    linhas.sort(key=lambda l: l.centro_y)


def _extrair_texto_das_linhas(linhas):
    texto_da_pagina = []
    for linha in linhas:
        texto_linha = " ".join(
            palavra.text for palavra in linha.palavras if palavra.text
        )
        texto_da_pagina.append(texto_linha)
    return "\n".join(texto_da_pagina)


class Linha(BaseModel):
    centro_y: float
    palavras: list[Line] = []

    model_config = ConfigDict(arbitrary_types_allowed=True)
