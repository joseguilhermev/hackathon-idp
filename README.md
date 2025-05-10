# EstagIA: Conexão Inteligente para Estágios

## 🚀 Sobre o Projeto

O EstagIA é uma plataforma inteligente desenvolvida para auxiliar alunos universitários a encontrarem oportunidades de estágio que sejam verdadeiramente alinhadas com seus perfis acadêmicos, experiências e interesses. A solução visa otimizar o processo de busca e "match" entre estudantes e vagas, utilizando Inteligência Artificial para uma análise profunda e recomendações personalizadas.

## 🎯 Problema Solucionado

Muitos estudantes enfrentam dificuldades para:
•⁠  ⁠Identificar vagas de estágio que correspondam às suas habilidades e conhecimentos adquiridos na faculdade.
•⁠  ⁠Analisar e comparar diversas oportunidades de forma eficiente.
•⁠  ⁠Entender como seu perfil acadêmico e extracurricular se traduz em requisitos do mercado.

O EstagIA busca diminuir essa lacuna, oferecendo um serviço de direcionamento mais assertivo e inteligente.

## ✨ Funcionalidades Principais (MVP)

1.  *Cadastro Detalhado do Aluno:*
    * Coleta de informações pessoais, curso, semestre.
    * Identificação de áreas e setores de interesse profissional.
    * Upload de currículo em PDF para análise.
    * Coleta de URL do perfil LinkedIn.
2.  *Análise de Perfil com IA:*
    * Extração automática de texto do currículo PDF utilizando *Azure Cognitive Services - Computer Vision (OCR)*.
    * Coleta de informações do perfil público do LinkedIn (via scraping).
    * Consolidação dessas informações para formar um perfil rico do candidato.
3.  *Busca Inteligente de Vagas:*
    * Utilização de um agente de IA (*LlamaIndex ReActAgent* com *Azure OpenAI LLM*) para processar o perfil do aluno.
    * O agente utiliza uma ferramenta customizada (⁠ ProcurarVagas ⁠) que interage com o *LinkedIn Jobs Scraper* para buscar vagas em tempo real, aplicando filtros relevantes (localização, tipo de vaga, nível de experiência, data de postagem).
    * As vagas encontradas são apresentadas ao aluno de forma organizada.

(Conceito Futuro Apresentado no Pitch: Chat com Assistente IA para preparação, incluindo roadmap de estudos e tira-dúvidas para vagas específicas, e uma "IA Mestre" para otimização contínua do sistema).

## 🛠️ Arquitetura e Tecnologias Utilizadas

•⁠  ⁠*Frontend:* Streamlit (para uma interface web interativa e de rápido desenvolvimento).
•⁠  ⁠*Backend Logic & Orchestration:* Python (aplicação monolítica para este MVP).
•⁠  ⁠*Extração de Texto de PDF (OCR):* Azure Cognitive Services - Computer Vision.
•⁠  ⁠*Modelo de Linguagem (LLM):* Azure OpenAI (utilizado pelo agente LlamaIndex).
•⁠  ⁠*Framework de Agentes/Orquestração de LLM:* LlamaIndex (especificamente ⁠ ReActAgent ⁠).
•⁠  ⁠*Busca de Vagas:* ⁠ linkedin-jobs-scraper ⁠ (integrado como uma ferramenta LlamaIndex).
•⁠  ⁠*Gerenciamento de Perfil LinkedIn (Scraping Básico):* ⁠ crewai_tools.ScrapeWebsiteTool ⁠.
•⁠  ⁠*Principais Bibliotecas Python:* ⁠ streamlit ⁠, ⁠ llama-index ⁠, ⁠ azure-cognitiveservices-vision-computervision ⁠, ⁠ azure-ai-ml ⁠, ⁠ openai ⁠ (para interações com Azure OpenAI), ⁠ linkedin-jobs-scraper ⁠, ⁠ python-dotenv ⁠.

## ⚙️ Funcionamento (Fluxo do Usuário no MVP)

