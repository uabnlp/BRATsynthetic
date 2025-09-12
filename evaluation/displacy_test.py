import spacy
from spacy import displacy
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description="Render dependency parse to HTML")
parser.add_argument("file", nargs="?", default="test_files/sample.txt", help="Input text file path")
parser.add_argument("--model", default="en_core_sci_sm", help="spaCy model to use (default: en_core_sci_sm)")
args = parser.parse_args()

nlp = spacy.load(args.model)
file_path = args.file

with open(file_path, "r", encoding="utf-8") as f:
    text = f.read().strip()
doc = nlp(text)

options = {
    'compact': True,
    'bg': '#f0f0f0',
    'color': 'black',
    'font': 'Arial',
    'distance': 100,
    'offset_x': 50,
    'arrow_stroke': 2,
    'arrow_width': 8
}

# Visualize the dependency tree with custom options
html = displacy.render(doc, style='dep', options=options)

# Generate output filename based on input filename
input_name = Path(file_path).stem
output_dir = Path("evaluation/Displays")
output_dir.mkdir(parents=True, exist_ok=True)
output_file = output_dir / f"{input_name}_dependency_visualization.html"

with open(output_file, "w") as f:
    f.write(html)

print(f"Visualization saved to {output_file}")
