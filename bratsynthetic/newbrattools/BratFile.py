import os
import re
from typing import List, Any, Optional, Dict
from .BratAnnotation import BratAnnotation, BratEntity, BratEvent, BratAttribute

class BratFile:
    """ Representation of Named Entity Recognition File. Contains the text and the entity for each file.
    Useful for translating from one document format to another.
    """

    @classmethod
    def load_from_file(cls, txt_path: str, ann_path: Optional[str] = None) -> 'BratFile':
        """
        loads the text and annotations from path given.
        if ann_path is None will automatically check for an ann file associated with txt_path.

        @param txt_path: path to txt_path to load from
        @param ann_path: path to the annotation file, if not given will replace .txt on txt_path with .ann to find it.
        @return a BratFile created from the txt_path and ann_path.
        """
        with open(txt_path, 'r') as text_file:
            text_contents = text_file.read()

        if not ann_path:
            ann_path = os.path.splitext(txt_path)[0] + '.ann'

        if os.path.exists(ann_path):
            with open(ann_path, 'r') as ann_file:
                ann_contents = ann_file.read()
                ann_lines = [line for line in ann_contents.splitlines()]
        else:
            ann_lines = []

        annotations = []
        for line in ann_lines:
            try:
                annotation = BratAnnotation.from_ann_line(line)
                if annotation: # filter unparseable annotations
                    annotations.append(annotation)
            except ValueError as error:
                print(f"Ignoring line \"{line}\" in {ann_path} because {error}")

        brat_file = BratFile(text_contents, annotations)
        brat_file.identifier = os.path.splitext(os.path.basename(txt_path))[0]
        brat_file.ann_path = ann_path

        return brat_file

    def __init__(self, text: str = '', annotations: List[BratAnnotation] = [], identifier: Any = None, ann_path: str = None):
        """Creates Basic NERFile, Text and Annotations, (Identifier can be however the user of this class wants.)"""
        self.text = text
        self.annotations = annotations
        self.identifier: Any = identifier
        self.ann_path = ann_path
        self.identifier_to_annotation = self.__create_annotation_dict()
        self.__build_relations_for_annotations()

    def __create_annotation_dict(self) -> Dict[str, BratAnnotation]:
        id2ann: Dict[str, BratAnnotation] = {}
        for annotation in self.annotations:
            id2ann[annotation.identifier] = annotation
        return id2ann

    def __build_relations_for_annotations(self):

        for attribute in self.attributes:
            if attribute.ann_identifier in self.identifier_to_annotation:
                related_ann = self.identifier_to_annotation[attribute.ann_identifier]
                attribute.related_annotations.append(related_ann)
                related_ann.related_annotations.append(attribute)

        for event in self.events:
            if event.entity_identifier in self.identifier_to_annotation:
                related_ann = self.identifier_to_annotation[event.entity_identifier]
                event.related_annotations.append(related_ann)
                related_ann.related_annotations.append(event)

    @property
    def entities(self) -> List[BratEntity]:
        return [ann for ann in self.annotations if (type(ann) == BratEntity or ann.identifier_type == BratEntity.ANN_TYPE_IDENTIFIER)]

    @property
    def events(self) -> List[BratEvent]:
        return [ann for ann in self.annotations if (type(ann) == BratEvent or ann.identifier_type == BratEvent.ANN_TYPE_IDENTIFIER)]

    @property
    def attributes(self) -> List[BratAttribute]:
        return [ann for ann in self.annotations if (type(ann) == BratAttribute or ann.identifier_type == BratAttribute.ANN_TYPE_IDENTIFIER)]


    def __str__(self) -> str:
        return f'File Identifier: {str(self.identifier)} Annotations: {len(self.annotations)}'

    def __repr__(self) -> str:
        return str(self)

    def check_annotation(self, entity: BratEntity) -> bool:
        test_lines = []
        for span in entity.spans:
            test_lines.append(self.text[span[0]:span[1]])
        test_text = ' '.join(test_lines)
        test_text = re.sub(r'\n+', ' ', test_text)
        if entity.text != test_text:
            print(f"Entity Text and test_text do not match:\n  [{entity.text}]\n  [{test_text}]")
            return False
        # else
        return True

    def check_annotations(self) -> bool:
        """Checks that the annotations start and stop index and text match the
        text from the BratFile."""

        annotations_good: bool = True
        for index, entity in enumerate(self.annotations):
            if (type(entity) == BratEntity or entity.identifier_type == BratEntity.ANN_TYPE_IDENTIFIER) and not self.check_annotation(entity):
                print(f"Error in BratFile entity at {index}: {entity}")
                print(f"  Original Line: {entity.original_line}")
                print(f"  TEXT: [{self.text[entity.start():entity.end()]}]")
                annotations_good = False

        return annotations_good

    def to_brat_ann(self) -> str:
        """Converts file to tuple for brat with text and annotation as string."""

        # if not self.check_annotations():
        #     raise ValueError("Issue with annotations. Can not convert BratFile to Brat annotations format.")
        #     return

        if not self.check_annotations():
            annotations_to_ignore = []
            for ann in self.annotations:
                if (type(ann) == BratEntity or ann.identifier_type == BratEntity.ANN_TYPE_IDENTIFIER) and not self.check_annotation(ann):
                    entity_to_ignore: BratEntity = ann
                    print(f"Ignoring in BratFile entity: {entity_to_ignore} Text [{self.text[entity_to_ignore.start():entity_to_ignore.end()]}]")
                    annotations_to_ignore.append(entity_to_ignore)
                    annotations_to_ignore.extend(entity_to_ignore.applied_events)
                    annotations_to_ignore.extend(entity_to_ignore.applied_attributes)

            annotations_to_use = [annotation for annotation in self.annotations if annotation not in annotations_to_ignore]
            return '\n'.join([annotation.to_ann_line() for annotation in annotations_to_use])
        else:
            return '\n'.join([annotation.to_ann_line() for annotation in self.annotations])

    def write_to_dir(self, dir: str):

        with open(os.path.join(dir, self.identifier + '.txt'), 'w', encoding='utf-8', newline='\n') as txt_file:
            txt_file.write(self.text)

        with open(os.path.join(dir, self.identifier + '.ann'), 'w', encoding='utf-8', newline='\n') as ann_file:
            ann_file.write(self.to_brat_ann())

    def update_identifier_num(self, tag: BratEntity, new_num: int):
        assert False, "Not Implemented"
        pass


