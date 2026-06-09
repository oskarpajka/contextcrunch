# Context Crunch — Project Plan

## Python Version: 3.10+

We get `match/case` (useful for the parser), modern type hints (`X | Y`), and still broad compatibility. Not bleeding edge, not legacy.

## Language: English only for v1

Token optimization rules are deeply language-specific. Translating other languages to English is a separate, riskier feature — saving it for later is the right call.

## Input Handling: Preserve everything non-instructional

Numbers, emojis, code, quoted strings, URLs, HTML tags, hex colors, file paths — all preserved as-is. Only the "instructional prose" around them gets compressed.

---

## Core Problem: Literal vs. Instructional Content

This is the hardest problem. Example:

```
"Create a paragraph in a HTML element that says 'hello world' and make the text color #FF0000"
```

Must become:

```
"Create HTML paragraph saying 'hello world' with text color #FF0000"
```

Not:

```
"Create HTML paragraph saying 'hi earth' with text color #FF0011"
```

**Protected content types we must detect and freeze:**

- Quoted strings (`'...'`, `"..."`, `` `...` ``), including nested quotes (`"She said 'hello'"`)
- Escaped characters within strings (`"It\'s tricky"`, `\"`, `\\`)
- Code blocks (`` ```...``` ``) and inline code (`` `code()` ``)
- HTML/XML tags (`<div>`, `</span>`)
- URLs and file paths
- Programming identifiers (camelCase, snake_case)
- Numbers, math expressions, hex values
- Emojis
- Markdown formatting markers
- Email addresses, IPs, domain names
- Structured data: JSON (`{"key": "value"}`), YAML, CSV, tables
- Regex patterns (`/pattern/flags`, `r"..."`, `re.compile(...)`)
- SQL queries and shell commands
- LaTeX / math expressions (`$...$`, `$$...$$`)
- UUIDs, version strings (`v1.2.3`), git hashes, hex dumps
- ISO 8601 dates and timestamps
- Base64 strings
- Mixed content: quoted strings containing HTML/code/URLs — outer protection takes priority

**Overlapping spans — resolution rules:**

1. Longest span wins when two detectors overlap (e.g., a URL inside a quoted string: the quote span wins because it fully contains the URL).
2. If spans are identical length, the detector with higher specificity wins: code block > quoted string > URL > plain identifier.
3. Adjacent spans of the same type are merged if the gap between them is ≤ 2 characters (handles split URLs or multi-part HTML tags).

---

## Compression Strategies (ordered by safety)

### Tier 1 — Safe (near-zero meaning loss)

| Strategy | Example |
|---|---|
| Filler word removal | "please basically just really" → removed |
| Verbose phrase shortening | "in order to" → "to", "due to the fact that" → "because" |
| Redundant article removal | "Create a function" → "Create function" |
| Whitespace normalization | Multiple spaces → single space |
| Unicode normalization | NFKC normalization for consistency before matching |

> **Caveat on article removal:** Dropping articles can shift definiteness ("Delete the file" → "Delete file" loses the reference to a specific file). When `level="safe"`, articles are preserved after imperative verbs that reference prior context.

### Tier 2 — Moderate (minimal meaning loss)

| Strategy | Example |
|---|---|
| Synonym replacement | "utilize" → "use", "approximately" → "about" |
| Contractions | "do not" → "don't", "it is" → "it's" |
| Instruction compression | "You should create" → "Create" |
| Passive → active voice | "It should be created" → "Create it" |
| Sentence merging | Combine overlapping sentences |

### Tier 3 — Aggressive (user opt-in only)

| Strategy | Example |
|---|---|
| Heavy abbreviation | Common phrases → shorthand |
| Structural reformatting | Reorder for token efficiency |
| Implicit context removal | Remove obvious context |

### Level ↔ Tier Mapping

| API `level` | Tiers applied |
|---|---|
| `"safe"` | Tier 1 only |
| `"balanced"` | Tier 1 + Tier 2 |
| `"aggressive"` | Tier 1 + Tier 2 + Tier 3 |

---

