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

---

## 2026-09-14: Run 1 - the model piles on search terms until nothing matches

**Category:** Search terms (first run of the full agent, Opus 5)

Question: *What is known about the thermal stability of T4 lysozyme mutants?* The agent made **17 searches and 4 fetch calls over 10 turns in 73 s**, then hit the turn cap with no answer.

**5 of the 17 searches returned zero matches.** All five were long, and two included author surnames:

- `enhanced protein thermostability entropy unfolding glycine alanine proline T4 lysozyme Matthews` - 0
- `T4 lysozyme cysteine-free WT* pseudo-wild-type stability` - 0
- `Alber Matthews contributions of hydrogen bonds Thr 157 lysozyme` - 1

PubMed ANDs every term, so each extra concept narrows the result set, and a query naming eight of them matches nothing. The model appears to be writing queries the way you would phrase a Google search, or as if recalling a specific paper it wants to find. Its 2-4 concept queries (`T4 lysozyme salt bridge stability mutant` - 11 matches) worked fine.

**Diagnosis:** the model doesn't know how the tool's search engine behaves. The tool descriptions are deliberately minimal (that was the plan - see the header), so this is the first thing to fix. Whether the fix belongs in the **tool description** or the **system prompt** is the interesting question, and the answer is worth recording.

**Fix:** applied to the **tool description** rather than the system prompt (see the Run 2 entry below for the before/after numbers).

---

## 2026-09-14: Run 1 cost is unrecorded, because of how my own code exits

**Category:** Cost

The token and cost report is printed in `main()` *after* `run_agent()` returns. When the agent hit the turn cap, `run_agent` called `sys.exit`, which skipped the report entirely. Real money was spent on 10 turns and there's no record of how much.

**Why it matters:** the failure mode that most needs measuring - a loop that runs away - is exactly the one that produced no measurement. Instrumentation has to survive the error path, or it only ever reports the cheap successful runs.

**Fix:** applied. `run_agent` no longer calls `sys.exit`; it returns `(answer, retrieved, stats)` with a `note` field, and `main` always calls `report()`. Token usage is accumulated in `send()`, so it is recorded even when a turn fails.

---

## 2026-09-14: Run 2 - putting the search rules in the tool description mostly worked

**Category:** Search terms

Same question, after adding to the `search_pubmed` **description** (not the system prompt) that PubMed ANDs every term, that 2-4 concepts work best, that author surnames usually return nothing, and that a zero-result search should be retried with *fewer* terms.

| | Run 1 (minimal description) | Run 2 (rules in the description) |
|---|---|---|
| Searches | 17 | 12 |
| Zero-result searches | 5 | 2 |
| Turns used | 10 (hit the cap, no answer) | 9 (answered) |

The queries got visibly shorter and more targeted. Two things did **not** fix themselves:

1. `T4 lysozyme WT* cysteine-free pseudo-wild-type stability` returned 0 in both runs. `WT*` is lab notation for the cysteine-free background; PubMed has nothing to match it to. The model is searching with jargon that only exists in a specialist's head, which no amount of query-syntax advice will fix.
2. `T4 lysozyme disulfide bonds engineered increased thermal stability Matsumura` still carried an author surname, despite the description saying not to. It happened to return 2 matches, so it was harmless - but the instruction was not reliably followed.

**Conclusion for the write-up:** the tool description was the right place for this. It is a property of the tool, and the fix cut the failure rate without touching the system prompt at all.

---

## 2026-09-14: Run 2 - citation validation passed, 40/40

**Category:** Citations

The answer cited 40 distinct PMIDs. All 40 were in `retrieved`, i.e. every one came from an abstract the tool had actually fetched. Nothing was flagged as invented.

Worth being precise about what this does and does not prove: the check confirms the *PMID was fetched*, not that the claim attached to it is what that paper says. Attribution accuracy needs domain knowledge and is checked separately (next entry).

---

## 2026-09-14: Run 2 cost - $0.99 per question, and it is nearly all resent abstracts

**Category:** Cost

| | |
|---|---|
| Turns | 9 |
| Input tokens | 163,239 |
| Output tokens | 7,121 |
| Estimated cost | $0.994 (Opus 5 at $5/$25 per MTok) |
| Wall clock | 133 s |

Input tokens are **23x** the output tokens. The reason is structural, not a bug: the API is stateless, so every turn resends the whole conversation, and by turn 9 that includes all 40 abstracts. Fetching 40 abstracts once cost around 15k tokens; resending them across turns is what produced 163k.

