from playwright.sync_api import sync_playwright
from db_sync import sync_jobs
from imc import scrape_imc
from urllib.parse import urljoin
from p72 import scrape_p72

from opt import scrape_optiver
from bam import scrape_bam

timeout = 3000

# Urls list
urls = [
    "https://www.imc.com/ap/search-careers?jobOffices=Amsterdam%2CLondon%2CZug%2CHong+Kong&page=1",
    "https://optiver.com/working-at-optiver/career-opportunities/",
    "https://bambusdev.my.site.com/s/",
    "https://careers.point72.com/?location=london;milan;paris;warsaw,%20pl;singapore;hong%20kong",
]


# Main function
def scrape_all(urls):
    all_jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for url in urls:
            page = browser.new_page()

            try:
                page.goto(url, wait_until="networkidle")

                # choose scraper based on url
                if "optiver.com" in url:
                    jobs = scrape_optiver(page)

                elif "bambusdev" in url:
                    jobs = scrape_bam(page)

                elif "imc.com" in url:
                    jobs = scrape_imc(page)

                elif "point72.com" in url:
                    jobs = scrape_p72(page)

                else:
                    jobs = []

                all_jobs.extend(jobs)

            except Exception as e:
                print(f"Error scraping {url}")
                print(e)

            finally:
                page.close()

        browser.close()

    return all_jobs


# Main function
jobs = scrape_all(urls)


# Syncing Db
sync_jobs(jobs)
