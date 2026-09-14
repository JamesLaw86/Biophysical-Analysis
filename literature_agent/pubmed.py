"""PubMed retrieval via NCBI E-utilities.

Two plain functions, no LLM involved:
  search_pubmed   - esearch: query in, PMIDs and total hit count out
  fetch_abstracts - efetch: PMIDs in, title/authors/year/abstract out

Run directly to check retrieval by eye:
  python pubmed.py "T4 lysozyme thermal stability mutants"
"""

import os
import sys
import time
import xml.etree.ElementTree as ET

import requests

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
TOOL_NAME = "biophysical-literature-agent"

# NCBI allows 3 requests per second without an API key.
MIN_INTERVAL_S = 1 / 3
_last_request_time = 0.0


def _get(endpoint, params):
    """GET an E-utilities endpoint, rate-limited and with NCBI's contact parameters."""
    global _last_request_time

    email = os.environ.get("NCBI_EMAIL")
    if not email:
        raise RuntimeError("Set the NCBI_EMAIL environment variable; NCBI asks for a contact address.")

    wait = MIN_INTERVAL_S - (time.monotonic() - _last_request_time)
    if wait > 0:
        time.sleep(wait)
    _last_request_time = time.monotonic()

    params = {**params, "tool": TOOL_NAME, "email": email}
    response = requests.get(BASE_URL + endpoint, params=params, timeout=30)
    response.raise_for_status()
    return response


def search_pubmed(query, max_results=10):
    """Search PubMed.

    Returns {"pmids": [...], "total_count": n}. total_count is the number of
    matches in the whole of PubMed, so it shows whether a query was too broad
    or too narrow even though only max_results PMIDs come back.
    """
    response = _get("esearch.fcgi", {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
        # E-utilities returns newest first by default, unlike the PubMed website.
        # With few results that hides the foundational papers (see NOTES.md).
        "sort": "relevance",
    })
    result = response.json()["esearchresult"]
    return {"pmids": result["idlist"], "total_count": int(result["count"])}


def fetch_abstracts(pmids):
    """Fetch title, authors, year and abstract for each PMID.

    Only journal articles (<PubmedArticle>) are parsed; book records are skipped,
    so the result can be shorter than the input.
    """
    if not pmids:
        return []
    response = _get("efetch.fcgi", {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
    })
    # Pass bytes, not text, so the parser uses the encoding declared in the XML.
    root = ET.fromstring(response.content)
    return [_parse_article(article) for article in root.findall("PubmedArticle")]


def _parse_article(pubmed_article):
    citation = pubmed_article.find("MedlineCitation")
    article = citation.find("Article")
    return {
        "pmid": citation.findtext("PMID"),
        "title": _text(article.find("ArticleTitle")),
        "authors": _authors(article),
        "year": _year(article),
        "abstract": _abstract(article),
    }


def _text(element):
    """All text in an element, including inline markup such as <i> and <sup>.

    findtext() would stop at the first child tag, truncating titles that
    italicise a species or gene name.
    """
    if element is None:
        return ""
    return "".join(element.itertext()).strip()


def _authors(article):
    names = []
    for author in article.findall("AuthorList/Author"):
        collective = author.find("CollectiveName")
        if collective is not None:
            names.append(_text(collective))
        else:
            last = author.findtext("LastName", "")
            initials = author.findtext("Initials", "")
            names.append(f"{last} {initials}".strip())
    return names


def _year(article):
    # <Year> appears in several places (revision dates, history), so be specific.
    pub_date = article.find("Journal/JournalIssue/PubDate")
    if pub_date is None:
        return None
    year = pub_date.findtext("Year")
    if year:
        return year
    # Some records give a free-text date instead, e.g. "1998 Dec-1999 Jan".
    medline_date = pub_date.findtext("MedlineDate", "")
    return medline_date[:4] or None


def _abstract(article):
    # Structured abstracts are split into labelled sections (BACKGROUND, METHODS, ...).
    sections = []
    for section in article.findall("Abstract/AbstractText"):
        label = section.get("Label")
        text = _text(section)
        sections.append(f"{label}: {text}" if label else text)
    return "\n".join(sections)


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or "T4 lysozyme thermal stability mutants"
    search = search_pubmed(query, max_results=5)
    print(f"query: {query}")
    print(f"{search['total_count']} matches in PubMed; fetching {len(search['pmids'])}")

    papers = fetch_abstracts(search["pmids"])
    missing = set(search["pmids"]) - {paper["pmid"] for paper in papers}
    if missing:
        print(f"WARNING: no article returned for {sorted(missing)}")

    for paper in papers:
        authors = paper["authors"]
        first_author = f"{authors[0].split()[0]} et al." if authors else "(no authors)"
        print(f"\n{paper['pmid']} - {first_author} ({paper['year']}) - {paper['title']}")
        print(f"  {len(authors)} authors, abstract {len(paper['abstract'])} chars")
        print(f"  {paper['abstract'][:200]}")
