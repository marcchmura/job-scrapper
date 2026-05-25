from urllib.parse import urljoin


def scrape_flow(page):
    jobs = []

    # wait until jobs container loads
    page.wait_for_selector("div.flex.flex-col.gap-\\[1\\.5rem\\]")

    # click all "Show more" buttons if present
    while True:
        try:
            show_more_btn = page.query_selector("button:has-text('Show more')")

            if show_more_btn and show_more_btn.is_enabled():
                show_more_btn.scroll_into_view_if_needed()
                show_more_btn.click()

                # wait for additional jobs to load
                page.wait_for_timeout(2000)
            else:
                break

        except Exception:
            break

    # get all job blocks
    listings = page.query_selector_all(
        "div.flex.flex-col.gap-\\[1\\.5rem\\] > div.w-full.border-b"
    )

    for item in listings:
        try:
            # department + location
            meta_element = item.query_selector("h6")
            meta_text = meta_element.inner_text().strip() if meta_element else None

            location = None
            department = None

            if meta_text and "|" in meta_text:
                location, department = [x.strip() for x in meta_text.split("|", 1)]

            # title
            title_element = item.query_selector("h2")

            title = title_element.inner_text().strip() if title_element else None

            # description
            desc_element = item.query_selector("p.description")

            description = desc_element.inner_text().strip() if desc_element else None

            # link
            link_element = item.query_selector("a[href*='/careers/job-description/']")

            if not link_element:
                continue

            href = link_element.get_attribute("href")

            jobs.append(
                {
                    "title": title,
                    "location": location,
                    "department": department,
                    "description": description,
                    "link": urljoin(page.url, href),
                    "company": "Flow Traders",
                }
            )

        except Exception as e:
            print(f"Error parsing job: {e}")

    return jobs
