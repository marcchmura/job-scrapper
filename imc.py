def scrape_imc(page):
    jobs = []

    page.wait_for_timeout(3000)

    listings = page.query_selector_all("a[href*='/careers/jobs/']")

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

        jobs.append(
            {
                "title": title,
                "link": urljoin(page.url, href),
                "location": None,
                "company": "IMC",
            }
        )

    return jobs
