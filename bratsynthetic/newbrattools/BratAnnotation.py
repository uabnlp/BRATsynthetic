
from dataclasses import dataclass
from typing import Optional, List, Tuple

import deprecation


class BratAnnotation(object):

    def __init__(self, identifier: str):
        self.identifier = identifier
        self.original_line: Optional[str] = None
        self.related_annotations: List[BratAnnotation] = []

    @classmethod
    def from_ann_line(cls, ann_line: str) -> 'BratAnnotation':
        split = ann_line.split('\t')
        parsed_annotation = None
        if len(split) > 1:
            annotation_type = split[0][0]
            if annotation_type == BratEntity.ANN_TYPE_IDENTIFIER:
                try:
                    parsed_annotation = BratEntity.from_ann_line(ann_line)
                except ValueError as valueError:
                    raise valueError
            elif annotation_type == BratEvent.ANN_TYPE_IDENTIFIER:
                parsed_annotation = BratEvent.from_ann_line(ann_line)
            elif annotation_type == BratAttribute.ANN_TYPE_IDENTIFIER:
                parsed_annotation = BratAttribute.from_ann_line(ann_line)
            else:
                print(f"No Class Match for line: {ann_line}")

        return parsed_annotation


    def to_ann_line(self) -> Optional[str]:
        raise NotImplemented("to_brat_ann_line must be implemented by sub-class")
        return None

    @property
    def identifier_num(self) -> int:
        return int(self.identifier[1:]) # All identifiers a single capital letter followed by a number. Example T29

    @identifier_num.setter
    def identifier_num(self, value: int):
        self.identifier = f"{self.identifier[:1]}{value}"

    @property
    def identifier_type(self) -> str:
        return self.identifier[:1]  # All identifiers a single capital letter followed by a number Example: T29

class BratEntity(BratAnnotation):
    """Simple BratEntity class for use with BratFile.py"""

    ANN_TYPE_IDENTIFIER = 'T'

    @classmethod
    def from_ann_line(cls, ann_line: str) -> Optional['BratEntity']:

        # Split the annotation line into components
        # Sample: T1	Protein 1881 1888;1892 1901	general confusion
        split = ann_line.split('\t')
        if len(split) == 3:
            ann_type, entity_txtrange, text = ann_line.split('\t')
            tag_num = int(ann_type[1:])
            entity_type = entity_txtrange[:entity_txtrange.find(' ')]
            txtranges = entity_txtrange[entity_txtrange.find(' ') + 1:]

            txtranges = [(int(fragment_range.split(' ')[0]), int(fragment_range.split(' ')[1])) for fragment_range in
                         txtranges.split(';')]

            tag = None
            try:
                tag = BratEntity(ann_type, entity_type, txtranges, text)
                tag.original_line = ann_line
            except ValueError as valueError:
                raise valueError
            return tag

        else:
            print("Unable to process ann_line: " + ann_line)
            return None

    def to_ann_line(self) -> str:

        # Combine into Annotation Line
        # Sample: T1	Protein 1881 1888;1892 1901	general confusion
        txtranges = ';'.join([f'{span[0]} {span[1]}' for span in self.spans])
        entity_txtranges = f'{self.entity_type} {txtranges}'

        ann_line = '\t'.join([self.identifier, entity_txtranges, self.text])
        return ann_line

    def overlaps_spans(self, span: Tuple[int, int]) -> bool:
        """
        Tests if a span overlaps any span in the entity's span

        :param span: span to to test
        :return: true if there is an overlap false otherwise
        """
        for tag_span in self.spans:
            if tag_span[0] == tag_span[1] or span[0] == span[1]:
                continue
            if (tag_span[0] < span[1] and tag_span[1] > span[0]) or (tag_span[1] > span[0] and span[1] > tag_span[0]):
                return True
        return False

    def overlaps_tag(self, other_tag: 'BratEntity') -> bool:
        for other_span in other_tag.spans:
            if self.overlaps_spans(other_span):
                return True
        return False

    @deprecation.deprecated(deprecated_in="0.2", removed_in="1.0",
                            current_version="0.2",
                            details="Use self.entity_type instead.")
    @property
    def tag_type(self) -> str:
        return self.entity_type

    @property
    def applied_events(self) -> List['BratEvent']:
        applied_events: List[BratEvent] = []

        for related_annotation in self.related_annotations:
            if related_annotation.identifier_type == BratEvent.ANN_TYPE_IDENTIFIER:
                related_event: BratEvent = related_annotation
                if self.identifier == related_event.entity_identifier:
                    applied_events.append(related_event)

        return applied_events

    @property
    def applied_direct_attributes(self) -> List['BratAttribute']:
        """
        Returns list of BratAttributes applied directly to the entity
        and not indirectly through an event.

        :return: List of BratAttributes applied directly to the entity.
        """

        applied_direct_attributes: List['BratAttribute'] = []

        for related_annotation in self.related_annotations:
            related_annotation: BratAnnotation = related_annotation
            if related_annotation.identifier_type == BratAttribute.ANN_TYPE_IDENTIFIER:
                tmp_attribute: BratAttribute = related_annotation
                if tmp_attribute.ann_identifier == self.identifier:
                    applied_direct_attributes.append(tmp_attribute)

        return applied_direct_attributes


    @property
    def applied_attributes(self, consider_events: bool = True) -> List['BratAttribute']:
        """
        Gather attributes (think negation and doc time rel) applicable to the entity.
        This will also look at related events and gather those attributes as well.

        :return: list of BratAttributes applicable to the entity
        """

        # Gather Directly Related Attributes
        applied_attributes = self.applied_direct_attributes

        # Gather Related Attributes through events
        for event in self.applied_events:
            event: BratEvent = event
            for attr in event.applied_attributes:
                attr: BratAttribute = attr
                if attr.ann_identifier == event.identifier:
                    applied_attributes.append(attr)

        return applied_attributes

    def has_related_brat_attribute_of_type(self, attribute_type: str) -> bool:
        for attribute in self.applied_attributes:
            if attribute.attribute_type == attribute_type:
                return True
        return False



    def __init__(self, identifier: str, entity_type: str = "", spans: List[Tuple[int, int]] = [], text: str = ""):
        """
        Create BratEntity

        :param identifier: BRAT identifier
        :param entity_type: Tag type
        :param spans: tuple of start / end of the text
        :param text: full text of the entity.
        """

        super().__init__(identifier)
        self.entity_type = entity_type
        self.spans = spans
        self.text = text

        if '\n' in text:
            raise ValueError(f"({identifier}) Text contains a new line:\n{text}")

        len_of_spans = sum([span[-1] - span[0] + 1 for span in spans]) - 1
        if not len(text) == len_of_spans:
            raise ValueError(f"({identifier}) Text length ({len(text)}) != span length ({len_of_spans}):\n  ->{self.text}<-")
            # print(f"({identifier}) Text length ({len(text)}) != span length ({len_of_spans}):\n  {self.text}")

    def start(self) -> Optional[int]:
        if len(self.spans) > 0:
            return self.spans[0][0]
        else:
            return None

    def end(self):
        if len(self.spans) > 0:
            return self.spans[-1][-1]
        else:
            return None

    def __str__(self):
        return self.to_ann_line()
        # return f'{self.identifier} {self.entity_type} ({self.start()}, {self.end()}) "{self.text}"'

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if self is other:
            return True
        if type(self) != type(other):
            return False

        return self.entity_type == other.entity_type \
               and self.start() == other.start() \
               and self.end() == other.end() \
               and self.text == other.text

