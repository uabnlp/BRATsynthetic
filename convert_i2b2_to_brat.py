"""
Converts I2B2 2014 Deid xml files to Brat files.
"""

import os
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from dataclasses import dataclass

import argparse

from bratsynthetic.brattools import BratFile, BratTag

from typing import List, Tuple

@dataclass
class I2B2Tag:
    #Sample Tag: <LOCATION id="P4" start="343" end="353" text="Clarkfield" TYPE="HOSPITAL" comment="" />
    supertype: str  # "LOCATION"
    id: str         # "P4"
    text: str       # "Clarkfield"
    type: str       # "HOSPITAL"
    start: int      # 343
    end: int        # 353
    comment: str    # ""

    def __init__(self):
        pass

    @classmethod
    def from_tag_element(cls, tag_element: Element) -> 'I2B2Tag':
        new_tag = I2B2Tag()
        new_tag.supertype = tag_element.tag
        new_tag.id = tag_element.attrib['id']
        new_tag.text = tag_element.attrib['text']
        new_tag.type = tag_element.attrib['TYPE']
        new_tag.start = int(tag_element.attrib['start'])
        new_tag.end = int(tag_element.attrib['end'])
        new_tag.comment = tag_element.attrib['comment']

        return new_tag

class I2B2BratConverter:

    @classmethod
    def _get_text_tags_from_xml(cls, src_xml: str) -> Tuple[str, List[I2B2Tag]]:
        # get text for src_xml
        tree = ElementTree.parse(src_xml)
        root = tree.getroot()
        text = root.findtext('TEXT')

        # get tags
        tags: List[I2B2Tag] = [I2B2Tag.from_tag_element(tag_elem) for tag_elem in root.findall('TAGS/*')]

        return text, tags

    @classmethod
    def _convert_i2b2_to_brat_tag(cls, i2b2_tag: I2B2Tag) -> BratTag:
        return BratTag(identifier=None, tag_type=i2b2_tag.type, spans=[(i2b2_tag.start, i2b2_tag.end)], text=i2b2_tag.text)


    @classmethod
    def convert_file(cls, src_xml: str) -> BratFile:
        """
        :param src_xml: Path to I2B2 xml file
        :return: BratFile representing the I2B2 xml file.
        """
        text, i2b2_tags = cls._get_text_tags_from_xml(src_xml)
        brat_tags = [cls._convert_i2b2_to_brat_tag(i2b2_tag) for i2b2_tag in i2b2_tags]
        brat_file = BratFile(text, brat_tags, identifier=os.path.basename(src_xml))
        brat_file.update_tag_identifiers()

        return brat_file

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

    paths_to_process = [os.path.join(input_dir, fname) for fname in os.listdir(input_dir) if fname.endswith('.xml')]

    print(f"Processing {len(paths_to_process)} files in {input_dir}")
    count = 0
    for src_xml in paths_to_process:
        ann_fname = os.path.splitext(os.path.basename(src_xml))[0] + '.ann'
        dest_ann = os.path.join(output_dir, ann_fname)

        try:
            brat_file = I2B2BratConverter.convert_file(src_xml)
            brat_file.write(dest_ann)
            count += 1
        except ValueError as err:   # Skip files causing errors
            print(f"Skipping {src_xml}")
            print(err)

    print(f"Output {count} files to {output_dir}")
    if count != len(paths_to_process):
        print(f"  Skipped {len(paths_to_process) - count} files due to errors")

