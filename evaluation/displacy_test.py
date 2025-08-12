import spacy
from spacy import displacy

nlp = spacy.load('en_core_web_lg')

#sentence = "Apple's CEO Tim Cook visited the company's headquarters in Cupertino."
file = "/data/user/ozborn/OUD/oud_2_10/synthetic/random/dev/1885374/1885374_26807773/1885374_26807773.txt"

with open (file, "r", encoding = "utf-8") as file:
    text = file.read().strip()
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

with open("/data/user/lmansill/homedata/bratSynth/BRATsynthetic/evaluation/Displays/Random/dev/1885374_26807773(new)(lg).html", "w") as file:
    file.write(html)

print("Visualization saved to 1885374_26807773(lg).html")
