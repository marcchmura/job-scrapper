from urllib.parse import urljoin

BASE_URL = "https://www.janestreet.com"


def scrape_js(page):
    jobs = []

    page.wait_for_selector("div.jobs-container > a", state="attached", timeout=30000)

    listings = page.query_selector_all("div.jobs-container > a")

    for item in listings:
        try:
            job_div = item.query_selector("div.job")
            if not job_div or "closed" in (job_div.get_attribute("class") or ""):
                continue

            title_el = item.query_selector("div.item.position p")
            location_el = item.query_selector("div.item.city p")
            dept_el = item.query_selector("div.item.department p")
            href = item.get_attribute("href")

            if not title_el or not href:
                continue

            jobs.append({
                "title": title_el.inner_text().strip(),
                "location": location_el.inner_text().strip() if location_el else None,
                "category": dept_el.inner_text().strip() if dept_el else None,
                "link": urljoin(BASE_URL, href),
                "company": "Jane Street",
            })

        except Exception as e:
            print(f"Error parsing job: {e}")

    return jobs
