from urllib.parse import urljoin


def scrape_optiver(page):
    jobs = []

    # wait for jobs to appear
    page.wait_for_selector("li.job-archive-js-item")
    """
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
    """

    # get all jobs
    listings = page.query_selector_all("li.job-archive-js-item")

    for item in listings:
        link_element = item.query_selector("h5 a")

        if not link_element:
            continue

        title = link_element.inner_text().strip()

        href = link_element.get_attribute("href")

        location_element = item.query_selector("p.text-s")

        location = location_element.inner_text().strip() if location_element else None

        jobs.append(
            {
                "title": title,
                "link": urljoin(page.url, href),
                "location": location,
                "company": "Optiver",
            }
        )
    return jobs