if __name__ == '__main__':
    """For testing development"""

    txt_path = '/Users/tobiasoleary/web/nlp/uabnlpfileutils/uabnlpfileutils/brattools/samples/brat_sample/test.txt'
    ann_path = '/Users/tobiasoleary/web/nlp/uabnlpfileutils/uabnlpfileutils/brattools/samples/brat_sample/test.ann'

    bratfile = BratFile.load_from_file(txt_path, ann_path)

    # for annotation in bratfile.annotations:
    #
    #     print(annotation)
    #
    #     if type(annotation) == BratEntity:
    #         entity: BratEntity = annotation
    #         print(f'Identifier: {entity.identifier}')
    #         print(f'Entity Type: {entity.entity_type}')
    #         print(f'Tag Text: {entity.text}')
    #         print(f'Original Line: {entity.original_line}')

    with open(ann_path, 'r', newline='\n') as f:
        original_ann = f.read()

    created_ann = bratfile.to_brat_ann()

    print("----Original Ann File----")
    print(original_ann)
    print("-------------------------")

    print("----Created Ann File----")
    print(created_ann)
    print("------------------------")

    original_ann_lines = original_ann.split('\n')
    create_ann_lines = bratfile.to_brat_ann().split('\n')

    success = True
    for i in range(len(original_ann_lines)):
        if i >= len(create_ann_lines):
            print(f"Missing Annotation Line at {i}: {original_ann_lines[i]}")
            success = False
        elif original_ann_lines[i].strip() != create_ann_lines[i].strip():
            success = False
            print("Lines not equal fail")
            print(f'  {original_ann_lines[i]}')
            print(f'  {create_ann_lines[i]}')

    if success:
        print("Success")
    else:
        print("Fail")
