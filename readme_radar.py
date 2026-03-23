import os
import sys
import base64

import json

import requests
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

SEARCH_URL = "https://api.github.com/search/repositories"


def get_query_and_limit() -> tuple[str, int]:
    query = "language:python stars:10..50"
    limit = 20

    if len(sys.argv) > 1:
        query = sys.argv[1]

    if len(sys.argv) > 2:
        possible_limit = sys.argv[2]

        if not possible_limit.startswith("--"):
            try:
                limit = int(possible_limit)
            except ValueError:
                print("Error: limit must be an integer.")
                sys.exit(1)

    if limit < 1:
        print("Error: limit must be at least 1.")
        sys.exit(1)

    if limit > 100:
        print("Error: limit cannot exceed 100.")
        sys.exit(1)

    return query, limit


def get_headers() -> dict:
    if not GITHUB_TOKEN:
        print("Error: GITHUB_TOKEN is missing. Add it to your .env file.")
        sys.exit(1)

    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }


def fetch_repositories(query: str, limit: int, headers: dict) -> list:
    params = {
        "q": query,
        "sort": "stars",
        "order": "asc",
        "per_page": limit,
    }

    response = requests.get(SEARCH_URL, headers=headers, params=params, timeout=20)

    if response.status_code != 200:
        print(f"Error: GitHub search failed ({response.status_code})")
        print(response.text)
        sys.exit(1)

    data = response.json()
    return data.get("items", [])


def fetch_readme(owner: str, name: str, headers: dict) -> tuple[str | None, str]:
    readme_url = f"https://api.github.com/repos/{owner}/{name}/readme"
    response = requests.get(readme_url, headers=headers, timeout=20)

    if response.status_code == 200:
        readme_data = response.json()
        encoded_content = readme_data.get("content", "")
        decoded_bytes = base64.b64decode(encoded_content)
        readme_text = decoded_bytes.decode("utf-8", errors="ignore")
        return "found", readme_text

    if response.status_code == 404:
        return "missing", ""

    return f"error ({response.status_code})", ""


def analyze_readme(readme_text: str) -> dict:
    word_count = len(readme_text.split())

    heading_count = 0
    for line in readme_text.splitlines():
        if line.strip().startswith("#"):
            heading_count += 1

    text_lower = readme_text.lower()

    has_install = "install" in text_lower
    has_usage = "usage" in text_lower
    has_contributing = "contributing" in text_lower
    has_license = "license" in text_lower

    reasons = []
    score = 0

    if word_count < 100:
        reasons.append("README under 100 words")
        score += 50

    if heading_count < 2:
        reasons.append("Fewer than 2 headings")
        score += 25

    if not has_install:
        reasons.append("Missing Installation section")
        score += 10

    if not has_usage:
        reasons.append("Missing Usage section")
        score += 10

    if not has_contributing:
        reasons.append("Missing Contributing section")
        score += 5

    if not has_license:
        reasons.append("Missing License section")
        score += 5

    return {
        "word_count": word_count,
        "heading_count": heading_count,
        "score": score,
        "reasons": reasons,
    }


def get_severity(score: int) -> str:
    if score >= 75:
        return "Very Weak"
    if score >= 50:
        return "Weak"
    if score >= 25:
        return "Moderate"
    return "Strong"


def get_candidate_label(severity: str) -> str:
    if severity == "Very Weak":
        return "STRONG CANDIDATE"
    if severity == "Weak":
        return "GOOD CANDIDATE"
    if severity == "Moderate":
        return "Skip"
    return "Skip"


def build_results(repos: list, headers: dict) -> tuple[list, int]:
    results = []
    total_scanned = 0

    for repo in repos:
        total_scanned += 1

        owner = repo["owner"]["login"]
        name = repo["name"]
        full_name = f"{owner}/{name}"

        readme_status, readme_text = fetch_readme(owner, name, headers)

        if readme_status == "found":
            analysis = analyze_readme(readme_text)

            results.append({
                "name": full_name,
                "url": repo["html_url"],
                "stars": repo["stargazers_count"],
                "description": repo["description"],
                "readme_status": "found",
                "word_count": analysis["word_count"],
                "heading_count": analysis["heading_count"],
                "score": analysis["score"],
                "reasons": analysis["reasons"],
            })
        else:
            results.append({
                "name": full_name,
                "url": repo["html_url"],
                "stars": repo["stargazers_count"],
                "description": repo["description"],
                "readme_status": readme_status,
                "word_count": None,
                "heading_count": None,
                "score": 100,
                "reasons": ["Missing README"] if readme_status == "missing" else ["README fetch failed"],
            })

    return results, total_scanned


