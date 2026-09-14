"""Command-line agent that answers questions from the PubMed literature.

A hand-rolled tool-calling loop: Claude picks its own search terms, reads the
abstracts, searches again if it needs to, and answers with [PMID n] citations.
Every cited PMID is then checked against the abstracts that were actually fetched.

Usage:
  python agent.py "What is known about the thermal stability of T4 lysozyme mutants?"

Needs ANTHROPIC_API_KEY and NCBI_EMAIL in the environment.
"""

import json
import re
import sys

import anthropic

import pubmed

MODEL = "claude-sonnet-5"
# USD per million tokens for MODEL, used for the running cost and the budget check.
INPUT_PRICE_PER_MTOK = 2.00
OUTPUT_PRICE_PER_MTOK = 10.00

MAX_TURNS = 20         # hard stop, so a confused model can't loop forever
MAX_RESULTS_CAP = 20   # limits how many abstracts one tool call can pull into the context
MAX_COST_USD = 0.75    # stop searching once one question has cost this much

SYSTEM_PROMPT = """You answer questions about biological targets using the PubMed literature.

Use the tools to search PubMed and read abstracts. Base your answer only on abstracts you have fetched. Cite each claim as [PMID 12345678], one PMID per bracket. If the evidence is thin or conflicting, say so."""

TOOLS = [
    {
        "name": "search_pubmed",
        "description": (
            "Search PubMed. Returns matching PMIDs ordered by relevance, plus the total number "
            "of matches in PubMed. Does not return abstracts; use fetch_abstracts to read papers.\n"
            "PubMed combines every term with AND, so each extra word narrows the search. Use 2-4 "
            "concepts, e.g. 'T4 lysozyme cavity mutant stability'. Long queries and author "
            "surnames usually return zero matches. If a search returns 0 results, remove terms "
            "rather than adding them."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "PubMed search query."},
                "max_results": {
                    "type": "integer",
                    "description": f"Number of PMIDs to return (default 10, maximum {MAX_RESULTS_CAP}).",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "fetch_abstracts",
        "description": "Fetch the title, authors, publication year and abstract for a list of PMIDs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pmids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": f"PubMed IDs, at most {MAX_RESULTS_CAP} per call.",
                },
            },
            "required": ["pmids"],
        },
    },
]

# Every number inside a PMID bracket: "[PMID 123]", "[PMIDs 123, 456]", "[PMID 123; PMID 456]"
BRACKET_CITATION = re.compile(r"\[PMIDs?\b[^\]]*\]")
# Unbracketed mentions in running text: "PMID 123", "PMID: 123"
BARE_CITATION = re.compile(r"\bPMID:?\s*(\d+)")


def run_tool(name, tool_input, retrieved):
    """Execute one tool call and return its result as a JSON string.

    Fetched papers are recorded in `retrieved` (pmid -> paper); that dict is
    the ground truth for citation checking.
    """
    if name == "search_pubmed":
        query = tool_input["query"]
        max_results = min(tool_input.get("max_results", 10), MAX_RESULTS_CAP)
        print(f'[searching pubmed: "{query}"]')
        result = pubmed.search_pubmed(query, max_results)
        print(f"[{result['total_count']} matches, {len(result['pmids'])} returned]")
        return json.dumps(result)

    if name == "fetch_abstracts":
        # Tool input is model output: coerce types rather than trust the schema.
        pmids = [str(pmid) for pmid in tool_input["pmids"]]
        if len(pmids) > MAX_RESULTS_CAP:
            raise ValueError(f"Too many PMIDs ({len(pmids)}); fetch at most {MAX_RESULTS_CAP} per call.")
        papers = pubmed.fetch_abstracts(pmids)
        for paper in papers:
            retrieved[paper["pmid"]] = paper
        print(f"[retrieved {len(papers)} abstracts]")
        return json.dumps(papers)

    raise ValueError(f"Unknown tool: {name}")


def cost_usd(stats):
    """Cost of this question so far, from the token counts the API reported.

    One formula, shared by the budget check and the final report, so the number
    the loop stops on is the number printed.
    """
    return (stats["input_tokens"] * INPUT_PRICE_PER_MTOK
            + stats["output_tokens"] * OUTPUT_PRICE_PER_MTOK) / 1_000_000


def send(client, messages, stats, tool_choice=None):
    """One API call, recording token usage in `stats` whatever the outcome."""
    extra = {"tool_choice": tool_choice} if tool_choice else {}
    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=messages,
        # If Opus 5's safety classifier declines, the API retries on another model.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        **extra,
    )
    stats["turns"] += 1
    stats["input_tokens"] += response.usage.input_tokens
    stats["output_tokens"] += response.usage.output_tokens
    if any(entry.type == "fallback_message" for entry in response.usage.iterations or []):
        stats["fallback_ran"] = True
    return response


def answer_text(response):
    """The text blocks of a response, joined. Thinking and tool_use blocks are skipped."""
    return "\n".join(block.text for block in response.content if block.type == "text").strip()