1.  *Cadastro:* O aluno acessa a interface Streamlit e preenche o formulário de cadastro com seus dados pessoais, acadêmicos, áreas de interesse, currículo PDF e link do LinkedIn.
2.  *Processamento de Dados:*
    * O texto do currículo PDF é extraído via Azure Vision OCR.
    * Informações básicas do perfil LinkedIn são coletadas.
    * Todos os dados são consolidados.
3.  *Busca de Vagas:*
    * O aluno navega para a seção de "Busca de Vagas".
    * Ao clicar em "Buscar vagas compatíveis", um prompt detalhado contendo o perfil do aluno é enviado para o ⁠ ReActAgent ⁠ do LlamaIndex.
    * O agente utiliza a ferramenta ⁠ ProcurarVagas ⁠ (que aciona o ⁠ LinkedinScraper ⁠) para buscar oportunidades relevantes.
    * As vagas encontradas e formatadas pela ferramenta são retornadas pelo agente e exibidas na interface Streamlit.
4.  *Visualização:* O aluno visualiza as vagas que a IA considerou compatíveis com seu perfil.

## 🔧 Configuração e Execução do Projeto

*Pré-requisitos:*
•⁠  ⁠Python 3.8+
•⁠  ⁠pip (gerenciador de pacotes Python)
•⁠  ⁠Contas e chaves de API para os serviços Azure (OpenAI e Computer Vision).

*Passos:*

1.  *Clone o Repositório (se aplicável) ou Descompacte os Arquivos:*
    ⁠ bash
    # Exemplo: git clone [https://github.com/seu-usuario/EstagIA.git](https://github.com/seu-usuario/EstagIA.git)
    cd EstagIA
     ⁠

2.  *Crie um Ambiente Virtual (Recomendado):*
    ⁠ bash
    python -m venv venv
    # No Windows:
    .\venv\Scripts\activate
    # No macOS/Linux:
    source venv/bin/activate
     ⁠

3.  *Configure as Variáveis de Ambiente:*
    * Crie um arquivo ⁠ .env ⁠ na raiz do projeto (ex: na pasta ⁠ hackathon/ ⁠).
    * Adicione suas chaves de API e endpoints, conforme o exemplo abaixo (substitua pelos seus valores reais):
        
4.  *Instale as Dependências:*
    Navegue até a pasta que contém o ⁠ requirements.txt ⁠ (ex: ⁠ hackathon/ ⁠) e execute:
    ⁠ bash
    pip install -r requirements.txt
     ⁠

5.  *Execute a Aplicação Streamlit:*
    Navegue até a pasta que contém o ⁠ app.py ⁠ (ex: ⁠ hackathon/ ⁠) e execute:
    ⁠ bash
    streamlit run app.py
     ⁠
    A aplicação deverá abrir no seu navegador padrão (geralmente ⁠ http://localhost:8501 ⁠).

## 🔮 Próximos Passos e Melhorias Futuras

•⁠  ⁠*Chat de Preparação com IA:* Implementar o chat interativo para auxiliar os alunos na preparação para entrevistas, gerando roadmaps de estudo e tirando dúvidas sobre as vagas (utilizando o LLM).
•⁠  ⁠*Banco de Dados Vetorial:* Implementar um banco de dados vetorial (ex: LanceDB, Qdrant, Milvus) para armazenar embeddings de currículos e vagas, permitindo um matching semântico mais escalável e eficiente.
•⁠  ⁠*"IA Mestre":* Desenvolver a IA otimizadora que aprende com o feedback dos usuários e o sucesso das colocações para refinar continuamente os algoritmos de matching e a eficácia do chat.
•⁠  ⁠*Integração com Sistemas da Faculdade:* Conectar diretamente à base de dados da instituição para obter dados acadêmicos de forma automática e segura.
•⁠  ⁠*Melhorias na Ferramenta de Busca de Vagas:* Adicionar mais fontes de vagas além do LinkedIn e refinar os filtros.
•⁠  ⁠*Interface do Usuário (UX/UI):* Aprimorar a experiência do usuário com um design mais elaborado.

## 🏆 Por que o EstagIA?

O EstagIA não é apenas mais um portal de vagas. É um assistente de carreira inteligente que visa entender profundamente o aluno e o mercado, utilizando o que há de mais moderno em IA para criar conexões de valor e preparar os estudantes para os desafios do mundo profissional.
