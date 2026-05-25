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


def sync_jobs(scraped_jobs, firm_counts=None):
    conn = get_connection()

    try:
        new_jobs = insert_jobs(conn, scraped_jobs)

        scraped_count = len(scraped_jobs)
        new_count = len(new_jobs)

        print(f"Scraped jobs: {scraped_count}")
        print(f"New postings: {new_count}")

        broken = [firm for firm, count in (firm_counts or {}).items() if count == 0]
        if broken:
            print(f"Broken scrapers (0 jobs): {', '.join(broken)}")

        send_to_telegram(new_jobs, firm_counts or {})

        return new_jobs

    finally:
        conn.close()


TELEGRAM_BOT_TOKEN = "8806547080:AAESJB7x5MfwqGXPyfyRt9ZeGKSOC8jyaBg"
TELEGRAM_CHAT_ID = "-5134836158"


COMPANY_EMOJI = {
    "Optiver": "🔵",
    "IMC": "🟣",
    "Point72": "🟡",
    "Jump Trading": "🟠",
    "Flow Traders": "🟢",
    "Mako": "⚪",
    "Jane Street": "🔴",
    "BAM": "🟤",
    "Citadel Securities": "🏰",
    "Crypto.com": "🪙",
    "SIG": "📊",
}


def send_to_telegram(jobs, firm_counts={}):
    from datetime import datetime

    broken = [firm for firm, count in firm_counts.items() if count == 0]

    if not jobs and not broken:
        return

    now = datetime.now().strftime("%d %b %Y · %H:%M")
    lines = []

    if jobs:
        grouped = {}
        for job in jobs:
            company = job.get("company", "Unknown")
            grouped.setdefault(company, []).append(job)

        total = sum(len(v) for v in grouped.values())
        lines.append(f"🚨  NEW JOBS DETECTED  🚨")
        lines.append(f"🗓  {now}")
        lines.append(f"📦  {total} new posting{'s' if total != 1 else ''} across {len(grouped)} firm{'s' if len(grouped) != 1 else ''}")
        lines.append("─" * 28)

        for company, company_jobs in grouped.items():
            emoji = COMPANY_EMOJI.get(company, "🏢")
            lines.append(f"\n{emoji}  {company.upper()}  ·  {len(company_jobs)} job{'s' if len(company_jobs) != 1 else ''}")
            for job in company_jobs[:10]:
                lines.append(f"  ↳ {job['title']}")
                lines.append(f"     {job['link']}")

        lines.append("\n" + "─" * 28)

    if broken:
        lines.append(f"\n⚠️  BROKEN SCRAPERS  ({len(broken)} firm{'s' if len(broken) != 1 else ''})")
        lines.append("Returned 0 jobs — check the code:\n")
        for firm in broken:
            lines.append(f"  ❌  {firm}")

    message = "\n".join(lines)

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "disable_web_page_preview": True,
        },
    )