def final_answer(client, messages, stats):
    """Ask for an answer from the abstracts already fetched, with tools switched off.

    Used when the turn cap or the cost budget is reached, so a long run still
    produces something. This one call is allowed to exceed the budget: without it,
    the money already spent buys nothing at all.
    """
    messages.append({
        "role": "user",
        "content": "You have run out of search turns. Answer the question now, using only the abstracts you have already fetched.",
    })
    response = send(client, messages, stats, tool_choice={"type": "none"})
    return answer_text(response)


def run_agent(question):
    """Run the tool-calling loop until Claude gives a final answer.

    Returns (answer, retrieved, stats). `answer` is "" if no answer was produced;
    `stats["note"]` explains anything unusual. Never exits the process, so the
    caller can always report what the run cost.
    """
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": question}]
    retrieved = {}
    stats = {"turns": 0, "input_tokens": 0, "output_tokens": 0, "fallback_ran": False, "note": None}

    for _ in range(MAX_TURNS):
        if cost_usd(stats) >= MAX_COST_USD:
            stats["note"] = f"reached the ${MAX_COST_USD:.2f} budget; answered from the abstracts already fetched"
            print(f"[${MAX_COST_USD:.2f} budget reached: asking for an answer from what has been fetched]")
            return final_answer(client, messages, stats), retrieved, stats

        response = send(client, messages, stats)

        # Send back the full content, not just the text: tool_use and thinking
        # blocks must be returned unchanged on the next request.
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            return answer_text(response), retrieved, stats

        if response.stop_reason != "tool_use":
            # max_tokens, or a refusal the fallback model also declined
            details = f" ({response.stop_details.explanation})" if response.stop_details else ""
            stats["note"] = f"stopped early: stop_reason={response.stop_reason}{details}"
            return answer_text(response), retrieved, stats

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            try:
                content, is_error = run_tool(block.name, block.input, retrieved), False
            except Exception as error:
                # A failed tool goes back to the model as an error it can react to, not a crash.
                content, is_error = f"Error: {error}", True
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": content,
                "is_error": is_error,
            })
        # All results in one message; splitting them discourages parallel tool calls.
        messages.append({"role": "user", "content": tool_results})

    # Out of turns: same treatment as running out of budget.
    stats["note"] = f"hit the {MAX_TURNS}-turn cap; answered from the abstracts already fetched"
    print(f"[{MAX_TURNS}-turn cap reached: asking for an answer from what has been fetched]")
    return final_answer(client, messages, stats), retrieved, stats


def cited_pmids(text):
    """PMIDs cited in the answer, unique and in order of first appearance."""
    found = []
    for bracket in BRACKET_CITATION.findall(text):
        found.extend(re.findall(r"\d+", bracket))
    found.extend(BARE_CITATION.findall(text))
    return list(dict.fromkeys(found))


def check_citations(text, retrieved):
    """Split cited PMIDs into (verified, invented): fetched by a tool, or not."""
    cited = cited_pmids(text)
    verified = [pmid for pmid in cited if pmid in retrieved]
    invented = [pmid for pmid in cited if pmid not in retrieved]
    return verified, invented


def format_source(paper):
    authors = paper["authors"]
    if not authors:
        first_author = "Unknown authors"
    else:
        # "Matthews BW" -> "Matthews"; rsplit keeps multi-word surnames like "van der Waals"
        first_author = authors[0].rsplit(" ", 1)[0] + (" et al." if len(authors) > 1 else "")
    return f"  {paper['pmid']} - {first_author} ({paper['year']}) - {paper['title']}"


def report(answer, retrieved, stats):
    """Print the answer, its sources, any invented citations, and what the run cost."""
    verified, invented = check_citations(answer, retrieved)

    if answer:
        print("\n" + answer)
        print("\nSources:")
        for pmid in verified:
            print(format_source(retrieved[pmid]))
    if invented:
        print(f"\nWARNING: cited but never fetched (possibly invented): {', '.join(invented)}")

    cost = cost_usd(stats)
    print(
        f"\n[{stats['turns']} turns, {len(retrieved)} abstracts fetched, {len(verified)} cited, "
        f"{stats['input_tokens']:,} input + {stats['output_tokens']:,} output tokens, ~${cost:.3f}]"
    )
    if stats["fallback_ran"]:
        print(f"[note: a fallback model served at least one turn; cost uses {MODEL} prices]")
    if stats["note"]:
        print(f"[note: {stats['note']}]")


def main():
    if len(sys.argv) < 2:
        sys.exit('Usage: python agent.py "your question"')
    # Abstracts contain characters like Δ and °; without this, redirecting output
    # to a file on Windows falls back to cp1252 and crashes.
    sys.stdout.reconfigure(encoding="utf-8")

    question = " ".join(sys.argv[1:])
    answer, retrieved, stats = run_agent(question)
    report(answer, retrieved, stats)
    if not answer:
        sys.exit(1)


if __name__ == "__main__":
    main()
