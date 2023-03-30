import os
import re
from collections import defaultdict
from typing import List, Any, Optional, Dict, Tuple
from .BratAnnotation import BratAnnotation, BratEntity, BratEvent, BratAttribute

class BratFile:
    """ Representation of Named Entity Recognition File. Contains the text and the tag for each file.
    Useful for translating from one document format to another.
    """

    @classmethod
    def load_file_ann_file(cls, ann_path: str) -> 'BratFile':
        """
        loads the annotations from path given.
        if ann_path is None will automatically check for an ann file associated with txt_path.

        @param ann_path: path to the annotation file, assumes the .txt file is the same name with extension replaced.
        @return a BratFile created from the ann_path.
        """
        txt_path = os.path.splitext(ann_path)[0] + '.txt'
        return cls.load_from_file(txt_path, ann_path)

    @classmethod
    def load_from_file(cls, txt_path: str, ann_path: Optional[str] = None) -> 'BratFile':
        """
        loads the text and annotations from path given.
        if ann_path is None will automatically check for an ann file associated with txt_path.

        @param txt_path: path to txt_path to load from
        @param ann_path: path to the annotation file, if not given will replace .txt on txt_path with .ann to find it.
        @return a BratFile created from the txt_path and ann_path.
        """

        if not os.path.exists(txt_path):
            raise ValueError(f"Invalid path for BratFile.load_from_file: {txt_path} does not exist.")

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
                attribute.applied_annotations.append(related_ann)
                related_ann.applied_annotations.append(attribute)

        for event in self.events:
            if event.entity_identifier in self.identifier_to_annotation:
                related_ann = self.identifier_to_annotation[event.entity_identifier]
                event.applied_annotations.append(related_ann)
                related_ann.applied_annotations.append(event)

    @property
    def entities(self) -> List[BratEntity]:
        return [ann for ann in self.annotations if (type(ann) == BratEntity or ann.identifier_type == BratEntity.ANN_TYPE_IDENTIFIER)]

    @property
    def events(self) -> List[BratEvent]:
        return [ann for ann in self.annotations if (type(ann) == BratEvent or ann.identifier_type == BratEvent.ANN_TYPE_IDENTIFIER)]

    @property
    def attributes(self) -> List[BratAttribute]:
        return [ann for ann in self.annotations if (type(ann) == BratAttribute or ann.identifier_type == BratAttribute.ANN_TYPE_IDENTIFIER)]

    def replace_annotation(self, annotation_identifier: str, replacement_annotation: BratAnnotation):
        foundIndex = -1
        for index, annotation in enumerate(self.annotations):
            if annotation.identifier == annotation_identifier:
                foundIndex = index
                break
        if foundIndex != 0:
            self.annotations[foundIndex] = replacement_annotation


    def find_duplicate_annotation_in_list(self, input_list:List['BratAnnotation']):
        ann_str_to_ann = defaultdict(list)
        for annotation in input_list:
            ann_line = annotation.to_ann_line()

            ann_line_without_identifier = ann_line
            if ann_line.index('\t') > 0:
                ann_line_without_identifier = ann_line[ann_line.index('\t'):]

            ann_str_to_ann[ann_line_without_identifier].append(annotation)

        duplicate_annotations = []
        for k, v in ann_str_to_ann.items():
            if len(v) > 1:
                duplicate_annotations.append(v)
        return duplicate_annotations

    def find_entities_at_span(self, span: Tuple[int, int]) -> List['BratEntity']:
        found_entities = []
        for ent in self.entities:
            if ent.overlaps_span(span):
                found_entities.append(ent)

        return found_entities

    def find_duplicate_entities(self) -> List[List['BratEntity']]:
        return self.find_duplicate_annotation_in_list(self.entities)

    def find_duplicate_attributes(self) -> List[List['BratAttribute']]:
        return self.find_duplicate_annotation_in_list(self.attributes)

    def find_duplicate_events(self) -> List[List['BratEvent']]:
        return self.find_duplicate_annotation_in_list(self.events)

    def remove_duplicate_annotations(self):
        duplicate_annotations = self.find_duplicate_annotation_in_list(self.annotations)

        annotations_to_remove = []
        for annotations in duplicate_annotations:
            annotations_to_remove += annotations[1:]

        indices_to_remove = []
        for ann_to_remove in annotations_to_remove:
            identifier = ann_to_remove.identifier
            for index, ann in enumerate(self.annotations):
                if ann.identifier == identifier:
                    indices_to_remove.append(index)

        for index_to_remove in sorted(indices_to_remove, reverse=True):
            self.annotations.pop(index_to_remove)

        if len(self.find_duplicate_annotation_in_list(self.annotations)) > 0:
            print(f"FOUND {len(self.find_duplicate_annotation_in_list(self.annotations))} DUPLICATES AFTER CLEANING: ")
            print(self.find_duplicate_annotation_in_list(self.annotations))
            print()
            pass

        # assert 0 == len(self.find_duplicate_annotation_in_list(self.annotations)), "Removal of Duplicate Annotations was not successful."

    def __str__(self) -> str:
        return f'File Identifier: {str(self.identifier)} Annotations: {len(self.annotations)}'

    def __repr__(self) -> str:
        return str(self)

    def entity_text_from_spans(self, spans: List[Tuple[int, int]]) -> str:
        entity_text_lines: List[str] = []
        for span in spans:
            entity_text_lines.append(self.text[span[0]:span[1]])
        entity_text = ' '.join(entity_text_lines)
        entity_text = re.sub(r'\n+', ' ', entity_text)

        return entity_text

    def check_annotation(self, entity: BratEntity) -> bool:
        test_text = self.entity_text_from_spans(entity.spans)
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

        if not os.path.exists(dir):
            os.makedirs(dir)

        with open(os.path.join(dir, self.identifier + '.txt'), 'w', encoding='utf-8', newline='\n') as txt_file:
            txt_file.write(self.text)

        with open(os.path.join(dir, self.identifier + '.ann'), 'w', encoding='utf-8', newline='\n') as ann_file:
            contents = self.to_brat_ann()
            ann_file.write(contents)

    def update_identifier_nums(self):
        def start_span_key(ent):
            return ent.spans[0][0]

        ent_id_num_mappings = []
        all_entities = sorted(self.entities, key=start_span_key)

        attribute_num = 1
        event_num = 1
        for index, entity in enumerate(all_entities):
            entity: BratEntity = entity
            ent_id_num_mappings.append((entity.identifier_num, index+1))
            entity.identifier_num = index + 1

            old_applied_attributes = entity.applied_attributes
            new_applied_attributes = []
            for attr in old_applied_attributes:
                attr.ann_identifier = entity.identifier
                attr.identifier_num = attribute_num
                attribute_num += 1
                new_applied_attributes.append(attr)

            old_applied_events = entity.applied_events
            new_applied_events = []
            for event in old_applied_events:
                event.ann_identifier = entity.identifier
                event.identifier_num = event_num
                new_applied_events.append(event)
                event_num += 1

            entity.applied_annotations = new_applied_events + new_applied_attributes


        all_annotations = []
        for ent in all_entities:
            all_annotations.append(ent)
            all_annotations += ent.applied_annotations

        self.annotations = all_annotations

    def find_line_num_for_text_index(self, text_index: int) -> int:
        """
        Returns the line number in the associated text file that the text_index occurs on.
        """
        assert text_index >= 0 and text_index <= len(self.text), "text index outside bounds of file"

        return self.text[:text_index].count('\n')


if __name__ == '__main__':
    """For testing development"""

    txt_path = '/Users/tobiasoleary/web/nlp/uabnlpfileutils/uabnlpfileutils/brattools/samples/brat_sample/test.txt'
    ann_path = '/Users/tobiasoleary/web/nlp/uabnlpfileutils/uabnlpfileutils/brattools/samples/brat_sample/test.ann'

    bratfile = BratFile.load_from_file(txt_path, ann_path)

    entities = bratfile.entities

    for entity in entities:
        print('_' * 10)
        print(entity)
        print(f"  Applied Events: {entity.applied_events}")
        print(f"  Applied Attributes: {entity.applied_attributes}")

        print('-' * 10)

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

    with open(ann_path, 'r', newline='\n') as f:
        original_ann = f.read().replace("\r\n", "\n") # For random

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
