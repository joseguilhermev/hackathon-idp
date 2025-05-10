from llama_index.core.tools import FunctionTool
import logging
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData, EventMetrics
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import (
    RelevanceFilters,
    TimeFilters,
    TypeFilters,
    ExperienceLevelFilters,
    OnSiteOrRemoteFilters,
)
import types
from selenium.webdriver.chrome.options import Options as ChromeOptions

# Global job results list to store jobs across function calls
jobs_data = []

# Set up logging
logging.getLogger("li:scraper").setLevel(logging.INFO)


# Event handlers must be defined as standalone functions
def on_data(data: EventData):
    """Handle job data events from the scraper"""
    global jobs_data
    job_info = {
        "title": data.title,
        "company": data.company,
        "location": data.place,
        "date": data.date_text,
        "link": data.link,
        "apply_link": getattr(data, "apply_link", None),
        "description": (
            data.description[:500] + "..."
            if len(data.description) > 500
            else data.description
        ),
        "insights": getattr(data, "insights", None),
    }
    jobs_data.append(job_info)
    print(f"[Found job] {data.title} at {data.company}")


def on_error(error):
    """Handle error events from the scraper"""
    print(f"[LinkedIn Scraper Error] {error}")


def on_end():
    """Handle end events from the scraper"""
    global jobs_data
    print(f"[LinkedIn Scraper] Finished search with {len(jobs_data)} results")


def format_to_markdown(jobs):
    """Format job results to markdown"""
    if not jobs:
        return "No jobs found matching your criteria."

    markdown = "# Jobs Found\n\n"
    for i, job in enumerate(jobs, 1):
        markdown += f"## {i}. {job['title']}\n"
        markdown += f"**Company:** {job['company']}\n"
        markdown += f"**Location:** {job['location']}\n"
        markdown += f"**Posted:** {job['date']}\n"
        markdown += f"**Job Link:** [Apply Here]({job['link']})\n"
        if job["apply_link"]:
            markdown += f"**Direct Apply Link:** [Quick Apply]({job['apply_link']})\n"
        markdown += "\n**Description Summary:**\n"
        markdown += f"{job['description']}\n\n"
        if job["insights"]:
            markdown += "**Insights:** " + ", ".join(job["insights"]) + "\n"
        # Usando um separador mais claro entre vagas
        markdown += "\n---\n\n"

    return markdown


# Initialize scraper once at module level with more human-like behavior
scraper = LinkedinScraper(
    chrome_options=ChromeOptions(),  # Create a proper ChromeOptions instance
    chrome_executable_path=None,  # Let the package detect Chrome path
    headless=True,  # Run in headless mode
    max_workers=1,  # Number of worker threads
    slow_mo=1.5,  # Slow down the scraper to avoid detection
    page_load_timeout=40,  # Page load timeout
)

# Register event handlers
scraper.on(Events.DATA, on_data)
scraper.on(Events.ERROR, on_error)
scraper.on(Events.END, on_end)


def procurar_vagas(
    search_term: str,
    google_search_term: str,
) -> str:
    """
    Search for jobs matching the search terms using LinkedIn Jobs Scraper

    Args:
        search_term: Primary job search term
        google_search_term: Additional search context (used for query refinement)

    Returns:
        Markdown-formatted job listings
    """
    global jobs_data
    # Reset jobs data
    jobs_data = []

    print(f"Searching for jobs: {search_term}")

    # Tenta algumas variações da consulta se os resultados iniciais são poucos
    attempts = 0
    max_attempts = 3

    # Combine search terms for better results
    combined_term = search_term
    if google_search_term and google_search_term != search_term:
        # Extract keywords from google_search_term to enhance the search
        keywords = " ".join(
            [
                word
                for word in google_search_term.split()
                if word.lower() not in search_term.lower() and len(word) > 3
            ]
        )

        if keywords:
            combined_term = f"{search_term} {keywords}"

    # Build query with more relaxed parameters
    query = Query(
        query=combined_term,
        options=QueryOptions(
            locations=["Brasília/DF"],  # Broader location for more results
            apply_link=True,  # Try to extract apply links
            skip_promoted_jobs=False,  # Include promoted jobs too
            limit=10,  # Increased number of jobs to fetch
            filters=QueryFilters(
                relevance=RelevanceFilters.RECENT,
                time=TimeFilters.MONTH,  # Look for jobs from past month instead of just week
                type=[
                    TypeFilters.FULL_TIME,
                    TypeFilters.CONTRACT,
                    TypeFilters.INTERNSHIP,
                ],
                experience=[
                    ExperienceLevelFilters.INTERNSHIP,
                    ExperienceLevelFilters.ENTRY_LEVEL,
                    ExperienceLevelFilters.ASSOCIATE,
                    ExperienceLevelFilters.MID_SENIOR,
                ],
                on_site_or_remote=[
                    OnSiteOrRemoteFilters.ON_SITE,
                    OnSiteOrRemoteFilters.REMOTE,
                    OnSiteOrRemoteFilters.HYBRID,
                ],
            ),
        ),
    )

    # Execute query with retry logic
    while attempts < max_attempts:
        try:
            # Clear previous results if this is a retry
            if attempts > 0:
                jobs_data = []
                print(f"Retry attempt {attempts}: modifying search term...")

                # On first retry, try to broaden or simplify the search term
                if attempts == 1:
                    # Simplify search by using fewer words
                    words = combined_term.split()
                    if len(words) > 2:
                        combined_term = " ".join(words[:2])
                        query.query = combined_term
                        query.options.locations = ["Brasil"]
                        print(f"Simplified search term to: {combined_term}")

                # On second retry, try using just the main job category
                elif attempts == 2:
                    # Try a very general term from the original search
                    general_terms = [
                        "desenvolvedor",
                        "analista",
                        "engenheiro",
                        "designer",
                        "gerente",
                    ]
                    for term in general_terms:
                        if term.lower() in search_term.lower():
                            combined_term = term
                            query.query = combined_term
                            query.options.limit = 15  # Try to get more results
                            print(f"Using general term: {combined_term}")
                            break

            print(f"Running search with term: {query.query}")
            scraper.run([query])

            # If we got results, no need for more attempts
            if len(jobs_data) > 0:
                print(f"Found {len(jobs_data)} jobs. Search successful.")
                break

            # If no results, try again with a different strategy
            print(f"No results found with term: {query.query}")
            attempts += 1

        except Exception as e:
            print(f"Error during search: {str(e)}")
            attempts += 1

    # If still no results, provide a helpful message
    if len(jobs_data) == 0:
        return """
# Não encontramos vagas específicas para o seu perfil

Infelizmente, nossa busca não retornou resultados específicos. Isso pode acontecer devido a:

1. Termos de busca muito específicos
2. Poucas vagas disponíveis no momento para sua área
3. Limitações temporárias do LinkedIn

## Sugestões para sua busca:

- Tente usar termos mais gerais para sua área
- Verifique diretamente no [LinkedIn Jobs](https://www.linkedin.com/jobs/)
- Experimente outras plataformas como [Glassdoor](https://www.glassdoor.com.br/) ou [Indeed](https://br.indeed.com/)

Tente realizar uma nova busca com termos diferentes.
"""

    # Format results to markdown
    results_markdown = format_to_markdown(jobs_data)
    return results_markdown


# Create function tool for the agent
tool_procurar_vagas = FunctionTool.from_defaults(
    fn=procurar_vagas,
    name="ProcurarVagas",
    description="Buscar vagas de emprego alinhadas com perfil da pessoa no LinkedIn. Fornece vagas atualizadas com descrições, links e informações da empresa.",
)
