from collections import defaultdict
from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict
import re
import warnings
import deprecation
from copy import copy, deepcopy

class BratAnnotation(object):

    def __hash__(self):
        return hash(self.to_ann_line())

    def __init__(self, identifier: str):
        self.identifier = identifier
        self.original_line: Optional[str] = None
        self.applied_annotations: List[BratAnnotation] = []

    @classmethod
    def from_ann_line(cls, ann_line: str) -> 'BratAnnotation':
        split = ann_line.split('\t')
        parsed_annotation = None
        if len(split) > 1:
            annotation_type = split[0][0]
            if annotation_type == 'T':
                try:
                    parsed_annotation = BratEntity.from_ann_line(ann_line)
                except ValueError as valueError:
                    raise valueError
            elif annotation_type == 'E':
                parsed_annotation = BratEvent.from_ann_line(ann_line)
            elif annotation_type == 'A':
                parsed_annotation = BratAttribute.from_ann_line(ann_line)
            elif annotation_type == '#':
                pass #Ignoring comments
            else:
                print(f"No Class Match for line: {ann_line}")

        return parsed_annotation


    def to_ann_line(self) -> Optional[str]:
        raise NotImplemented("to_brat_ann_line must be implemented by sub-class")
        return None

    @property
    def identifier_num(self) -> int:
        return int(self.identifier[1:])

    @identifier_num.setter
    def identifier_num(self, value: int):
        self.identifier = f"{self.identifier[:1]}{value}"

    @property
    def identifier_type(self) -> str:
        return self.identifier[:1]

class BratEntity(BratAnnotation):
    """Simple BratEntity class for use with BratFile.py"""

    ANN_TYPE_IDENTIFIER = 'T'

    __hash__ = BratAnnotation.__hash__

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
                tag = BratEntity(ann_type, entity_type, txtranges, text, ann_line)
            except ValueError as valueError:
                raise valueError
            return tag

        else:
            print("Unable to process ann_line: " + ann_line)
            return None

    @property
    def identifier_num(self) -> int:
        return int(self.identifier[1:])

    @identifier_num.setter
    def identifier_num(self, value: int):
        new_identifier = f"{self.identifier[:1]}{value}"
        for attr in self.applied_attributes:
            attr.ann_identifier = new_identifier
        for event in self.applied_events:
            event.entity_identifier = new_identifier
        self.identifier = new_identifier

    def to_ann_line(self) -> str:

        # Combine into Annotation Line
        # Sample: T1	Protein 1881 1888;1892 1901	general confusion
        txtranges = ';'.join([f'{span[0]} {span[1]}' for span in self.spans])
        entity_txtranges = f'{self.entity_type} {txtranges}'

        ann_line = '\t'.join([self.identifier, entity_txtranges, self.text])
        return ann_line


    def overlaps_span(self, span: Tuple[int, int]) -> bool:
        """
        Tests if a span overlaps any span in the tag's span

        :param span: span to to test
        :return: true if there is an overlap false otherwise
        """
        for tag_span in self.spans:
            if tag_span[0] == tag_span[1] or span[0] == span[1]: #empty span
                continue
            if (tag_span[0] < span[1] and tag_span[1] > span[0]) or (tag_span[1] > span[0] and span[1] > tag_span[0]):
                return True
        return False

    def spans_match_exactly(self, other_entity: 'BratEntity') -> bool:
        #Filter empty spans
        spans = [span for span in self.spans if span[0] != span[1]]
        ospans = [span for span in other_entity.spans if span[0] != span[1]]

        if len(spans) != len(ospans):
            return False

        for i in range(len(spans)):
            if spans[i][0] != ospans[i][0] or spans[i][1] != spans[i][1]:
                return False
        return True

    def overlaps_tag(self, other_entity: 'BratEntity') -> bool:
        for other_span in other_entity.spans:
            if self.spans_match_exactly(other_entity) or self.overlaps_span(other_span):
                return True
        return False

    @deprecation.deprecated(deprecated_in="0.3", removed_in="1.0",
                            current_version="0.3",
                            details="tag_type property has been deprecated use self.entity_type instead.")
    def wrapped_tag_type(self) -> str:
        """
        Deprecation only work with function not properties so adding this so warning appears.
        @return: entity
        """
        return self.entity_type

    @property
    def tag_type(self) -> str:
        warnings.warn(
            "tag_type is deprecated, use entity_type instead",
            DeprecationWarning
        )
        ### Keeping this in here since we don't use the -Wd when running scripts.
        print("!!!!!tag_type is deprecated, use entity_type instead!!!!")

        # Have to call a method for the deprecation to work.
        return self.wrapped_tag_type()

    @property
    def applied_events(self) -> List['BratEvent']:
        if len([ann for ann in self.applied_annotations if ann.identifier_type == BratEvent.ANN_TYPE_IDENTIFIER]) != len([ann for ann in self.applied_annotations if ann.identifier_type == BratEvent.ANN_TYPE_IDENTIFIER and ann.entity_identifier == self.identifier]):
            print('ahhh....')

        return [ann for ann in self.applied_annotations if ann.identifier_type == BratEvent.ANN_TYPE_IDENTIFIER and ann.entity_identifier == self.identifier]

    def apply_event(self, event: 'BratEvent'):
        event: BratEvent = event.deepcopy()
        event.entity_identifier = self.identifier
        self.applied_annotations.append(event)

    @property
    def applied_attributes(self) -> List['BratAttribute']:
        if len([ann for ann in self.applied_annotations if ann.identifier_type == BratAttribute.ANN_TYPE_IDENTIFIER]) != len([ann for ann in self.applied_annotations if ann.identifier_type == BratAttribute.ANN_TYPE_IDENTIFIER and ann.ann_identifier == self.identifier]):
            print("hmmmm....")
        return [ann for ann in self.applied_annotations if ann.identifier_type == BratAttribute.ANN_TYPE_IDENTIFIER]

    @property
    def related_attributes_on_events(self) -> Dict['BratEvent', List['BratAttribute']]:
        event_to_attributes = defaultdict(list)
        for event in self.applied_events:
            event_to_attributes[event].append(event.applied_attributes)

        return event_to_attributes

    @property
    def applied_attributes_with_events(self) -> List['BratAttribute']:
        applied_attributes: List[BratAttribute] = []

        # Gather Directly Related Attributes
        for related_annotation in self.applied_annotations:
            related_annotation: BratAnnotation = related_annotation
            if related_annotation.identifier_type == BratAttribute.ANN_TYPE_IDENTIFIER:
                tmp_attribute: BratAttribute = related_annotation
                if tmp_attribute.ann_identifier == self.identifier:
                    applied_attributes.append(tmp_attribute)

        # Gather Related Attributes though events
        for event in self.applied_events:
            event: BratEvent = event
            for attr in event.applied_attributes:
                attr: BratAttribute = attr
                if attr.ann_identifier == event.identifier:
                    applied_attributes.append(attr)

        return applied_attributes

    def apply_attribute(self, attribute: 'BratAttribute'):
        attribute_copy = attribute.__deepcopy__()
        attribute_copy.ann_identifier = self.identifier
        self.applied_annotations.append(attribute_copy)

    def applied_events_by_type(self) -> Dict[str, List['BratEvent']]:
        events_by_type = defaultdict(list)
        for event in self.applied_events:
            events_by_type[event.event_type].append(event)
        return events_by_type

    def has_applied_attribute_of_type(self, attribute_type: str) -> bool:
        for attribute in self.applied_attributes:
            if attribute.attribute_type == attribute_type:
                return True
        return False

    def apply_annotation(self, annotation:BratAnnotation):
        if annotation.identifier_type == BratEvent.ANN_TYPE_IDENTIFIER:
            self.apply_event(annotation)
        elif annotation.identifier_type == BratAttribute.ANN_TYPE_IDENTIFIER:
            self.apply_attribute(annotation)
        else:
            print("!!!Unhandled Annotation Type (BratEntity.add_related_annotation): " + annotation.to_ann_line())

    def apply_annotations(self, annotations: List[BratAnnotation]):
        for ann in annotations:
            self.apply_annotation(ann)


    def __init__(self, identifier: str, entity_type: str = "", spans: List[Tuple[int, int]] = [], text: str = "", original_ann_line: str = ''):
        """
        Create BratEntity

        :param identifier: BRAT identifier
        :param entity_type: Tag type
        :param spans: tuple of start / end of the text
        :param text: full text of the tag.
        """

        super().__init__(identifier)
        self.entity_type = entity_type
        self._spans = spans
        self._text = text
        self.original_line = original_ann_line

        if '\n' in text:
            raise ValueError(f"({identifier}) Text contains a new line:\n{text}")

        len_of_spans = sum([span[-1] - span[0] + 1 for span in spans]) - 1
        if not len(text) == len_of_spans:
            raise ValueError(f"({identifier}) Text length ({len(text)}) != span length ({len_of_spans}):\n  ->{self.text}<-")
            # print(f"({identifier}) Text length ({len(text)}) != span length ({len_of_spans}):\n  {self.text}")

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value:str):
        self._text = value

    @property
    def spans(self):
        return self._spans

    @spans.setter
    def spans(self, value):
        new_spans: List[Tuple[int, int]] = []
        for span in value:
            new_start = max(0, span[0])
            new_end = span[1]
            new_span = (new_start, new_end)
            new_spans.append(new_span)

        self._spans = new_spans


    def start(self) -> Optional[int]:
        if len(self.spans) > 0:
            return self.spans[0][0]
        else:
            return None

    def end(self):
        if len(self.spans) > 0:
            return self.spans[-1][1]
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

    def __copy__(self):
        return BratEventArg(self.name, self.identifer)

    def __deepcopy__(self, memodict={}):
        return self.copy()


