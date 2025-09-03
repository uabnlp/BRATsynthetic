from copy import deepcopy
from dataclasses import dataclass
import logging
from typing import Optional, List, Tuple

# Retrieve the global 'BratSynthetic' logger
logger = logging.getLogger('BratSynthetic')

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
                parsed_annotation = BratEntity.from_ann_line(ann_line)
            elif annotation_type == 'E':
                parsed_annotation = BratEvent.from_ann_line(ann_line)
            elif annotation_type == 'A':
                parsed_annotation = BratAttribute.from_ann_line(ann_line)
            elif annotation_type == '#':
                # ignore comments
                pass
            else:
                logger.warning(f"No Class Match for line: {ann_line}")
        return parsed_annotation

    def to_ann_line(self) -> Optional[str]:
        raise NotImplementedError()

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
    ANN_TYPE_IDENTIFIER = 'T'

    @classmethod
    def from_ann_line(cls, ann_line: str) -> Optional['BratEntity']:
        split = ann_line.split('\t')
        if len(split) == 3:
            ann_id, txtrange, text = split
            entity_type, spans_str = txtrange.split(' ', 1)
            spans = [(int(s), int(e)) for part in spans_str.split(';') for s,e in [part.split(' ')]]
            return BratEntity(ann_id, entity_type, spans, text, ann_line)
        logger.warning(f"Unable to process ann_line: {ann_line}")
        return None

    def __init__(
        self,
        identifier: str,
        entity_type: str,
        spans: List[Tuple[int, int]],
        text: str,
        original_ann_line: str = ''
    ):
        super().__init__(identifier)
        self.entity_type = entity_type
        # merge adjacent/overlapping spans
        self._spans = self.merge_adjacent_spans(spans)
        self._text = text
        self.original_line = original_ann_line

        # no newlines allowed in entity text
        if '\n' in text:
            raise ValueError(f"({identifier}) Text contains newline: {text}")

        total_len = sum(e - s for s,e in self._spans)
        if total_len != len(text):
            logger.warning(
                f"({identifier}) Text-span length mismatch: text has {len(text)} chars "
                f"but spans cover {total_len}. Annotation will be kept, "
                "and text will be re-anchored at merge time."
            )
            # do NOT raise; keep the entity object

        if not self.validate_discontinuous_spans():
            logger.warning(f"Invalid discontinuous spans in {identifier}: {self._spans}")

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str):
        if '\n' in value:
            raise ValueError(f"Text cannot contain newlines: {value}")
        self._text = value

    @property
    def spans(self) -> List[Tuple[int,int]]:
        return self._spans

    @spans.setter
    def spans(self, value: List[Tuple[int,int]]):
        clean = [(max(0,s), e) for s,e in value]
        self._spans = self.merge_adjacent_spans(clean)

    def start(self) -> int:
        # Return the start offset of the first span.
        return self._spans[0][0]

    def end(self) -> int:
        # Return the end offset of the first span.
        return self._spans[-1][1]

    def to_ann_line(self) -> str:
        spans_str = ';'.join(f"{s} {e}" for s,e in self.spans)
        return '\t'.join([self.identifier, f"{self.entity_type} {spans_str}", self.text])

    def merge_adjacent_spans(self, spans: List[Tuple[int,int]]) -> List[Tuple[int,int]]:
        if not spans:
            return []
        sorted_spans = sorted(spans, key=lambda x: x[0])
        merged = [sorted_spans[0]]
        for s,e in sorted_spans[1:]:
            ls, le = merged[-1]
            if s <= le:
                merged[-1] = (ls, max(le, e))
            else:
                merged.append((s,e))
        return merged

    def validate_discontinuous_spans(self) -> bool:
        if not self._spans:
            return False
        for i in range(len(self._spans)-1):
            _, end = self._spans[i]
            start_next, _ = self._spans[i+1]
            if end > start_next:
                logger.warning(f"Overlapping spans {self._spans[i]} and {self._spans[i+1]}")
                return False
        return True

    def overlaps_span(self, span: Tuple[int, int]) -> bool:
        for tag_span in self.spans:
            if tag_span[0] == tag_span[1] or span[0] == span[1]:
                continue
            if tag_span[0] < span[1] and tag_span[1] > span[0]:
                return True
        return False

    def spans_match_exactly(self, other: 'BratEntity') -> bool:
        a = [s for s in self.spans if s[0] != s[1]]
        b = [s for s in other.spans    if s[0] != s[1]]
        if len(a) != len(b):
            return False
        return all(x == y for x, y in zip(a, b))

    def overlaps_tag(self, other: 'BratEntity') -> bool:
        for other_span in other.spans:
            if self.spans_match_exactly(other) or self.overlaps_span(other_span):
                return True
        return False

    @property
    def applied_events(self) -> List['BratEvent']:
        return [ann for ann in self.applied_annotations
                if isinstance(ann, BratEvent) and ann.entity_identifier == self.identifier]

    @property
    def applied_attributes(self) -> List['BratAttribute']:
        return [ann for ann in self.applied_annotations if isinstance(ann, BratAttribute) and ann.ann_identifier == self.identifier]

    def copy_with_new_id(self, new_id: str) -> 'BratEntity':
        new_ent = BratEntity(new_id, self.entity_type, self.spans.copy(), self.text, self.original_line)
        return new_ent

