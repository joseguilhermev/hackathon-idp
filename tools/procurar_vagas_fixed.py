import asyncio
import json
from typing import List
from llama_index.core.tools import BaseTool, FunctionTool
from selenium.webdriver.chrome.options import Options as ChromeOptions
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import (
    RelevanceFilters,
    TimeFilters,
    TypeFilters,
    ExperienceLevelFilters,
)

# Store scraped jobs
jobs_data = []


# Define event callbacks
def on_data(data: EventData):
    global jobs_data
    jobs_data.append(
        {
            "title": data.title,
            "company": data.company,
            "company_link": data.company_link,
            "place": data.place,
            "date": data.date,
            "link": data.link,
            "description": data.description,
            "job_id": data.job_id,
        }
    )
    print(
        f"[ON DATA] {data.title} | {data.company} | {data.date} | {data.link} | {data.description[:50]}..."
    )


def on_error(error):
    print(f"[ON ERROR] {error}")


def on_end():
    print("[ON END]")


# Initialize scraper
try:
    # Create proper Chrome options
    chrome_options = ChromeOptions()
    # Add necessary options for headless operation
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize with proper options
    scraper = LinkedinScraper(
        chrome_options=chrome_options,  # Pass the proper ChromeOptions instance
        chrome_executable_path=None,  # Let the package detect Chrome
        headless=True,
        max_workers=1,
        slow_mo=1.5,
        page_load_timeout=40,
    )

    # Add event listeners
    scraper.on(Events.DATA, on_data)
    scraper.on(Events.ERROR, on_error)
    scraper.on(Events.END, on_end)

except Exception as e:
    print(f"Error initializing LinkedIn scraper: {e}")
    # Provide a dummy scraper if real one fails
    scraper = None


def search_jobs(keywords, locations=None, limit=10):
    """
    Search for jobs on LinkedIn
    """
    global jobs_data
    jobs_data = []  # Reset jobs data

    if not locations:
        locations = ["Brasil"]

    if not scraper:
        return [{"error": "LinkedIn scraper could not be initialized"}]

    try:
        queries = [
            Query(
                query=keywords,
                options=QueryOptions(
                    locations=locations,
                    apply_link=True,
                    skip_promoted_jobs=True,
                    limit=limit,
                ),
            )
        ]

        scraper.run(queries)
        return jobs_data
    except Exception as e:
        print(f"Error searching jobs: {e}")
        return [{"error": f"Error searching jobs: {str(e)}"}]


def procurar_vagas(consulta: str) -> str:
    """
    Procura vagas de emprego que correspondam à consulta.

    Args:
        consulta (str): Informações sobre o perfil do candidato e tipo de vaga que busca

    Returns:
        str: Lista de vagas encontradas no formato JSON
    """
    try:
        # Extract keywords from query
        keywords = consulta.split()[:5]  # Use first 5 words as keywords
        keyword_str = " ".join(keywords)

        # Search for jobs
        vagas = search_jobs(keyword_str)

        # Format results
        if isinstance(vagas, list) and vagas and isinstance(vagas[0], dict):
            # Return only relevant information in a structured format
            resultado_formatado = []
            for vaga in vagas:
                if "error" in vaga:
                    continue

                resultado_formatado.append(
                    {
                        "título": vaga.get("title", "Sem título"),
                        "empresa": vaga.get("company", "Empresa não informada"),
                        "local": vaga.get("place", "Local não informado"),
                        "data": vaga.get("date", "Data não informada"),
                        "link": vaga.get("link", ""),
                        "descrição": vaga.get("description", "Sem descrição")[:500]
                        + "...",
                    }
                )

            return json.dumps(resultado_formatado, ensure_ascii=False, indent=2)
        else:
            return json.dumps({"erro": "Nenhuma vaga encontrada"})

    except Exception as e:
        return json.dumps({"erro": f"Erro ao buscar vagas: {str(e)}"})


# Create tool
tool_procurar_vagas = FunctionTool.from_defaults(fn=procurar_vagas)