## Architecture

```
contextcrunch/
├── pyproject.toml
├── src/
│   └── contextcrunch/
│       ├── __init__.py          # Public API: crunch(), compress()
│       ├── crunch.py            # Main pipeline orchestrator
│       ├── normalizer.py        # Unicode/whitespace normalization (pre-pipeline)
│       ├── detector.py          # Identifies spans of protected (literal) content
│       ├── protector.py         # Masks detected spans with placeholders
│       ├── restorer.py          # Unmasks placeholders → original content
│       ├── parser.py            # Segments compressible zones into sentences/clauses
│       ├── strategies/
│       │   ├── __init__.py
│       │   ├── base.py          # Abstract base strategy
│       │   ├── filler.py        # Filler word removal
│       │   ├── contraction.py   # Contraction replacement
│       │   ├── verbose.py       # Verbose phrase → concise
│       │   ├── synonym.py       # Synonym shortening
│       │   ├── restructuring.py # Sentence restructuring
│       │   ├── whitespace.py    # Whitespace cleanup
│       │   └── normalize.py     # Unicode normalization
│       ├── token_counter.py     # tiktoken-based token counting
│       ├── config.py            # CompressionLevel, settings
│       └── types.py             # Segment, Change, CompressionResult types
├── data/
│   └── mappings/
│       ├── contractions.json
│       ├── filler_words.json
│       ├── verbose_phrases.json
│       └── synonyms.json
└── tests/
    ├── test_crunch.py
    ├── test_pipeline.py
    ├── test_detector.py
    ├── test_protector.py
    ├── test_restorer.py
    ├── test_parser.py
    ├── test_normalizer.py
    ├── test_token_counter.py
    ├── test_config.py
    ├── test_properties.py
    ├── test_regressions.py
    ├── test_tokenizers.py
    ├── test_strategies/
    │   ├── test_filler.py
    │   ├── test_contraction.py
    │   ├── test_verbose.py
    │   ├── test_synonym.py
    │   ├── test_restructuring.py
    │   ├── test_whitespace.py
    │   └── test_normalize.py
    └── bench_compression.py
```

---

## Public API Design

```python
import contextcrunch

result = contextcrunch.crunch(
    "Please create a function that basically just returns the sum of two numbers",
    level="safe",                    # "safe" | "balanced" | "aggressive"
    tokenizer="cl100k_base",         # or model="gpt-4o" (auto-maps to tokenizer)
    target_tokens=None,              # optional: hard ceiling; raises if unreachable
    custom_protect_patterns=None,    # list[re.Pattern] for domain-specific literals
    idempotent=True,                 # safe-level only: guarantee stable output
                                     # across repeated calls on the same string
)

result.compressed          # "Create function returning sum of two numbers"
result.original_tokens     # 18
result.compressed_tokens   # 8
result.savings_percent     # 55.6
result.changes             # [Change(type="filler", original="please", replacement="", span=(0,6)), ...]
                           # Spans always refer to the ORIGINAL text indices so consumers
                           # can map changes back without tracking cumulative offsets.
result.protected_spans     # [(12, 20), (45, 58)]  # byte/char spans preserved

# Convenience shortcut — returns just the compressed string
compressed = contextcrunch.compress(
    "Please create a function...",
    level="safe",
    tokenizer="cl100k_base",
)
# compressed == "Create function returning sum of two numbers"
```

**Error handling & constraints:**

- `InputTooLargeError` — raised when input exceeds a configurable byte limit (default 1 MB). Prevents accidental OOM on massive paste dumps.
- `TargetTokensUnreachableError` — raised when `target_tokens` is set but even aggressive compression cannot meet it.
- `EmptyInputError` — raised on empty or whitespace-only strings.
- All exceptions subclass `ContextCrunchError` for easy catching.

---

## Pipeline Flow

