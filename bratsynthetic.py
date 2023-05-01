"""
Replaces tagged personal information text with synthetic substitutes.
Input is a directory of brat files.
Output is will create a new .text file for each file.

Tags starting with the following will be replaced:

AGE
BIOID
CITY
COUNTRY
DATE
DEVICE
DOCTOR
EMAIL
FAX
HEALTHPLAN
HOSPITAL
IDNUM
LOCATION-OTHER
MEDICALRECORD
ORGANIZATION
PATIENT
PHONE
PROFESSION
STATE
STREET
TIME
UNDETERMINED
URL
USERNAME
ZIP

"""

import argparse
import os

from bratsynthetic import BratSynthetic, BratSyntheticConfig


def load_config_file(config_file_path: str) -> BratSyntheticConfig:
    """
    Makes sure input directory exists. Creates output directory if it does not exist.
    """
    return BratSyntheticConfig(config_file_path)


def parse_args() -> argparse.Namespace:
    """
    Parse Program Arguments

    -c / --config_file - Configuration Parameters (See Sample File config.yaml)
    """

    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--config_file', type=str, metavar='FILE_PATH',
                        required=True,
                        help='Configuration File')

    args = parser.parse_args()

    return args


def makeSyntheticText(bratsyn, input_dir, output_dir, recurse):
    if not os.path.exists(input_dir):
        return
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    files = [os.path.join(input_dir, file) for file in os.listdir(input_dir) if file.endswith('.txt')]
    print(f"Processing {len(files)} files...")

    for index in range(len(files)):
        txt_path = files[index]
        ann_path = os.path.splitext(txt_path)[0] + '.ann'

        if os.path.exists(ann_path):
            print(f"  [{index + 1}]: {os.path.basename(txt_path)}")
        else:
            print(f"  [{index + 1}]: No ANN file skipping {os.path.basename(txt_path)}.")

        replaced_text, replaced_ann_text = bratsyn.syntheticize(txt_path)

        output_txt_path = os.path.join(output_dir, os.path.basename(txt_path))
        output_ann_path = os.path.splitext(output_txt_path)[0] + '.ann'

        with open(output_txt_path, 'w', newline='\n', encoding='utf-8') as out_file:
            out_file.write(replaced_text)

        with open(output_ann_path, 'w', newline='\n', encoding='utf-8') as out_ann_file:
            out_ann_file.write(replaced_ann_text)
    print(f"Finished Process. Output Dir: {output_dir}")

    if recurse:
        subdirs = [d.path.replace(input_dir, '').lstrip('\\/') for d in os.scandir(input_dir) if d.is_dir()]
        for sdir in list(subdirs):
            if os.path.join(input_dir, sdir) != output_dir:
                makeSyntheticText(bratsyn, os.path.join(input_dir, sdir), os.path.join(output_dir, sdir), recurse)

if __name__ == '__main__':

    args = parse_args()
    config: BratSyntheticConfig = load_config_file(args.config_file)

    brat_synthetic = BratSynthetic(config=config)
    makeSyntheticText(brat_synthetic, config.general.input_dir, config.general.output_dir, config.general.recursive)



