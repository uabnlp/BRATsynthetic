
import os
from typing import List, Any, Optional
from .BratAnnotation import BratAnnotation, BratTag

class BratFile:
    """ Representation of Named Entity Recognition File. Contains the text and the tag for each file.
    Useful for translating from one document format to another.
    """

    @classmethod
    def load_from_file(cls, txt_path: str, ann_path: Optional[str] = None) -> 'BratFile':
        '''
        loads the text and annotations from path given.
        if ann_path is None will automatically check for an ann file associated with txt_path.
        '''
        with open(txt_path, 'r') as text_file:
            text_contents = text_file.read()

        if not ann_path:
            ann_path = os.path.splitext(txt_path)[0] + '.ann'

        if os.path.exists(ann_path):
            with open(ann_path, 'r') as ann_file:
                ann_contents = ann_file.read()
                ann_lines = [line.strip() for line in ann_contents.splitlines()]
        else:
            ann_lines = []

        annotations = []
        for line in ann_lines:
            try:
                annotation = BratAnnotation.from_ann_line(line)
                annotations.append(annotation)
            except ValueError as error:
                print(f'Skipping annotation line: {error}\n  >{line}<')
                # raise error

        brat_file = BratFile(text_contents, [ann for ann in annotations if ann]) #filter unparseable annotations
        brat_file.identifier = os.path.splitext(os.path.basename(txt_path))[0]
        return brat_file


    def __init__(self, text: str = '', annotations: List[BratAnnotation] = [], identifier: Any = None):
        """Creates Basic NERFile, Text and Annotations, (Identifier can be is whatever the user of this class wants, used in write_to_dir.)"""
        self.text = text
        self.annotations = annotations
        self.identifier: Any = identifier


    def __str__(self) -> str:
        return f'File Identifier: {str(self.identifier)} Annotations: {len(self.annotations)}'

    def __repr__(self) -> str:
        return str(self)

    def check_annotation(self, tag: BratTag) -> bool:
        len_text: int = len(self.text)
        if tag.start() < 0 or tag.end() < 0 or tag.start() > len_text - 1 or tag.end() > len_text:
            return False
        #else
        if tag.text != self.text[tag.start():tag.end()].replace('\n', ' '):
            return False
        #else
        return True

    def check_annotations(self) -> bool:
        """Checks that the annotations start and stop index and text match the
        text from the BratFile."""

        annotations_good: bool = True
        for index, tag in enumerate(self.annotations):
            if type(tag) == 'BratTag' and not self.check_annotation(tag):
                print(f"Error in BratFile tag at {index}: {tag}.")
                annotations_good = False

        return annotations_good

    def to_brat_ann(self) -> str:
        """Converts file to tuple for brat with text and annotation as string,
        only supports entities (T tokens)."""

        if not self.check_annotations():
            raise ValueError("Issue with annotations. Can not convert BratFile to Brat annotations format.")
            return
        # else
        return '\n'.join([annotation.to_ann_line() for annotation in self.annotations])

    @property
    def brat_tags(self) -> List[BratTag]:
        return [ann for ann in self.annotations if type(ann) == BratTag]

    @brat_tags.setter
    def brat_tags(self, tags: List[BratTag]):
        """
        WARNING: DOES NOT HANDLE UPDATING EVENTS AND ATTRIBUTES
        """
        self.annotations = [ann for ann in self.annotations if type(ann) != BratTag] + tags

    def update_tag_identifiers(self):
        """
        Updates identifiers of all BratTag, sorted by start, then end keys

        WARNING: Does not handle updating BratEvent, BratAttribute
        """

        tags = sorted(self.brat_tags, key=lambda x: (x.start, x.end))
        for index, tag in enumerate(tags):
            tag.identifier = BratTag.ANN_TYPE_IDENTIFIER + str(index+1)


    def write(self, ann_path: str):

        txt_path = os.path.splitext(ann_path)[0] + '.txt'

        with open(txt_path, 'w') as txt_file:
            txt_file.write(self.text)

        with open(ann_path, 'w') as ann_file:
            ann_file.write(self.to_brat_ann())

    def write_to_dir(self, dir: str):

        with open(os.path.join(dir, self.identifier + '.txt'), 'w') as txt_file:
            txt_file.write(self.text)

        with open(os.path.join(dir, self.identifier + '.ann'), 'w') as ann_file:
            ann_file.write(self.to_brat_ann())
