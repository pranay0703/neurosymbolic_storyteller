Okay, here is the content you provided, formatted as a README.md file.


# Neurosymbolic Storyteller

A hybrid AI system that combines neural language generation (via a local Ollama LLM) with symbolic consistency checks to generate and iteratively improve narratives. Each draft is parsed for character and temporal facts, validated against a set of logical rules (e.g., no dead characters acting, no contradictory traits, no temporal contradictions), and automatically revised until no violations remain or a configurable maximum iteration count is reached.

---

## Table of Contents

1.  [Features](#features)
2.  [Prerequisites](#prerequisites)
3.  [Installation & Setup](#installation--setup)
4.  [Usage](#usage)
    * [Command-Line Interface (CLI)](#command-line-interface-cli)
    * [Web Interface (Gradio)](#web-interface-gradio)
    * [Unit Tests](#unit-tests)
    * [Example Prompts](#example-prompts)
5.  [Project Structure](#project-structure)
6.  [How It Works](#how-it-works)
7.  [Extending & Customizing](#extending--customizing)
8.  [License](#license)

---

## Features

-   **Neural Generation**: Leverages a local Llama 2 (7B) model via the Ollama runtime to produce creative story drafts.
-   **Symbolic Validation**: Applies logical rules (e.g., no dead characters acting, no contradictory traits, no temporal contradictions) to ensure narrative consistency.
-   **Self-Improvement Loop**: Automatically revises drafts by feeding detected violations back to the language model, looping up to a configurable number of iterations.
-   **SQLite Persistence**: Logs each iteration’s prompt, draft text, and detected violations to `data/stories.db` for auditing and analysis.
-   **Multiple Interfaces**:
    -   **CLI**: Quick command-line usage with optional verbose iteration details.
    -   **Web UI**: Gradio-based interface for interactive story generation and violation breakdown.
-   **Modular & Extensible**: Easily add new symbolic rules or swap in a different local LLM model.

---

## Prerequisites

1.  **macOS 12+**
2.  **Homebrew** (for installing Ollama)
3.  **Python 3.8+** (with `venv` support)
4.  **Git** (for version control)
5.  **Ollama** (local LLM runtime; installable via Homebrew)

---

## Installation & Setup

1.  **Clone (or create) the repository**
    ```bash
    git clone [https://github.com/](https://github.com/)<your-username>/neurosymbolic_storyteller.git
    cd neurosymbolic_storyteller
    ```

2.  **Create & activate a Python virtual environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    Your shell prompt should now show `(venv)`.

3.  **Install Python dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Download spaCy’s English model**
    ```bash
    python3 -m spacy download en_core_web_sm
    ```

5.  **Install Ollama via Homebrew** (in a separate terminal tab; do not activate the `venv` here)
    ```bash
    brew update
    brew install ollama
    ```

6.  **Start the Ollama server** (keep this running while using the project)
    ```bash
    ollama serve
    ```

7.  **Pull the Llama 2 7B Chat model** (in another terminal tab)
    ```bash
    ollama pull llama2:7b-chat
    ```
    Wait for the download to finish. Verify with:
    ```bash
    ollama list
    ```
    You should see "llama2:7b-chat" listed.

8.  **Return to your `venv` terminal** (`(venv)` active) to run tests, the CLI, or the Web UI.

---

## Usage

### Command-Line Interface (CLI)

Ensure Ollama is running (Terminal A):
```bash
ollama serve
```

In another tab (Terminal B), activate your `venv` and run:
bash
cd ~/neurosymbolic_storyteller/src # Adjust path if necessary
source ../venv/bin/activate

python3 cli.py \
  --prompt "Write a story where Alice dies in chapter 1, then speaks in chapter 2." \
  --iterations 3 \
  --model llama2:7b-chat \
  --verbose

**Output:**
Iteration 1: Initial draft + detected violations (if any).
Iteration 2 & 3: Revised drafts until no violations remain or max iterations reached.
Final Story and a summary of “violations fixed” appear at the end.

### Web Interface (Gradio)

Terminal A (keep Ollama running):
bash
ollama serve


Terminal B (activate `venv`):
bash
cd ~/neurosymbolic_storyteller/src # Adjust path if necessary
source ../venv/bin/activate
python3 web_interface.py

Open your browser to `http://localhost:7860/`.

Enter a story prompt, select your Ollama model (e.g., `llama2:7b-chat`), set max iterations, then click **Generate Story**.

**UI Displays:**
-   Final Story
-   Summary (iterations count, violations fixed, word count)
-   Iteration Details (if enabled)

### Unit Tests

bash
cd ~/neurosymbolic_storyteller/tests # Adjust path if necessary
source ../venv/bin/activate
python3 test_basic.py

-   `test_character_addition`: Verifies that adding a character to the story state works.
-   `test_death_violation_detection`: Ensures that a “dead character acting” violation is detected.
-   `test_temporal_consistency`: Ensures contradictory time phrases are flagged.

All tests should pass with “OK.”

### Example Prompts

bash
cd ~/neurosymbolic_storyteller/examples # Adjust path if necessary
source ../venv/bin/activate
python3 example_prompts.py

Contains a set of example prompts designed to trigger specific violations:
-   Character Death
-   Trait Contradiction
-   Temporal Inconsistency
-   No Violations (baseline)

**Output:** Example description, expected violations, final story, and detected violations.

---

## Project Structure

text
neurosymbolic_storyteller/
├── data/
│   └── stories.db              ← SQLite database (auto-created)
├── docs/
├── examples/
│   └── example_prompts.py      ← Demo prompts & expected violations
├── notebooks/
│   └── storyteller_demo.ipynb  ← Jupyter notebook demo
├── src/
│   ├── storyteller_engine.py   ← Core engine: parser, validator, generator, loop
│   ├── cli.py                  ← Command-line interface
│   └── web_interface.py        ← Gradio web interface
├── tests/
│   └── test_basic.py           ← Unit tests for parser & validator
├── .gitignore
├── requirements.txt
└── README.md                   ← This file


---

## How It Works

1.  **Initial Draft**:
    * The user submits a prompt (via CLI or Web).
    * `NeuralGenerator.generate_story()` calls `ollama.chat()` to produce an initial story draft.

2.  **Parsing**:
    * `StoryParser.parse_story()` uses spaCy (if available) to extract entities (characters, locations) and update statuses.
    * Falls back to a simple regex-based parser if spaCy is not installed.

3.  **Symbolic Validation**:
    * `SymbolicValidator.validate()` runs each rule:
        * `character_death`: Flags if a “dead” character performs any action.
        * `temporal_consistency`: Flags contradictory temporal phrases (e.g., “morning … evening … morning”).
        * `character_consistency`: Flags contradictory trait statements (e.g., “Alice was brave” vs. “Alice was cowardly”).

4.  **Self-Improvement Loop**:
    * If violations exist and the loop count is less than `max_iterations`, build a feedback prompt:
        ```text
        Please improve the following story by addressing these issues:

        - [Violation 1 description]
          Suggestion: [Optional suggestion]
        - [Violation 2 description]
          Suggestion: [Optional suggestion]
        …

        Original Story:
        [<draft text>]

        Improved Story (keep the same general plot but fix the issues):
        ```
    * `NeuralGenerator.improve_story()` sends this prompt back to Ollama, producing a revised draft.
    * Parse → Validate → (repeat) until no violations remain or `max_iterations` reached.

5.  **Persistence & Output**:
    * Each iteration is stored in `data/stories.db` (SQLite), capturing:
        * Prompt text
        * Iteration number
        * Draft text
        * JSON‐serialized list of violations
        * Timestamp
    * The final story and summary (iterations used, violations fixed) are returned to the user.

---

## Extending & Customizing

### Adding New Symbolic Rules

1.  Open `src/storyteller_engine.py`.
2.  In class `SymbolicValidator`, add a new method:
    ```python
    def _check_<new_rule_name>(self, text: str, story_state: StoryState) -> List[StoryViolation]:
        violations = []
        # Implement your rule logic (regex or custom checks)
        return violations
    ```
3.  Register this rule in the `__init__` dictionary:
    ```python
    self.rules = {
        'character_death': self._check_character_death,
        'temporal_consistency': self._check_temporal_consistency,
        'character_consistency': self._check_character_traits,
        '<new_rule_name>': self._check_<new_rule_name>
    }
    ```
4.  Write corresponding unit tests in `tests/test_basic.py` to cover your new rule.
5.  Re-run `python3 -m pytest` or `python3 tests/test_basic.py` to verify everything passes.

### Swapping Local LLM

To use a different model (e.g., `tinyllama`), simply pass `--model tinyllama` to the CLI or select it in the Web UI.
Before that, ensure you have pulled it via Ollama:
```bash
ollama pull tinyllama
```

### Tweaking Generation Parameters

In `NeuralGenerator.generate_story()` or `.improve_story()`, you can modify `temperature`, `num_predict` (max tokens), or other Ollama options to adjust creativity, length, or sampling behavior.

---

## License

This project is released under the MIT License. See `LICENSE` for details.
```
