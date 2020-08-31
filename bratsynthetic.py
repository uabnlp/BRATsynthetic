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

import os
import argparse
from pathlib import Path

from bratsynthetic import BratSynthetic

def check_args(args: argparse.Namespace):
    """
    Makes sure input directory exists. Creates output directory if it does not exist.
    """

    if not (os.path.exists(args.input_dir) and os.path.isdir(args.input_dir)):
        print(f"Input dir does not exist: {args.input_dir}")
        exit(-1)

    if not (os.path.exists(args.output_dir) and os.path.isdir(args.output_dir)):
        print(f"Output dir does not exist. Creating {args.output_dir}")
        os.makedirs(args.output_dir)


def parse_args() -> argparse.Namespace:
    """
    Parse Program Arguments

    -i / --input_dir - Directory containing I2B2 2014 XML files to convert
    -o / --output_dir - Directory to output converted brat files to
    """

    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input_dir', type=str, metavar='INPUT_DIR',
                        required=True,
                        help='Directory containing I2B2 2014 XML files to convert')

    parser.add_argument('-o', '--output_dir', type=str, metavar='OUTPUT_DIR',
                        required=True,
                        help='Directory to output converted brat files to')

    args = parser.parse_args()

    return args


if __name__ == '__main__':

    args = parse_args()
    check_args(args)

    input_dir = args.input_dir
    output_dir = args.output_dir

    files = [os.path.join(input_dir, file) for file in os.listdir(input_dir) if file.endswith('.txt')]

    print(f"Processing {len(files)} files...")

    brat_synthetic = BratSynthetic(simple_replacement=False)
    for index in range(len(files)):
        txt_path = files[index]
        ann_path = os.path.splitext(txt_path)[0] + '.ann'

        if os.path.exists(ann_path):
            print(f"  [{index+1}]: {os.path.basename(txt_path)}")
        else:
            print(f"  [{index+1}]: No ANN file skipping {os.path.basename(txt_path)}.")

        replaced_text = brat_synthetic.syntheticize(txt_path)

        output_txt_path = os.path.join(output_dir, os.path.basename(txt_path))
        output_ann_path = os.path.splitext(output_txt_path)[0] + '.ann'

        with open(output_txt_path, 'w', newline='\n', encoding='utf-8') as out_file:
            out_file.write(replaced_text)

        # Touch the annotation file.
        Path(output_ann_path).touch(exist_ok=True)
