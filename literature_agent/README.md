# PubMed literature agent

A command-line agent that answers questions about a biological target by searching the scientific literature and citing what it used.

The point of it is that **the model decides its own search strategy**. It reads the question, picks search terms, looks at what comes back, and searches again if that was not enough. The tool-calling loop is hand-written: there is no agent framework, no vector database and no embeddings.

```
python agent.py "What is known about the thermal stability of T4 lysozyme mutants?"
```

## How it works

1. The question goes to Claude along with two tool definitions.
2. If the model asks for a tool, the tool runs and the result is appended to the conversation.
3. Repeat until the model returns a final answer, or the turn cap is reached.
4. Print the answer, the sources it actually cited, and what the query cost.

| Tool | What it does |
|---|---|
| `search_pubmed(query, max_results)` | NCBI E-utilities `esearch`. Returns PMIDs ordered by relevance, plus the total number of matches in PubMed. |
| `fetch_abstracts(pmids)` | NCBI E-utilities `efetch`. Returns title, authors, year and abstract. |

Both live in [`pubmed.py`](pubmed.py) as plain functions with no LLM involved, and can be run on their own:

```
python pubmed.py "T4 lysozyme cavity mutant stability"
```

NCBI E-utilities is free and needs no API key at this volume. Requests are rate-limited to three per second and send the `tool` and `email` parameters that NCBI asks for.

## Citation validation

Hallucinated citations are the obvious failure mode for a tool like this, so the check is deliberate rather than hopeful. Only PMIDs returned by `fetch_abstracts` count as retrieved: a PMID the model saw in a search result but never read does not qualify. Every PMID cited in the answer is checked against that set, and anything else is flagged:

```
WARNING: cited but never fetched (possibly invented): 12345678
```

On the run below, 18 PMIDs were cited and all 18 were verified.

## Model and cost controls

| Constant | Default | Why |
|---|---|---|
| `MODEL` | `claude-sonnet-5` | $2/$10 per million input/output tokens. `claude-opus-5` searches more thoroughly for about 9x the cost - see NOTES.md for a like-for-like comparison. |
| `MAX_COST_USD` | `0.75` | Checked before each API call from the token counts the API has reported. Over budget, the agent stops searching and answers from the abstracts it already has. |
| `MAX_TURNS` | `20` | Hard stop, so a confused model cannot loop forever. |
| `MAX_RESULTS_CAP` | `20` | Caps how many abstracts one tool call can pull into the conversation. |

The budget bounds the search, not the answer: the final "answer from what you have" call is allowed to exceed it, because refusing it would mean the money already spent bought nothing. A monthly spend limit in the Anthropic console is still the real backstop.

## Running it

Requires Python 3.11 or newer (developed on 3.12).

```
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1      # PowerShell; use .venv\Scripts\activate in cmd.exe
pip install -r requirements.txt
```

Two environment variables:

| Variable | Why |
|---|---|
| `ANTHROPIC_API_KEY` | From console.anthropic.com. A Claude subscription is not the same thing and will not authenticate the SDK. |
| `NCBI_EMAIL` | Contact address sent to NCBI, as their usage policy asks. The code refuses to run without it. |

Neither is stored in the repo; `.gitignore` covers `.venv/` and `.env`.

## Example transcript

Abridged from a real run on the default model. Elisions are marked `[...]`. The search lines, the `[retrieved ...]` lines and the final cost line are verbatim. The answer paragraphs are shortened; long source lines are wrapped to fit this page; and throughout, Unicode (arrows, en-dashes, `°C`, `T<sub>m</sub>`, and the ü in Grütter) is flattened to ASCII.

