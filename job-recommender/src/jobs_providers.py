import os
import time
import requests
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urlencode

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")


def normalize_job(
    title: str,
    company: str,
    location: str,
    description: str,
    url: str,
    source: str,
    via: Optional[str] = None,
    posted_at: Optional[str] = None,
) -> Dict:
    return {
        "id": f"{source}:{hash((title, company, location, url))}",
        "title": title or "",
        "company": company or "",
        "location": location or "",
        "description": (description or "").strip(),
        "url": url or "",
        "source": source,
        "via": via or source,
        "posted_at": posted_at or "",
    }


# -------------------------
# Provider 1: SerpAPI (Google Jobs)
# -------------------------
def fetch_google_jobs_serpapi(
    query: str,
    location: str = "",
    num: int = 20,
) -> List[Dict]:
    """
    Uses SerpAPI's Google Jobs Engine.
    Docs: https://serpapi.com/jobs-results
    """
    if not SERPAPI_KEY:
        return []

    base = "https://serpapi.com/search.json"
    params = {
        "engine": "google_jobs",
        "q": query,
        "api_key": SERPAPI_KEY,
        "hl": "en",
        "gl": "in",
        "location": location or "India",
    }

    r = requests.get(base, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()

    results = []
    for item in data.get("jobs_results", [])[:num]:
        title = item.get("title", "")
        company = item.get("company_name", "")
        loc = item.get("location", "")
        desc = item.get("description", "") or item.get("snippet", "")
        via = "Google Jobs"
        posted = item.get("detected_extensions", {}).get("posted_at") or item.get("via")
        apply_links = item.get("apply_options") or []
        url = ""
        if apply_links:
            # Pick first apply link
            url = apply_links[0].get("link", "")
        else:
            url = item.get("job_id", "")

        results.append(
            normalize_job(
                title=title,
                company=company,
                location=loc,
                description=desc,
                url=url,
                source="serpapi",
                via=via,
                posted_at=str(posted) if posted else "",
            )
        )
    return results


# -------------------------
# Provider 2: JSearch (RapidAPI)
# -------------------------
def fetch_jobs_jsearch(
    query: str,
    location: str = "",
    job_type: str = "",
    num: int = 20,
) -> List[Dict]:
    """
    JSearch (RapidAPI) aggregates jobs from multiple boards.
    Endpoint: https://jsearch.p.rapidapi.com/search
    """
    if not RAPIDAPI_KEY:
        return []

    url = "https://jsearch.p.rapidapi.com/search"
    params = {
        "query": f"{query} {location}".strip(),
        "page": "1",
        "num_pages": "1",
        "employment_types": job_type or "",
    }
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "jsearch.p.rapidapi.com",
    }

    r = requests.get(url, headers=headers, params=params, timeout=40)
    r.raise_for_status()
    data = r.json()

    out = []
    for item in data.get("data", [])[:num]:
        out.append(
            normalize_job(
                title=item.get("job_title", ""),
                company=item.get("employer_name", ""),
                location=item.get("job_city", "") or item.get("job_country", "") or "",
                description=item.get("job_description", ""),
                url=item.get("job_apply_link", "") or item.get("job_apply_is_direct", ""),
                source="jsearch",
                via=item.get("job_publisher", "JSearch"),
                posted_at=item.get("job_posted_at_datetime_utc", ""),
            )
        )
    return out


def fetch_live_jobs(
    skills: List[str],
    experience_text: str,
    preferences: List[str],
    location: str = "",
    job_type: str = "",
    max_results: int = 25,
    use_serpapi: bool = True,
    use_jsearch: bool = True,
) -> List[Dict]:
    """
    High-level orchestrator to pull jobs from enabled providers.
    """
    query = " ".join(skills + preferences + [experience_text]).strip() or "internship"
    all_jobs: List[Dict] = []

    if use_serpapi:
        try:
            all_jobs += fetch_google_jobs_serpapi(query=query, location=location, num=max_results)
        except Exception as e:
            print("[SerpAPI] Error:", e)

    if use_jsearch:
        try:
            all_jobs += fetch_jobs_jsearch(query=query, location=location, job_type=job_type, num=max_results)
        except Exception as e:
            print("[JSearch] Error:", e)

    # Deduplicate by (title, company, location)
    seen = set()
    deduped = []
    for j in all_jobs:
        k = (j["title"].lower(), j["company"].lower(), j["location"].lower())
        if k not in seen and j["title"] and j["company"]:
            seen.add(k)
            deduped.append(j)
    return deduped
