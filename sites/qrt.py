from urllib.parse import urljoin

BASE_URL = "https://www.qube-rt.com/careers/"


def scrape_qrt(page):
    jobs = []

    page.wait_for_selector("a[href*='gh_jid']", state="attached", timeout=30000)

    for item in page.query_selector_all("section.careers-listing a[href*='gh_jid']"):
        try:
            title_el = item.query_selector("h3")
            location_el = item.query_selector("div p")
            href = item.get_attribute("href")

            if not title_el or not href:
                continue

            jobs.append({
                "title": title_el.inner_text().strip(),
                "location": location_el.inner_text().strip() if location_el else None,
                "category": None,
                "link": urljoin(BASE_URL, href),
                "company": "QRT",
            })

        except Exception as e:
            print(f"Error parsing job: {e}")

    return jobs