```
Input string
    ↓
1. Detect    → Identify protected character spans in the *original* text
               (quotes, code, URLs, regexes, SQL, etc.)
    ↓
2. Normalize → Produce a normalized *copy* (NFKC, whitespace collapse,
               lowercasing) used only for strategy matching. Original text
               and spans remain untouched.
    ↓
3. Tokenize  → Tokenize the original text to establish the baseline
               `original_tokens` count. Also build a character→token
               offset map so protected spans align with token boundaries.
    ↓
4. Protect   → Replace protected spans with stable placeholders that
               preserve character length (or track offset deltas). This
               prevents strategies from touching literals.
    ↓
5. Parse     → Split compressible zones into sentences/clauses using the
               normalized copy for matching, but map edits back to the
               original text.
    ↓
6. Compress  → Apply strategies based on compression level (Tier 1/2/3).
               Strategies operate on the mutable text; protected regions
               are skipped via the span mask.
    ↓
7. Restore   → Unmask placeholders → original content in exact character
               positions.
    ↓
8. Re-count  → Tokenize the *final reconstructed text* with the chosen
               tokenizer to get `compressed_tokens`. This is the only
               exact count; all intermediate counts are approximate.
    ↓
Output: CompressionResult
```

> **Why detect before normalize?** Lowercasing or collapsing whitespace before detection destroys case-sensitive literals (`CamelCase` → `camelcase`) and can fuse boundaries (`<div>  <span>` → `<div><span>`), making regex detectors miss spans or overlap incorrectly. Detection always runs on the original text; normalization is a read-only view for strategy dictionaries.
>
> **Why re-tokenize at the end?** BPE tokenizers are context-sensitive. Removing filler words shifts surrounding token boundaries (e.g., `" please"` + `" create"` can become `" create"` or even `"create"`). The only authoritative token count is from the final output string. The pipeline tracks approximate savings internally for strategy prioritization, but the reported `compressed_tokens` is always from a fresh tokenization pass.

---

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|---|---|
| Empty or whitespace-only input | Raise `EmptyInputError` (or return unchanged with 0 tokens, configurable) |
| 100% protected input | Return original unchanged; `savings_percent == 0.0`; `changes == []` |
| Nested quotes (`"She said 'hello'"`) | Outer double-quote span protects everything inside; inner single-quote detector is ignored |
| Escaped quotes inside strings (`"It\\'s"`) | Escaped character is part of the protected string span; backslash is preserved |
| URLs containing query params with quotes | URL detector (regex) span wins if longer than the quote detector's inner span |
| Multi-line code blocks with language tags | Full fence span (```` ```python\n...\n``` ````) is protected, including the fence markers |
| Unicode bidirectional text (RLM, LRM) | Preserved as-is; normalization skips bidirectional control characters |
| Zero-width joiners in emoji sequences (`👨‍👩‍👧‍👦`) | Treated as part of the emoji span; never split |
| Very long input (>1 MB) | Rejected by default; batch/streaming mode is a future feature |
| Mixed line endings (`\r\n` vs `\n`) | Normalized to `\n` during whitespace collapse; original preserved in output if not in a compressible zone |
| Markdown tables / CSV rows | Protected as structured data; compression only touches column headers if they are plain prose |

---

## Performance Considerations

1. **Compiled regex cache:** All detector regexes are compiled once at module load and stored in `detector._REGEX_CACHE`. This is thread-safe via immutable patterns.
2. **Character→token offset map:** Built lazily and cached per input string. For long inputs, this is the most expensive step after tokenization; consider a Cython or Rust extension if profiling shows it is a bottleneck.
3. **Strategy short-circuit:** Tier 1 strategies run first. If a Tier 1 pass yields `savings_percent >= 30%` and `level == "safe"`, the pipeline skips Tier 2/3 entirely.
4. **Memory:** The pipeline holds the original string, the normalized copy, the token list, and the placeholder-masked string simultaneously. Peak memory is ~4× input size — acceptable for <1 MB inputs.
5. **Repeated calls:** `crunch()` is deterministic and stateless. Repeated calls with identical inputs produce identical outputs, making it safe to wrap in LRU caches at the application layer.

---

## CLI / Tooling (v1.1+)

