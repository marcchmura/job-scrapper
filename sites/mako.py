def scrape_mako(page):
    jobs = []

    page.wait_for_selector("div.job-entry", timeout=30000)

    listings = page.query_selector_all("div.job-entry")

    for item in listings:
        try:
            title_el = item.query_selector("h3.job-heading")
            location_el = item.query_selector("[fs-cmsfilter-field='location']")
            dept_el = item.query_selector("[fs-cmsfilter-field='department']")
            link_el = item.query_selector("a.button")

            if not title_el or not link_el:
                continue

            jobs.append({
                "title": title_el.inner_text().strip(),
                "location": location_el.inner_text().strip() if location_el else None,
                "category": dept_el.inner_text().strip() if dept_el else None,
                "link": link_el.get_attribute("href"),
                "company": "Mako",
            })

        except Exception as e:
            print(f"Error parsing job: {e}")

    return jobs