My pre-run estimate was 10-20p, so I was out by roughly 5x. What I had not accounted for was that the model fetches in batches of 10 across several turns, and each batch is then re-sent on every remaining turn.

**Levers, if this needs to be cheaper:** prompt caching on the conversation prefix (the obvious one), fewer abstracts per fetch, or dropping full abstract text from old turns once summarised. None applied yet - noted so the trade-off is a deliberate choice rather than an oversight.

---

## 2026-09-14: Run 2 - the citations are real, the numbers are right, and one attribution still isn't

**Category:** Plausible but wrong - *the most valuable category, and the validator cannot see any of it*

I re-fetched eight of the 40 cited abstracts and compared them against what the answer claimed. Seven were accurate in full quantitative detail:

| PMID | Claim in the answer | Verdict |
|---|---|---|
| 1553543 | 6 cavity mutants, 2.7-5.0 kcal/mol at pH 3, double mutant 8.3, cavities 24-150 Å³, ~2.0 kcal/mol constant term, 24-33 cal mol⁻¹ Å⁻³, ~20 cal mol⁻¹ Å⁻² | Correct, including units |
| 2671995 | 9-164 +6.4 °C, 21-142 +11.0 °C, other two neutral/destabilising, entropy-vs-strain trade-off | Correct |
| 2812028 | Triple disulfide +23.4 °C, roughly additive | Correct |
| 19384984 | 1.9 Å bond-angle distortion not reproduced at 1.1 Å; rotamer strain ~0.8 kcal/mol, ~25% of the loss | Correct |
| 1737020 | A82P/A93P/G113A only ~0.5 ± 0.4 kcal/mol; enthalpy changes larger than free-energy changes and often opposite in sign | Correct |
| 1420185 | I3P most destabilising of five site-3 substitutions, -3.0 kcal/mol; I3L mildly stabilising | Correct |
| 8605178 | Buried water in a barnase cavity mutant; "hydrophobic" cavities have polar lining atoms | Correct, **and explicitly labelled as barnase** rather than passed off as T4L - the exact trap logged in the fusion-construct entry above |

**The one that is wrong.** The opening sentence reads: *"...melting temperature and ΔΔG can be measured directly and correlated with high-resolution crystal structures [PMID 911878] [PMID 7771320]."*

Elwell & Schellman 1977 (PMID 911878) contains **no crystallography**. It is absorption, fluorescence, CD and reversible melting analysed by van 't Hoff. It genuinely supports the first half of the sentence (reversible two-state unfolding, so Tm is measurable); the structural half comes only from the Matthews 1995 review. Elsewhere the same paper is cited for Trp138→Tyr affecting stability while Trp126/158 substitutions were neutral, which is exactly what its abstract says.

**The pattern: claim-splicing.** A compound sentence carries two PMIDs, the union of the two papers supports the sentence, but neither paper supports it alone. Every citation passes the validator, because every PMID really was fetched and really is related. Spotting it needs someone who knows that T4 lysozyme crystallography postdates 1977 - it is invisible to a token-level or retrieval-level check, and invisible to a reader who is not a structural biologist.

**Not yet fixed.** Candidate approaches: ask for one citation per claim and split compound sentences; or a second validation pass that sends each sentence plus its cited abstracts back to the model and asks whether that abstract alone supports it. The second is a much better interview answer but costs another API call per sentence.

---

## 2026-09-14: The answer contains HTML in a plain-text CLI

**Category:** Search terms / output (minor, but it shows up in the transcript)

The run 2 answer wrote melting temperature as `T<sub>m</sub>` - an HTML subscript tag - and used Markdown headings and bold throughout. Nothing asked it to; the system prompt says nothing about formatting, so it defaulted to writing for a web page rather than a terminal.

Harmless here, and I left it in the transcript rather than tidying it away. Worth knowing that an unspecified output format means the model picks one, and for a CLI the choice will usually be wrong.

---

## 2026-09-14: Run 3 - Sonnet 5 on the same question is 9.5x cheaper, not 2.5x

**Category:** Cost (and the most useful cost lesson so far)

Same question, same code, only `MODEL` changed from `claude-opus-5` to `claude-sonnet-5`. Sonnet 5's rate is 2.5x lower ($2/$10 per MTok against $5/$25), so I predicted ~$0.40. The actual bill was **$0.105**.

