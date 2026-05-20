from urllib.parse import urljoin


def scrape_p72(page):
    jobs = []

    # wait for job list to render
    page.wait_for_selector("ul#itemContainer li", timeout=10000)

    items = page.query_selector_all("ul#itemContainer li")

    for item in items:
        title_el = item.query_selector("a.searchSite")
        if not title_el:
            continue

        title = title_el.inner_text().strip()
        href = title_el.get_attribute("href")

        if not title or not href:
            continue

        if title.lower() == "apply now":
            continue

        link = urljoin(page.url, href)

        # location column (right section)
        location_el = item.query_selector(".o-listing--table__right p")
        location = location_el.inner_text().strip() if location_el else None

        jobs.append(
            {
                "title": title,
                "link": link,
                "location": location,
                "company": "Point72",
            }
        )

    return jobs
