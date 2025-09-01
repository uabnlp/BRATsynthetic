Evaluation Guide

This repository includes two main scripts for evaluating and visualizing text with medspaCy and spaCy.

Tools
- evaluation/medspacy2txt.py: Processes a directory of .txt files, collects counts/distributions, prints summary stats, and writes dependency-parse visualizations to HTML.
- evaluation/medspacy_evaluation.py: Computes aggregate statistics across a corpus laid out by BRATsynthetic types. Now parameterized via CLI.
- evaluation/displacy_test.py: Quick dependency visualization for a single file.

Prerequisites
- Two supported environments:
  - Main (Python 3.12, spaCy 3.8, en_core_web_lg): best for BRATsynthetic and new evaluations.
  - Legacy Eval (Python 3.9, spaCy 3.4.1, scispaCy 0.5.1 + en_core_sci_sm): for workflows that specifically rely on scispaCy.

Set up (recommended scripts)
- Main env (3.12):
  - bash scripts/setup_env_main.sh
  - source .venv-main/bin/activate
- Legacy eval env (3.9):
  - bash scripts/setup_env_legacy_eval.sh
  - source .venv-legacy/bin/activate
  - Install a compatible scispaCy model (if not provided via SCISPACY_MODEL), for example:
    - pip install https://github.com/allenai/scispacy/releases/download/v0.5.1/en_core_sci_sm-0.5.1.tar.gz

Manual setup (if you prefer)
- Main: create venv with Python 3.12, then `pip install -r requirements-main.txt` and run `python -m spacy download en_core_web_lg`.
- Legacy: create venv with Python 3.9, then `pip install -r requirements-eval-legacy.txt`.
  - Then install a compatible scispaCy model, e.g. the link above for 0.5.1.

Models
- Use `--model` to select the pipeline appropriate for your environment.
  - Main env: `--model en_core_web_lg`
  - Legacy env: `--model en_core_sci_sm` (provided via requirements-eval-legacy.txt)
- Sentence segmentation: PyRuSH is optional and not installed by default. The scripts will fall back to spaCy's `sentencizer` if PyRuSH is unavailable.

Running medspacy2txt.py
- Purpose: summarize counts/distributions and generate dependency visualizations.
- Usage:
  - Main env (3.12):
    - python evaluation/medspacy2txt.py --input-dir /path/to/texts --output-file evaluation/output.txt --model en_core_web_lg
  - Legacy env (3.9):
    - python evaluation/medspacy2txt.py --input-dir /path/to/texts --output-file evaluation/output.txt --model en_core_sci_sm
- Notes:
  - --input-dir: root directory; the script discovers .txt files recursively. If files are organized by BRATsynthetic variant (consist, random, markov, simple, orig) within the path, the script will infer the type from folder names.
  - --output-file: path for textual summary output. The parent directory is created if needed.
  - HTML visualizations are written under evaluation/Displays/. These files are ignored by git via .gitignore.
  - The dependency rendering uses the parsed spaCy doc (model_doc) to ensure a parser is present.

Running medspacy_evaluation.py
- Purpose: aggregate comparisons and divergence metrics across the BRATsynthetic types.
- CLI:
  - Main env (3.12):
    - python evaluation/medspacy_evaluation.py --root /path/to/corpus --model en_core_web_lg
  - Legacy env (3.9):
    - python evaluation/medspacy_evaluation.py --root /path/to/corpus --model en_core_sci_sm
  - Default root is ./test if not provided.
- Output includes Jensen–Shannon divergence metrics and context distributions.

Running displacy_test.py
- Visualize the dependency parse for a single text file.
- Usage:
  - python evaluation/displacy_test.py /path/to/file.txt
  - If no argument is provided, uses test_files/sample.txt.
- Output is written to evaluation/Displays/<name>_dependency_visualization.html

Alignment Notes
- The evaluation scripts replaced pylcs with Python’s difflib.SequenceMatcher for sequence alignment when compute_alignment is enabled. This changes behavior from exact LCS to block matching; results will not be identical to pylcs.

Troubleshooting
- Missing models: ensure the model specified via `--model` is installed in the active environment.
- Empty dependency visuals: confirm the model used for visualization includes a dependency parser component.
