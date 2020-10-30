
from typing import Optional, List, Tuple

class BratAnnotation(object):

    def __init__(self, identifier: str):
        self.identifier = identifier
        self.original_line: Optional[str] = None

    @classmethod
    def from_ann_line(cls, ann_line: str) -> 'BratAnnotation':
        split = ann_line.split('\t')
        parsed_annotation = None
        if len(split) > 1:
            annotation_type = split[0][0]
            if annotation_type == 'T':
                parsed_annotation = BratTag.from_ann_line(ann_line)
            elif annotation_type == 'E':
                parsed_annotation = BratEvent.from_ann_line(ann_line)
            elif annotation_type == 'A':
                parsed_annotation = BratAttribute.from_ann_line(ann_line)
            else:
                print(f"No Class Match for line: {ann_line}")

        return parsed_annotation


    def to_ann_line(self) -> str:
        raise NotImplemented("to_brat_ann_line must be implemented by sub-class")
        pass

    @property
    def identifier_num(self) -> int:
        return int(self.identifier[1:])

    @identifier_num.setter
    def identifier_num(self, value: int):
        self.identifier = f"{self.identifier[:1]}{value}"

    @property
    def identifier_type(self) -> str:
        return self.identifier[:1]

class BratTag(BratAnnotation):
    """Simple BratTag class for use with BratFile.py"""

    ANN_TYPE_IDENTIFIER = 'T'

    @classmethod
    def from_ann_line(cls, ann_line: str) -> Optional['BratTag']:

        # Split the annotation line into components
        # Sample: T1	Protein 1881 1888;1892 1901	general confusion
        split = ann_line.strip().split('\t')
        if len(split) == 3:
            ann_type, entity_txtrange, text = ann_line.split('\t')
            tag_num = int(ann_type[1:])
            tag_type = entity_txtrange[:entity_txtrange.find(' ')]
            txtranges = entity_txtrange[entity_txtrange.find(' ') + 1:]
            txtranges = [(int(fragment_range.split(' ')[0]), int(fragment_range.split(' ')[1])) for fragment_range in
                         txtranges.split(';')]

            return BratTag(ann_type, tag_type, txtranges, text)

        else:
            print("Unable to process ann_line: " + ann_line)
            return None

    def to_ann_line(self) -> str:

        # Combine into Annotation Line
        # Sample: T1	Protein 1881 1888;1892 1901	general confusion
        txtranges = ';'.join([f'{span[0]} {span[1]}' for span in self.spans])
        entity_txtranges = f'{self.tag_type} {txtranges}'

        ann_line = '\t'.join([self.identifier, entity_txtranges, self.text])
        return ann_line


    def __init__(self, identifier: str, tag_type: str = "", spans: List[Tuple[int, int]] = [], text: str = ""):
        """
        Create BratTag

        :param identifier: BRAT identifier
        :param tag_type: Tag type
        :param spans: tuple of start / end of the text
        :param text: full text of the tag.
        """
        super().__init__(identifier)
        self.tag_type = tag_type
        self.spans = spans
        self.text = text

        len_of_spans = sum([span[-1] - span[0] + 1 for span in spans]) - 1
        if not len(text) == len_of_spans:
            span_txt = ";".join([f"{span[0]} {span[1]}" for span in self.spans])
            raise ValueError(f"({identifier}) Text length ({len(text)}) != span length ({len_of_spans}) [{span_txt}]:\n  >{self.text}<")


    @property
    def start(self) -> Optional[int]:
        if len(self.spans) > 0:
            return self.spans[0][0]
        else:
            return None
    @property
    def end(self):
        if len(self.spans) > 0:
            return self.spans[-1][-1]
        else:
            return None

    def __str__(self):
        identifier_txt = 'NONE' if not self.identifier else self.identifier
        return f'{identifier_txt} {self.tag_type} ({self.start}, {self.end}) "{self.text}"'

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if self is other:
            return True
        if type(self) != type(other):
            return False

        return self.tag_type == other.tag_type \
               and self.start == other.start \
               and self.end == other.end \
               and self.text == other.text

class BratEvent(BratAnnotation):

    ANN_TYPE_IDENTIFIER = 'E'

    @classmethod
    def from_ann_line(cls, ann_line: str) -> Optional['BratEvent']:
        # Parse BratEvent from ann_line
        # Sample line: E1    SUD:T3

        split = ann_line.split('\t')
        if len(split) == 2:
            identifier, event_info = split
            event_num = int(identifier[1:])
            event_type, tag_identifier = event_info.split(':')
            return BratEvent(identifier, event_type, tag_identifier)

    def to_ann_line(self) -> str:
        # Sample line: E1    SUD:T3
        return '\t'.join([self.identifier, ':'.join([self.event_type, self.tag_identifier])])

    def __init__(self, identifier: str, event_type: str, tag_identifier: str):
        super().__init__(identifier)

        self.event_type = event_type
        self.tag_identifier = tag_identifier

    def __str__(self):
        return self.to_ann_line()

    def __repr__(self):
        return str(self)


class BratAttribute(BratAnnotation):

    @classmethod
    def from_ann_line(cls, ann_line: str) -> Optional['BratAttribute']:
        # Sample Line: A2	DocTimeRel T17 Before

        split = ann_line.split('\t')
        if len(split) == 2:
            identifier, attribute_info = split

            attribute_type, tag_identifier, attribute_value = attribute_info.split(' ')
            return BratAttribute(identifier, attribute_type, tag_identifier, attribute_value)
        else:
            return None

    def to_ann_line(self) -> str:
        # Sample Line: A2	DocTimeRel T17 Before
        return '\t'.join([self.identifier, ' '.join([self.type, self.tag_identifier, self.value])])

    def __init__(self, identifier: str, type: str, tag_identifier: str, value: str):
        super().__init__(identifier)

        self.type = type
        self.tag_identifier = tag_identifier
        self.value = value

    def __str__(self):
        return self.to_ann_line()

    def __repr__(self):
        return str(self)
