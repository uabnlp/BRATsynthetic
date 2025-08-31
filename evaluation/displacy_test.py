import spacy
from spacy import displacy
import sys
import os
from pathlib import Path

nlp = spacy.load('en_core_web_lg')

# Use command line argument or default test file
if len(sys.argv) > 1:
    file_path = sys.argv[1]
else:
    # Default relative path from project root
    file_path = "test_files/sample.txt"

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