| | Run 2, Opus 5 | Run 3, Sonnet 5 |
|---|---|---|
| Turns | 9 | 5 |
| Searches | 12 | 4 |
| Zero-result searches | 2 | 0 |
| Abstracts fetched | 40 | 19 |
| PMIDs cited | 40 | 18 |
| Input tokens | 163,239 | 37,437 |
| Output tokens | 7,121 | 2,964 |
| Wall clock | 133 s | 50 s |
| **Cost** | **$0.994** | **$0.105** |

**Why the gap between 2.5x and 9.5x.** Rate is only one factor. The cheaper model also *did less*: four searches instead of twelve, and 19 abstracts instead of 40. Because every turn resends the whole conversation, the abstract count multiplies across the remaining turns, so fetching half as much on half as many turns compounds. Cost in an agentic loop is driven by behaviour at least as much as by the price list, which means you cannot predict it from the rate card - you have to measure.

**What the money bought.** Opus 5 was more thorough: 40 papers against 18, and sections on helix-dipole electrostatics, long-range charge effects, buried hydroxyls, Gly->Ala/Xaa->Pro entropy arguments and site-96 saturation that Sonnet 5 never reached. Sonnet 5's answer is accurate but narrower. For a survey question, "$0.99 for twice the literature" is arguably the better deal; for repeated use it is 9.5x the bill. Both are defensible; the useful thing is having both numbers.

**Still not obeyed:** `T4 lysozyme engineered disulfide bonds increase melting temperature Matsumura` - an author surname again, despite the tool description saying not to. It returned 2 matches, so it did no harm, but two runs on two different models have now both ignored that instruction. Advice in a tool description is a nudge, not a constraint.

---

## 2026-09-14: A cost cap belongs in the loop, not just in the console

**Category:** Cost

Added `MAX_COST_USD` (0.75). Before each API call the loop computes the running cost from the token counts the API has already reported, and if it is over budget it stops searching and takes the same "answer from the abstracts you already have" path as the turn cap.

Three decisions worth being able to defend:

1. **One formula, two users.** `cost_usd()` is shared by the budget check and the final report, so the number the loop stops on is the number printed. Two copies of that arithmetic would eventually disagree.
2. **The final call is allowed to exceed the budget.** Refusing it would mean the money already spent bought nothing at all. The cap bounds the search, not the answer.
3. **$0.75, not $0.30.** A $0.30 cap sounded prudent but would have cut off the known-good Opus 5 run at roughly turn 7 - the cap has to sit above the cost of a normal successful question, or it silently degrades every answer. Set from measurement, not from taste.

The console-level monthly limit is still the real backstop: an in-code cap only governs runs that reach this code path.

---

## 2026-09-14: Run 3 attribution check - 4/4 correct, and the run 2 error did not recur

**Category:** Plausible but wrong (a negative result, which is still a result)

I re-fetched the four run-3 citations I had not already verified and compared them with the claims:

| PMID | Claim | Verdict |
|---|---|---|
| 8566545 | T4L tolerates extended alanine substitution; internal residues matter most; largest cavities most destabilising; nonpolar ligands rebind them | Correct |
| 10623513 | Small-to-large substitutions at Ala42/Ala98/Ala129 progressively destabilise; Ala129 much less so because of a pre-existing cavity | Correct, including the cavity explanation |
| 7869383 | Only Ser117, Leu118, Leu121 matter (>1 kcal/mol); pairwise combinations slightly non-additive in the *favourable* direction | Correct, including the direction |
| 1304882 | 21-142 disulfide raises Tm by 11 °C at pH 2, causes a 5.1° rigid-body domain rotation, and does not abolish hinge-bending | Correct - the abstract ends "enhances the stability of the protein without making the folded structure more rigid" |

**The interesting part:** run 2's claim-splicing error (Elwell & Schellman 1977 cited for "high-resolution crystal structures" it contains none of) did **not** recur. Sonnet 5 cited that same paper only for Trp138->Tyr affecting stability and activity, via van 't Hoff analysis, which is exactly what it says.

I would not conclude that the cheaper model is more careful with citations. It wrote a third as much text and made a third as many claims, so it had far fewer chances to overreach. The honest version is: **fewer claims, fewer errors, less coverage** - and one sample each is not a measurement.

**Minor:** 19 abstracts fetched, 18 cited. One paper was read and paid for but never used. Not worth fixing, but it is where a cost saving would come from if fetches were tightened.
