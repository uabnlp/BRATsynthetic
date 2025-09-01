import spacy
from spacy import displacy
<<<<<<< HEAD
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
=======

nlp = spacy.load('en_core_web_lg')

#sentence = "Apple's CEO Tim Cook visited the company's headquarters in Cupertino."
file = "/data/user/ozborn/OUD/oud_2_10/synthetic/random/dev/1885374/1885374_26807773/1885374_26807773.txt"

with open (file, "r", encoding = "utf-8") as file:
    text = file.read().strip()
>>>>>>> Luis_err
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

<<<<<<< HEAD
# Generate output filename based on input filename
input_name = Path(file_path).stem
output_dir = Path("evaluation/Displays")
output_dir.mkdir(parents=True, exist_ok=True)
output_file = output_dir / f"{input_name}_dependency_visualization.html"

with open(output_file, "w") as f:
    f.write(html)

print(f"Visualization saved to {output_file}")
=======
with open("/data/user/lmansill/homedata/bratSynth/BRATsynthetic/evaluation/Displays/Random/dev/1885374_26807773(new)(lg).html", "w") as file:
    file.write(html)

print("Visualization saved to 1885374_26807773(lg).html")
>>>>>>> Luis_err