```bash
# Basic usage
contextcrunch "Please create a function that returns the sum of two numbers" --level safe

# Pipe from stdin
cat prompt.txt | contextcrunch --level balanced --tokenizer cl100k_base

# Check only: report savings without mutating
contextcrunch preview prompt.txt --level aggressive

# Batch process
contextcrunch batch prompts/*.txt --level safe --output-dir compressed/
```

The CLI shares the same Python API and configuration files, ensuring no drift between library and tool behavior.

---

## Testing Strategy

Beyond unit tests, the test suite must enforce the core invariant: **protected content never changes**.

| Test Category | Files | Purpose |
|---|---|---|
| Unit tests | `test_detector.py`, `test_protector.py`, `test_restorer.py`, `test_normalizer.py`, `test_token_counter.py`, `test_config.py` | Component isolation |
| Strategy tests | `test_strategies/test_*.py` | Each strategy in isolation; prove idempotency where applicable |
| Integration tests | `test_pipeline.py` | End-to-end flow with known inputs/outputs |
| Property-based tests | `test_properties.py` (Hypothesis) | Generate random strings with embedded literals; assert literals survive compression |
| Regression tests | `test_regressions.py` | One test per reported bug; prevents recurrence |
| Benchmarks | `bench_compression.py` | Measure tokens/sec and memory for 1 KB / 10 KB / 100 KB inputs |
| Tokenizer parity | `test_tokenizers.py` | Assert that changing `tokenizer` produces consistent relative savings across supported encoders |

> **CI gate:** Property-based tests run for 10,000 iterations on every PR. If any protected literal is mutated, the build fails.

---

## Key Dependencies

- **tiktoken** — Token counting (OpenAI models, `cl100k_base` / `o200k_base`)

That's a single mandatory dependency. Everything else is pure Python logic with JSON data files.

> **Tokenizer abstraction:** `token_counter.py` should expose a `Tokenizer` protocol from day one so adding Claude (`tokenizers`), Gemini, or Llama tokenizers later is a drop-in replacement, not a refactor.
>
> **`re` over `regex`:** Standard `re` handles all v1 patterns (quoted strings, code fences, HTML tags, URLs) without issues. The `regex` library's recursive pattern support is only needed if we add nested-fence detection later — add it only when required.

---

## Future Feature Ideas

| Feature | Description | Priority |
|---|---|---|
| Multi-model tokenizers | Support Claude (`tokenizers`), Gemini, Llama tokenizers | High |
| CLI tool | `pip install contextcrunch[cli]` with stdin/stdout support | High |
| Batch processing | `crunch_many()` for processing prompt arrays with shared config | High |
| Custom dictionaries | User-defined replacement mappings loaded at runtime | Medium |
| Compression report | Machine-readable JSON / human-readable markdown breakdown | Medium |
| Domain presets | "coding", "creative", "analytical" — tuned strategy weights and detectors | Medium |
| Interactive mode | User approves/rejects each change (TUI or web) | Medium |
| Prompt cache optimization | Reorder/structure prompts for prefix caching (e.g., static system prompts first) | Medium |
| Framework integrations | LangChain, LlamaIndex, Haystack plugins | Low |
| Confidence scoring | Rate how likely each change preserves meaning; reject below threshold | Low |
| Streaming API | Generator-based for very long prompts (>1 MB) | Low |
| Language detection + translation | Auto-detect non-English, translate to English if it saves tokens | Very Low (risky) |
| Reversibility / round-trip | Encode a diff map so the original can be reconstructed from `compressed` + `metadata` | Very Low (lossy by design) |

> **Caveat: AI-assisted compression** — Using an LLM to compress prompts contradicts the core value proposition (fast, deterministic, zero external cost, privacy-preserving). If explored, it should be a separate `contextcrunch.llm` sub-package, never the default path.
>
> **Caveat: Reversibility** — Tier 1 is mostly reversible, but Tier 2/3 are lossy (synonym replacement changes word choice, voice changes alter emphasis). True reversibility requires storing the full original, which defeats the purpose. A *diff map* is more honest: it records what changed, not a lossless encoding.
