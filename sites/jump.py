from urllib.parse import urljoin


def scrape_jump(page):
    jobs = []

    # wait until jobs load
    page.wait_for_selector("div.jobs-item")

    # get all job cards
    listings = page.query_selector_all("div.jobs-item")

    for item in listings:
        try:
            # link element
            link_element = item.query_selector("a[gw-jobs-apply]")

            if not link_element:
                continue

            href = link_element.get_attribute("href")

            # title
            title_element = item.query_selector("div[gw-jobs-title]")

            title = title_element.inner_text().strip() if title_element else None

            # location
            location_element = item.query_selector("div[gw-jobs-location]")

            location = (
                location_element.inner_text().strip() if location_element else None
            )

            jobs.append(
                {
                    "title": title,
                    "location": location,
                    "link": urljoin(page.url, href),
                    "company": "Jump Trading",
                }
            )

        except Exception as e:
            print(f"Error parsing job: {e}")

    return jobs