```
$ python agent.py "What is known about the thermal stability of T4 lysozyme mutants?"
[searching pubmed: "T4 lysozyme mutant thermal stability"]
[44 matches, 10 returned]
[searching pubmed: "T4 lysozyme cavity mutant stability"]
[33 matches, 10 returned]
[retrieved 15 abstracts]
[searching pubmed: "T4 lysozyme multiple mutations additivity stability free energy"]
[2 matches, 2 returned]
[searching pubmed: "T4 lysozyme engineered disulfide bonds increase melting temperature Matsumura"]
[2 matches, 2 returned]
[retrieved 4 abstracts]

## Thermal Stability of T4 Lysozyme Mutants: Summary of Findings

**2. Hydrophobic core packing and cavity mutations**
"Cavity-creating" substitutions (e.g., Leu->Ala) generally destabilize the protein in
proportion to the size of the cavity created, confirming the hydrophobic effect as the
dominant stabilizing force [PMID 7771320, PMID 1290931]. Conversely, "cavity-filling"
mutations designed to increase packing density (Leu133->Phe, Ala129->Val) were expected
to stabilize the protein via added hydrophobic contacts, but instead were slightly
destabilizing due to introduced steric strain [PMID 2682639].

[...]

**3. Disulfide bonds as stabilizers**
Of four disulfides tested (9-164, 21-142, 90-122, 127-154), the 9-164 and 21-142 bridges
raised Tm by 6.4 C and 11.0 C respectively, with the most effective bridges spanning
large loops and flexible regions of the protein [PMID 2671995]. Combining two or three
stabilizing disulfides produced roughly additive increases in Tm, with a triple-disulfide
variant showing a 23.4 C increase in melting temperature over wild type [PMID 2812028].

[...]

Sources:
  7771320 - Matthews (1995) - Studies on protein stability with T4 lysozyme.
  8566545 - Matthews (1996) - Structural and genetic analysis of the folding and function
            of T4 lysozyme.
  3856227 - Alber et al. (1985) - A genetic screen for mutations that increase the thermal
            stability of phage T4 lysozyme.
  3681997 - Grutter et al. (1987) - Structural studies of mutants of the lysozyme of
            bacteriophage T4. The temperature-sensitive mutant protein Thr157----Ile.
  [... 14 more ...]

[5 turns, 19 abstracts fetched, 18 cited, 37,437 input + 2,964 output tokens, ~$0.105]
```

## What surprised me

The full log is in [NOTES.md](NOTES.md). Four things stood out.

**E-utilities does not sort the way the PubMed website does.** With no `sort` parameter it returns newest first, not best match. My first searches came back full of 2016-2019 computational papers that use T4 lysozyme as a benchmark, and none of the foundational experimental work. Adding `sort=relevance` put Alber 1985, Wetzel 1988 and the Matthews 1995 review at the top. With only 5-10 results per search, that difference decides what the model gets to reason about, and the answer would have looked perfectly sound either way.

**The model wrote search queries like a person talking to Google.** PubMed ANDs every term, so each extra concept narrows the result set, and queries such as `enhanced protein thermostability entropy unfolding glycine alanine proline T4 lysozyme Matthews` matched nothing at all. Five of seventeen searches in the first run returned zero results, and it never produced an answer. Putting the search rules in the **tool description** rather than the system prompt cut that to two of twelve, and the run finished. The one failure that advice could not fix was the model searching for `WT*`, the lab shorthand for the cysteine-free background: a term that exists in specialists' conversation but not in any index.

**The cost is almost all resent context, and the model you pick changes behaviour, not just the rate.** The API is stateless, so every turn resends the whole conversation: on Opus 5 one question came to 163,000 input tokens against 7,000 output, because by the last turn it was re-sending all 40 abstracts it had fetched. I predicted Sonnet 5 would be 2.5x cheaper, since that is the ratio of the published rates. It came out **9.5x** cheaper — $0.105 against $0.994 — because it also searched four times instead of twelve and fetched 19 abstracts instead of 40, and in a loop that resends everything, doing less compounds. What the extra money bought on Opus 5 was breadth: 40 cited papers against 18, including whole topics the cheaper run never reached. Neither figure was predictable from the price list, which is the real lesson: in an agentic loop you have to measure the cost, not calculate it.

**The failure that validation cannot see.** The citation check confirms that a PMID was fetched, not that the claim attached to it is what the paper says. On the Opus 5 run every one of its 40 citations passed, and the numbers were right to the unit across the seven papers I checked by hand. But one sentence claimed that melting temperatures could be "correlated with high-resolution crystal structures", citing Elwell & Schellman 1977 alongside the Matthews 1995 review. The 1977 paper contains no crystallography: it is absorption, fluorescence, CD and van 't Hoff melting. The two cited papers between them support the sentence; neither supports it alone. That kind of claim-splicing is invisible to the validator, invisible to a reader who is not a structural biologist, and it is the error class I would worry about most in a production tool.

## Files

| File | |
|---|---|
| [`pubmed.py`](pubmed.py) | The two retrieval tools, no LLM involved |
| [`agent.py`](agent.py) | Tool definitions, the loop, citation validation, cost reporting |
| [`NOTES.md`](NOTES.md) | Running log of what went wrong and what fixed it |
| `requirements.txt` | `anthropic`, `requests` |
