import unittest
import os
from os import path

from .. import BratFile, BratEntity, BratEvent, BratAttribute

class BratFileTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.txt_path = path.join(path.dirname(__file__), 'resources', 'test.txt')
        self.ann_path = path.join(path.dirname(__file__), 'resources', 'test.ann')

    def test_relations(self):

        bratfile = BratFile.load_from_file(self.txt_path, self.ann_path)

        marry_entity: BratEntity = bratfile.identifier_to_annotation['T1']
        self.assertEqual(len(marry_entity.applied_annotations), 1)
        self.assertEqual(marry_entity.applied_annotations[0].identifier, 'E1')

        # There is a single related annotation and that is E1, should match the applied events
        self.assertListEqual(marry_entity.applied_annotations, marry_entity.applied_events)

        # Event Attributes should match the entity attributes, since both come through the event.
        self.assertListEqual(marry_entity.applied_attributes, marry_entity.applied_annotations[0].applied_attributes)

        print(marry_entity.applied_attributes)

    def test_input_equal_output(self):
        """For testing development"""

        bratfile = BratFile.load_from_file(self.txt_path, self.ann_path)

        # for annotation in bratfile.annotations:
        #
        #     print(annotation)
        #
        #     if type(annotation) == BratEntity:
        #         tag: BratEntity = annotation
        #         print(f'Identifier: {tag.identifier}')
        #         print(f'Tag Type: {tag.tag_type}')
        #         print(f'Tag Text: {tag.text}')
        #         print(f'Original Line: {tag.original_line}')

        with open(self.ann_path, 'r', newline='\n') as f:
            original_ann = f.read().strip()

        created_ann = bratfile.to_brat_ann()

        # print("----Original Ann File----")
        # print(original_ann)
        # print("-------------------------")
        #
        # print("----Created Ann File----")
        # print(created_ann)
        # print("------------------------")

        original_ann_lines = original_ann.split('\n')
        create_ann_lines = bratfile.to_brat_ann().split('\n')

        self.assertEqual(len(original_ann_lines), len(create_ann_lines))

        for i in range(len(original_ann_lines)):
            if original_ann_lines[i].strip() != create_ann_lines[i].strip():
                print("Lines not equal fail")
                print(f'  {original_ann_lines[i]}')
                print(f'  {create_ann_lines[i]}')
                self.assertEqual(original_ann_lines[i], create_ann_lines[i])

if __name__ == '__main__':
    unittest.main()
