from playwright.sync_api import sync_playwright
from db_sync import sync_jobs
from sites.imc import scrape_imc
from urllib.parse import urljoin
from sites.p72 import scrape_p72
from sites.flow import scrape_flow

from sites.opt import scrape_optiver
from sites.bam import scrape_bam
from sites.jump import scrape_jump
from sites.mako import scrape_mako
from sites.js import scrape_js
from sites.qrt import scrape_qrt
from sites.wintermute import scrape_wintermute

timeout = 3000

# Urls list
urls = [
    "https://www.mako.com/opportunities",
    "https://www.janestreet.com/join-jane-street/open-roles/?type=students-and-new-grads&location=london",
    "https://www.imc.com/ap/search-careers?jobOffices=Amsterdam%2CLondon%2CZug%2CHong+Kong&page=1",
    "https://optiver.com/working-at-optiver/career-opportunities/",
    "https://bambusdev.my.site.com/s/",
    "https://careers.point72.com/?location=london;milan;paris;warsaw,%20pl;singapore;hong%20kong",
    "https://www.jumptrading.com/hr/experienced-candidates",
    "https://www.jumptrading.com/hr/students-new-grads",
    "https://www.flowtraders.com/careers/job-search/",
    "https://www.qube-rt.com/careers/",
    "https://www.wintermute.com/company/opportunities",
]


FIRM_LABELS = {
    "optiver.com": "Optiver",
    "bambusdev": "BAM",
    "imc.com": "IMC",
    "point72.com": "Point72",
    "jumptrading.com": "Jump Trading",
    "flowtraders.com": "Flow Traders",
    "mako.com": "Mako",
    "janestreet.com": "Jane Street",
    "qube-rt.com": "QRT",
    "citadelsecurities.com": "Citadel Securities",
    "wintermute.com": "Wintermute",
}


def label_for(url):
    for key, name in FIRM_LABELS.items():
        if key in url:
            return name
    return url


# Main function
def scrape_all(urls):
    all_jobs = []
    firm_counts = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for url in urls:
            page = browser.new_page()
            firm = label_for(url)

            try:
                # these scrapers manage their own navigation (use domcontentloaded)
                self_navigating = [
                    "citadelsecurities.com",
                    "crypto.com",
                    "jumptrading.com",
                ]
                if not any(s in url for s in self_navigating):
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

                elif "jumptrading.com" in url:
                    jobs = scrape_jump(page, url)

                elif "flowtraders.com" in url:
                    jobs = scrape_flow(page)

                elif "mako.com" in url:
                    jobs = scrape_mako(page)

                elif "janestreet.com" in url:
                    jobs = scrape_js(page)

                elif "qube-rt.com" in url:
                    jobs = scrape_qrt(page)

                elif "wintermute.com" in url:
                    jobs = scrape_wintermute(page)

                else:
                    jobs = []

                firm_counts[firm] = firm_counts.get(firm, 0) + len(jobs)
                all_jobs.extend(jobs)

            except Exception as e:
                print(f"Error scraping {url}")
                print(e)
                firm_counts[firm] = 0

            finally:
                page.close()

        browser.close()

    return all_jobs, firm_counts


# Main function
jobs, firm_counts = scrape_all(urls)


# Syncing Db
sync_jobs(jobs, firm_counts)
