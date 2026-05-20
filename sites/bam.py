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

            jobs.append(
                {
                    "title": title,
                    "link": urljoin(page.url, href) if href else job_id,
                    "location": meta,
                    "company": "Balyasny",
                }
            )

        except Exception:
            continue

    return jobs