@dataclass
class BratEventArg:
    name: str
    identifer: str


class BratEvent(BratAnnotation):

    ANN_TYPE_IDENTIFIER = 'E'

    @classmethod
    def from_ann_line(cls, ann_line: str) -> Optional['BratEvent']:
        # Parse BratEvent from ann_line
        # Sample Line: E1    SUD:T3
        # Sample Line: E2	Transfer-money:T3 Giver-Arg:T6

        split = ann_line.split('\t')
        if len(split) == 2:
            identifier, event_info = split
            event_to_entity, *event_args = event_info.split(' ')

            event_num = int(identifier[1:])
            event_type, entity_identifier = event_to_entity.split(':')

            brat_event_args: List[BratEventArg] = []
            for event_arg in event_args:
                arg_name, arg_indentifer = event_arg.split(':')
                brat_event_args.append(BratEventArg(arg_name, arg_indentifer))

            return BratEvent(identifier, event_type, entity_identifier, brat_event_args)

        #else
        raise ValueError(f"Invalid Event Line: {ann_line}")
        return None


    def to_ann_line(self) -> str:
        # Sample line: E1    SUD:T3
        # Sample Line: E2	Transfer-money:T3 Giver-Arg:T6

        event_info = ':'.join([self.event_type, self.entity_identifier])
        for brat_event_arg in self.event_args:
            event_info += ' ' + ':'.join([brat_event_arg.name, brat_event_arg.identifer])

        return '\t'.join([self.identifier, event_info])

    def __init__(self, identifier: str, event_type: str, entity_identifier: str, event_args: List[BratEventArg]):
        super().__init__(identifier)

        self.event_type = event_type
        self.entity_identifier = entity_identifier
        self.event_args = event_args

    def __str__(self):
        return self.to_ann_line()

    def __repr__(self):
        return str(self)

    @property
    def applied_attributes(self):
        applied_attributes: List[BratAttribute] = []

        for annotation in self.related_annotations:
            if annotation.identifier_type == BratAttribute.ANN_TYPE_IDENTIFIER:
                attr: BratAttribute = annotation
                if attr.ann_identifier == self.identifier:
                    applied_attributes.append(attr)

        return applied_attributes

class BratAttribute(BratAnnotation):

    ANN_TYPE_IDENTIFIER = 'A'

    @classmethod
    def from_ann_line(cls, ann_line: str) -> Optional['BratAttribute']:
        # Sample Line: A2	DocTimeRel T17 Before
        # Sample Line: A2	Negation E1

        split = ann_line.split('\t')
        if len(split) == 2:
            identifier, attribute_info = split

            split = attribute_info.split(' ')
            if len(split) == 2:
                attribute_type, ann_identifier = split
                return BratAttribute(identifier, attribute_type, ann_identifier, None)
            if len(split) == 3:
                attribute_type, ann_identifier, attribute_value = split
                return BratAttribute(identifier, attribute_type, ann_identifier, attribute_value)
        else:
            return None

    def to_ann_line(self) -> str:
        # Sample Line: A2	DocTimeRel T17 Before
        # Sample Line: A2	Negation E1
        if self.value:
            return '\t'.join([self.identifier, ' '.join([self.attribute_type, self.ann_identifier, self.value])])
        else:
            return '\t'.join([self.identifier, ' '.join([self.attribute_type, self.ann_identifier])])

    def __init__(self, identifier: str, attribute_type: str, ann_identifier: str, value: Optional[str]):
        super().__init__(identifier)

        self.attribute_type = attribute_type
        self.ann_identifier = ann_identifier
        self.value = value

    def __str__(self):
        return self.to_ann_line()

    def __repr__(self):
        return str(self)