class BratEvent(BratAnnotation):

    ANN_TYPE_IDENTIFIER = 'E'

    __hash__ = BratAnnotation.__hash__

    def copy(self):
        copy = BratEvent(self.identifier, self.event_type, self.entity_identifier, self.event_args)
        return copy

    def deepcopy(self, memodict={}):
        copy = BratEvent(self.identifier, self.event_type, self.entity_identifier, deepcopy(self.event_args))
        copy.applied_annotations = deepcopy(self.applied_attributes)
        return copy

    __copy__ = copy
    __deepcopy__ = deepcopy

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
            for event_arg in filter(lambda x: len(x) > 0, event_args): #Events with no arguments still end in a space
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

        for annotation in self.applied_annotations:
            if annotation.identifier_type == BratAttribute.ANN_TYPE_IDENTIFIER:
                attr: BratAttribute = annotation
                if attr.ann_identifier == self.identifier:
                    applied_attributes.append(attr)

        return applied_attributes

class BratAttribute(BratAnnotation):

    ANN_TYPE_IDENTIFIER = 'A'

    __hash__ = BratAnnotation.__hash__

    def copy(self):
        return BratAttribute(self.identifier, self.attribute_type, self.ann_identifier, self.value)

    def deepcopy(self, memodict={}):
        return self.copy()

    __copy__ = copy
    __deepcopy__ = deepcopy

    @classmethod
    def from_ann_line(cls, ann_line: str) -> Optional['BratAttribute']:
        # Sample Line: A1	DocTimeRel T17 Before
        # Sample Line: A2	Negation E1
        # Sample Line: A3	Negation T6

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
