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

On the run below, 40 PMIDs were cited and all 40 were verified.

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

Abridged from a real run. Elisions are marked `[...]`. The search lines, source list and cost line are verbatim; the answer paragraphs are shortened, and their Unicode (arrows, en-dashes, `°C`, `Å³`, `T<sub>m</sub>`) is flattened to ASCII.

```
$ python agent.py "What is known about the thermal stability of T4 lysozyme mutants?"
[searching pubmed: "T4 lysozyme mutant thermal stability"]
[44 matches, 20 returned]
[searching pubmed: "T4 lysozyme cavity creating mutant stability"]
[14 matches, 14 returned]
[retrieved 10 abstracts]
[retrieved 10 abstracts]
[searching pubmed: "T4 lysozyme helix propensity alanine substitution stability"]
[6 matches, 6 returned]
[searching pubmed: "T4 lysozyme hydrogen bond Thr157 stability"]
[1 matches, 1 returned]
[retrieved 10 abstracts]
[...]
[retrieved 5 abstracts]

## Hydrophobic core: cavity-creating mutations

Six Leu/Phe->Ala substitutions (L46A, L99A, L118A, L121A, L133A, F153A) destabilised
the protein by 2.7-5.0 kcal/mol at pH 3, and the double mutant L99A/F153A by
8.3 kcal/mol. In every crystal structure surrounding atoms relaxed inward but a cavity
always remained (24-150 A^3), with no ordered solvent inside. [PMID 1553543]

[...]

## Disulfide bonds

Engineered disulfides give the largest stability gains. Of four designed bridges in the
cysteine-free background, 9-164 and 21-142 raised Tm by 6.4 C and 11.0 C, whereas
90-122 and 127-154 were neutral or destabilising [PMID 2671995]. Combining bridges is
roughly additive, and a triple-disulfide variant melted 23.4 C above wild type
[PMID 2812028].

[...]

Sources:
  911878 - Elwell et al. (1977) - Stability of phage T4 lysozymes. I. Native properties...
  7771320 - Matthews (1995) - Studies on protein stability with T4 lysozyme.
  3856227 - Alber et al. (1985) - A genetic screen for mutations that increase the thermal
            stability of phage T4 lysozyme.
  1553543 - Eriksson et al. (1992) - Response of a protein structure to cavity-creating
            mutations and its relation to the hydrophobic effect.
  [... 36 more ...]

[9 turns, 40 abstracts fetched, 40 cited, 163,239 input + 7,121 output tokens, ~$0.994]
```

## What surprised me

The full log is in [NOTES.md](NOTES.md). Four things stood out.

**E-utilities does not sort the way the PubMed website does.** With no `sort` parameter it returns newest first, not best match. My first searches came back full of 2016-2019 computational papers that use T4 lysozyme as a benchmark, and none of the foundational experimental work. Adding `sort=relevance` put Alber 1985, Wetzel 1988 and the Matthews 1995 review at the top. With only 5-10 results per search, that difference decides what the model gets to reason about, and the answer would have looked perfectly sound either way.

**The model wrote search queries like a person talking to Google.** PubMed ANDs every term, so each extra concept narrows the result set, and queries such as `enhanced protein thermostability entropy unfolding glycine alanine proline T4 lysozyme Matthews` matched nothing at all. Five of seventeen searches in the first run returned zero results, and it never produced an answer. Putting the search rules in the **tool description** rather than the system prompt cut that to two of twelve, and the run finished. The one failure that advice could not fix was the model searching for `WT*`, the lab shorthand for the cysteine-free background: a term that exists in specialists' conversation but not in any index.

**The cost is almost all resent context.** One question came to 163,000 input tokens against 7,000 output. The API is stateless, so every turn resends the entire conversation, and by the last turn that included all 40 abstracts. My own estimate before the first run was 5x too low, because I had not thought about abstracts fetched in early turns being re-sent on every later one. It is about $1 a question as written, and prompt caching is the obvious lever if that matters.

**The failure that validation cannot see.** The citation check confirms that a PMID was fetched, not that the claim attached to it is what the paper says. In the run above, every one of 40 citations passed, and the numbers were right to the unit across the seven papers I checked by hand. But one sentence claimed that melting temperatures could be "correlated with high-resolution crystal structures", citing Elwell & Schellman 1977 alongside the Matthews 1995 review. The 1977 paper contains no crystallography: it is absorption, fluorescence, CD and van 't Hoff melting. The two cited papers between them support the sentence; neither supports it alone. That kind of claim-splicing is invisible to the validator, invisible to a reader who is not a structural biologist, and it is the error class I would worry about most in a production tool.

## Files

| File | |
|---|---|
| [`pubmed.py`](pubmed.py) | The two retrieval tools, no LLM involved |
| [`agent.py`](agent.py) | Tool definitions, the loop, citation validation, cost reporting |
| [`NOTES.md`](NOTES.md) | Running log of what went wrong and what fixed it |
| `requirements.txt` | `anthropic`, `requests` |
