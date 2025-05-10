from crewai_tools import ScrapeWebsiteTool


def get_linkedin_profile(url: str) -> str:
    scraper = ScrapeWebsiteTool(website_url=url)
    text = scraper.run(
        url=url,
    )
    return text
