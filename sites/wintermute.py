from urllib.parse import urljoin

BASE_URL = "https://www.wintermute.com"


def scrape_wintermute(page):
    jobs = []

    page.wait_for_selector("a[href*='/company/opportunities/']", state="attached", timeout=30000)

    for section in page.query_selector_all("div.mt-10, div.mt-16"):
        try:
            category_el = section.query_selector("h2")
            category = category_el.inner_text().strip() if category_el else None

            for item in section.query_selector_all("a[href*='/company/opportunities/']"):
                try:
                    title_el = item.query_selector("div.flex.items-center")
                    href = item.get_attribute("href")

                    if not title_el or not href:
                        continue

                    badges = item.query_selector_all("div.flex.flex-wrap.gap-md > div")
                    location = badges[2].inner_text().strip() if len(badges) >= 3 else None

                    jobs.append({
                        "title": title_el.inner_text().strip(),
                        "location": location,
                        "category": category,
                        "link": urljoin(BASE_URL, href),
                        "company": "Wintermute",
                    })

                except Exception as e:
                    print(f"Error parsing job: {e}")

        except Exception as e:
            print(f"Error parsing section: {e}")

    return jobs
