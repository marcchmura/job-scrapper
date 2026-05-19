from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
from db_sync import sync_jobs

timeout = 3000
# =========================================================
# OPTIVER
# =========================================================

def scrape_optiver(page):
    jobs = []

    # wait for jobs to appear
    page.wait_for_selector("li.job-archive-js-item")
    '''
    # click "Load more" until button disappears
    while True:
        button = page.query_selector(
            "a:has-text('Load more')"
        )

        if not button:
            break

        try:
            button.click()
            page.wait_for_timeout(timeout)
        except:
            break
    '''

    # get all jobs
    listings = page.query_selector_all("li.job-archive-js-item")

    for item in listings:
        link_element = item.query_selector("h5 a")

        if not link_element:
            continue

        title = link_element.inner_text().strip()

        href = link_element.get_attribute("href")

        location_element = item.query_selector("p.text-s")

        location = (
            location_element.inner_text().strip()
            if location_element
            else None
        )

        jobs.append({
            "title": title,
            "link": urljoin(page.url, href),
            "location": location,
            "company": "Optiver"
        })
    return jobs

# =========================================================
# OPTIVER
# =========================================================

# =========================================================
# IMC
# =========================================================
def scrape_bam(page):
    jobs = []

    # wait for results container
    page.wait_for_selector("lightning-layout-item")

    # each job card container
    listings = page.query_selector_all("lightning-layout-item")

    for item in listings:
        try:
            link_el = item.query_selector("a.group")
            if not link_el:
                continue

            # title is inside a specific div
            title_el = link_el.query_selector("div.font-semibold")
            title = title_el.inner_text().strip() if title_el else None

            # href (may be None in SPAs)
            href = link_el.get_attribute("href")

            # metadata is OUTSIDE the <a>
            meta_el = item.query_selector("div:not(.font-semibold)")
            meta = meta_el.inner_text().strip() if meta_el else None

            # fallback: use data-id if no href
            job_id = link_el.get_attribute("data-id")

            if not title:
                continue

            jobs.append({
                "title": title,
                "link": urljoin(page.url, href) if href else job_id,
                "location": meta,
                "company": "Balyasny"
            })

        except Exception:
            continue

    return jobs


# =========================================================
# IMC
# =========================================================

def scrape_imc(page):
    jobs = []

    page.wait_for_timeout(3000)

    listings = page.query_selector_all(
        "a[href*='/careers/jobs/']"
    )

    for item in listings:
        title = item.inner_text().strip()

        href = item.get_attribute("href")

        if href.startswith("http"):
            link = href
        else:
            link = urljoin("https://www.imc.com", href)

        if not title or not href:
            continue

        if title.lower() == "apply now":
            continue

        jobs.append({
            "title": title,
            "link": urljoin(page.url, href),
            "location": None,
            "company": "IMC"
        })

    return jobs




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


# =========================================================
# URLS
# =========================================================

urls = [
    "https://optiver.com/working-at-optiver/career-opportunities",

    "https://www.imc.com/ap/search-careers?jobOffices=Amsterdam,Hong%20Kong,Zug,London",

    "https://bambusdev.my.site.com/s/"
]


# =========================================================
# RUN
# =========================================================

jobs = scrape_all(urls)
print(jobs)

sync_jobs(jobs)
