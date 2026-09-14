# Build notes

A running log of what went wrong and what I learned while building the PubMed literature agent.

Categories:
- **Search terms**: bad queries, and whether the prompt or the tool description fixed them
- **Citations**: hallucinated or misattributed PMIDs, and how validation caught them
- **Plausible but wrong**: scientifically incorrect answers that looked right
- **Cost**: tokens and cost per query

---

## 2026-09-14: PubMed rewrites search terms before the model sees results

**Category:** Search terms (found while probing the raw E-utilities API, before any LLM was involved)

The query `T4 lysozyme thermal stability mutants` was not run as written. The esearch `querytranslation` shows that PubMed's Automatic Term Mapping expanded `lysozyme` to include:

- `"hen egg lysozyme"[Supplementary Concept]`
- `"muramidase"[MeSH Terms]`

It then ANDed that with a separate `"T4"[All Fields]`. So "T4" and "lysozyme" are not required to appear together as a phrase. Papers on hen egg-white lysozyme (HEWL), a different protein, can match if "T4" appears anywhere else in the record.

The top hit (PMID 32211456) was a computational free-energy model assessed *on* T4 lysozyme mutants, not experimental stability data.

**Why it matters:** an agent that trusts its search results could cite HEWL data as T4L data. Both are "lysozyme" and both have a large stability literature, so a non-specialist would not notice.

**Checked the same day:** quoting `"T4 lysozyme"` only cut the matches from 44 to 40, and no HEWL papers appeared in the top results either way. The term mapping is real, but it wasn't the main problem. The sort order was (next entry). Keep watching for HEWL results on other queries.

---

## 2026-09-14: E-utilities returns newest first, not best match

**Category:** Search terms (retrieval, still no LLM involved)

The PubMed website sorts by Best Match, but esearch without a `sort` parameter returned results in reverse date order. For `T4 lysozyme thermal stability mutants`, the top 5 were all 2016-2019 papers, mostly computational methods that use T4L as a benchmark. One was about chondroitinase and one about vaccine adjuvants.

Same query, top 5 PMIDs, first-author year:

| Order | Top 5 years | Examples |
|---|---|---|
| default | 2019, 2019, 2019, 2018, 2016 | free-energy models, QresFEP, chondroitinase |
| `sort=relevance` | 1988, 1985, 1991, 1989, 1987 | Wetzel (disulfides), Alber (genetic screen), Karpusas (cavity-filling) |
| `sort=relevance` + broader `"T4 lysozyme" stability mutant` | 1995, 1988, 2010, 2019, 1985 | Matthews 1995 review *Studies on protein stability with T4 lysozyme* at #1 |

**Why it matters:** with `max_results` of 5-10, the default order hides the foundational experimental literature. The model would reason over the wrong evidence, and it would be sound reasoning from that evidence, so the answer would look fine.

**Fix:** `search_pubmed` always sends `sort=relevance`. It's fixed in code rather than left to the model, because it's one fewer thing the model could get wrong.

**Also seen:** dropping `thermal` raised the matches from 44 to 150. Many stability papers talk about ΔΔG or denaturation rather than "thermal stability", so the model's choice of terms matters as much as the sort order.

---

## 2026-09-14: T4L fusion constructs as a citation trap

**Category:** Plausible but wrong (a risk to watch for; not yet produced by the agent)

PMID 30926935 (Wang 2019) is about the thermostability of a *CXCR1-T4 lysozyme* fusion. T4L is routinely fused into GPCRs to help them crystallise, so "T4 lysozyme" + "thermostability" pulls in GPCR construct engineering. That stability data is about the receptor construct, not T4L itself. An agent without that context could cite it as evidence about T4L mutants.
