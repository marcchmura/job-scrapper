import psycopg2
import requests

DB_URL = "postgresql://postgres.rsiumpmazmiguczafepq:0;4~-l5CdObg@aws-0-eu-west-1.pooler.supabase.com:6543/postgres"


def get_connection():
    return psycopg2.connect(DB_URL)


def insert_jobs(conn, jobs):
    if not jobs:
        return []

    new_jobs = []

    with conn.cursor() as cur:
        for job in jobs:
            cur.execute(
                """
                INSERT INTO jobs (title, link, company, location, meta)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (link) DO NOTHING
                RETURNING title, link, company, location
                """,
                (
                    job.get("title"),
                    job.get("link"),
                    job.get("company"),
                    job.get("location"),
                    job.get("meta"),
                ),
            )

            result = cur.fetchone()
            if result:
                new_jobs.append(
                    {
                        "title": result[0],
                        "link": result[1],
                        "company": result[2],
                        "location": result[3],
                    }
                )

    conn.commit()
    return new_jobs


def sync_jobs(scraped_jobs):
    conn = get_connection()

    try:
        new_jobs = insert_jobs(conn, scraped_jobs)

        scraped_count = len(scraped_jobs)
        new_count = len(new_jobs)

        print(f"Scraped jobs: {scraped_count}")
        print(f"New postings: {new_count}")

        send_to_telegram(new_jobs)

        return new_jobs

    finally:
        conn.close()


TELEGRAM_BOT_TOKEN = "8806547080:AAESJB7x5MfwqGXPyfyRt9ZeGKSOC8jyaBg"
TELEGRAM_CHAT_ID = "-5134836158"


def send_to_telegram(jobs):
    if not jobs:
        return

    # group jobs by company
    grouped = {}

    for job in jobs:
        company = job.get("company", "Unknown")
        grouped.setdefault(company, []).append(job)

    message = f"🆕 New Job Alert\n\n"

    for company, company_jobs in grouped.items():
        message += f"{company.upper()} ----- {len(company_jobs)} jobs\n"

        for job in company_jobs[:10]:
            message += f"• {job['title']}\n{job['link']}\n"

        message += "\n"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "disable_web_page_preview": True,
        },
    )