@dataclass
class BratEventArg:
    name: str
    identifer: str

    def __deepcopy__(self, memo=None):
        return BratEventArg(self.name, self.identifer)

class BratEvent(BratAnnotation):
    ANN_TYPE_IDENTIFIER = 'E'

    @classmethod
    def from_ann_line(cls, ann_line: str) -> Optional['BratEvent']:
        parts = ann_line.split('\t')
        if len(parts) != 2:
            raise ValueError(f"Invalid Event Line: {ann_line}")
        ident, info = parts
        parts = info.split(' ')
        evt_type, trigger = parts[0].split(':')
        args = [BratEventArg(*arg.split(':')) for arg in parts[1:] if arg]
        return BratEvent(ident, evt_type, trigger, args)

    def __init__(self, identifier: str, event_type: str, entity_identifier: str, event_args: List[BratEventArg]):
        super().__init__(identifier)
        self.event_type = event_type
        self.entity_identifier = entity_identifier
        self.event_args = event_args

    def to_ann_line(self) -> str:
        info = f"{self.event_type}:{self.entity_identifier}"
        for arg in self.event_args:
            info += f" {arg.name}:{arg.identifer}"
        return '\t'.join([self.identifier, info])

    def deepcopy(self):
        copy_args = [BratEventArg(arg.name, arg.identifer) for arg in self.event_args]
        ev = BratEvent(self.identifier, self.event_type, self.entity_identifier, copy_args)
        ev.applied_annotations = deepcopy(self.applied_annotations)
        return ev

    @property
    def applied_attributes(self) -> List['BratAttribute']:
        return [ann for ann in self.applied_annotations if isinstance(ann, BratAttribute) and ann.ann_identifier == self.identifier]

    def copy_with_new_id(self, new_id: str) -> 'BratEvent':
        ev = self.deepcopy()
        ev.identifier = new_id
        return ev

class BratAttribute(BratAnnotation):
    ANN_TYPE_IDENTIFIER = 'A'

    @classmethod
    def from_ann_line(cls, ann_line: str) -> Optional['BratAttribute']:
        parts = ann_line.split('\t')
        if len(parts) != 2:
            return None
        ident, info = parts
        tokens = info.split(' ')
        if len(tokens) == 2:
            atype, target = tokens
            return BratAttribute(ident, atype, target, None)
        elif len(tokens) == 3:
            atype, target, val = tokens
            return BratAttribute(ident, atype, target, val)
        return None

    def __init__(self, identifier: str, attribute_type: str, ann_identifier: str, value: Optional[str]):
        super().__init__(identifier)
        self.attribute_type = attribute_type
        self.ann_identifier = ann_identifier
        self.value = value

    def to_ann_line(self) -> str:
        if self.value is not None:
            return '\t'.join([self.identifier, f"{self.attribute_type} {self.ann_identifier} {self.value}"])
        return '\t'.join([self.identifier, f"{self.attribute_type} {self.ann_identifier}"])

    def copy_with_new_id(self, new_id: str) -> 'BratAttribute':
        return BratAttribute(new_id, self.attribute_type, self.ann_identifier, self.value)