def filter_display_results(results: list) -> list:
    display_results = []

    for result in results:
        severity = get_severity(result["score"])
        candidate = get_candidate_label(severity)

        if candidate == "Skip":
            continue

        enriched = result.copy()
        enriched["severity"] = severity
        enriched["candidate"] = candidate
        display_results.append(enriched)

    return display_results


def print_summary(query: str, total_scanned: int, results: list, shown_results: list) -> None:
    strong_count = sum(1 for r in shown_results if r["candidate"] == "STRONG CANDIDATE")
    good_count = sum(1 for r in shown_results if r["candidate"] == "GOOD CANDIDATE")

    print()
    print("readme-radar")
    print("============")
    print(f"Query: {query}")
    print(f"Scanned: {total_scanned}")
    print(f"Flagged: {len(results)}")
    print(f"Shown: {len(shown_results)}")
    print(f"Strong candidates: {strong_count}")
    print(f"Good candidates: {good_count}")
    print()

    issue_counts = {}

    for r in shown_results:
        issue = r["reasons"][0]
        issue_counts[issue] = issue_counts.get(issue, 0) + 1

    if issue_counts:
        print("Top issues:")
        for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"{count} - {issue}")

        print()


def print_ranked_results(results: list) -> None:
    if not results:
        print("No strong or good candidates found.")
        print()
        return

    for rank, result in enumerate(results, 1):
        top_reason = result["reasons"][0]

        print(
            f"{rank}. {result['candidate']} | "
            f"{result['name']} | "
            f"stars: {result['stars']} | "
            f"score: {result['score']} | "
            f"{top_reason}"
        )

        print(f"   {result['url']}")

        if result["readme_status"] != "missing" and result["readme_status"] != "found":
            print(f"   status: {result['readme_status']}")

        if result["description"]:
            print(f"   description: {result['description']}")

        if result["word_count"] is not None:
            print(f"   word count: {result['word_count']}")
            print(f"   heading count: {result['heading_count']}")

        print(f"   severity: {result['severity']}")
        print("   other issues:")

        if len(result["reasons"]) == 1:
            print("   - no additional issues")
        else:
            for reason in result["reasons"][1:]:
                print(f"   - {reason}")

        print()


def get_show_limit() -> int | None:
    if "--show" in sys.argv:
        index = sys.argv.index("--show")

        if len(sys.argv) > index + 1:
            try:
                value = int(sys.argv[index + 1])
                if value < 1:
                    print("Error: --show must be at least 1")
                    sys.exit(1)
                return value
            except ValueError:
                print("Error: --show must be an integer")
                sys.exit(1)
        else:
            print("Error: --show requires a number")
            sys.exit(1)

    return None


def is_compact_mode() -> bool:
    return "--compact" in sys.argv


def print_ranked_results_compact(results: list) -> None:
    if not results:
        print("No strong or good candidates found.")
        print()
        return

    for rank, result in enumerate(results, 1):
        top_reason = result["reasons"][0]

        print(
            f"{rank}. {result['candidate']} | "
            f"{result['name']} | "
            f"stars: {result['stars']} | "
            f"score: {result['score']} | "
            f"{top_reason}"
        )

        print(f"   {result['url']}")

        if result["readme_status"] != "missing" and result["readme_status"] != "found":
            print(f"   status: {result['readme_status']}")

        print("   other issues:")

        if len(result["reasons"]) == 1:
            print("   - no additional issues")
        else:
            for reason in result["reasons"][1:]:
                print(f"   - {reason}")

        print()


def main() -> None:
    query, limit = get_query_and_limit()
    show_limit = get_show_limit()
    compact = is_compact_mode()
    headers = get_headers()
    json_output = "--json" in sys.argv

    repos = fetch_repositories(query, limit, headers)
    results, total_scanned = build_results(repos, headers)

    results.sort(key=lambda x: -x["score"])

    shown_results = filter_display_results(results)

    if show_limit is not None:
        shown_results = shown_results[:show_limit]

    if "--json" in sys.argv:
        json_index = sys.argv.index("--json")

        if len(sys.argv) > json_index + 1:
            filename = sys.argv[json_index + 1]
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(shown_results, f, indent=2)
            print(f"Saved {len(shown_results)} results to {filename}")
        else:
            print(json.dumps(shown_results, indent=2))
    else:
        print_summary(query, total_scanned, results, shown_results)
        print()
        
        if compact:
            print_ranked_results_compact(shown_results)
        else:
            print_ranked_results(shown_results)


if __name__ == "__main__":
    main()
