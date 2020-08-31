from bratsynthetic import BratSynthetic

import os
from pathlib import Path


#TODO Add Parsing Args

if __name__ == '__main__':

    input_dir = '/Users/tobiasoleary/web/servers/brat/data/i2b2'
    output_dir = '/Users/tobiasoleary/web/servers/brat/data/i2b2_deid'

    files = [os.path.join(input_dir, file) for file in os.listdir(input_dir) if file.endswith('.txt') and 'deid' not in file]

    print(f"Processing {len(files)} files...")

    brat_synthetic = BratSynthetic(simple_replacement=False)
    for index in range(len(files)):
        txt_path = files[index]
        print(f"  [{index+1}]: {os.path.basename(txt_path)}")

        replaced_text = brat_synthetic.syntheticize(txt_path)

        output_txt_path = os.path.join(output_dir, os.path.basename(txt_path))
        output_ann_path = os.path.splitext(output_txt_path)[0] + '.ann'

        with open(output_txt_path, 'w', newline='\n', encoding='utf-8') as out_file:
            out_file.write(replaced_text)

        # Touch the annotation file.
        Path(output_ann_path).touch(exist_ok=True)
