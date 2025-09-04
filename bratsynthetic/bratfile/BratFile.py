from copy import deepcopy
import hashlib
import logging
import os
import re
from typing import List, Dict, Tuple, Optional

from .BratAnnotation import (
    BratAnnotation, BratEntity, BratEvent, BratAttribute
)

logger = logging.getLogger('BratSynthetic')


def normalize_text(text: str) -> str:
    """
    Normalize line endings to LF and remove trailing CR.
    """
    return text.replace('\r\n', '\n').replace('\r', '\n')


def md5_hash(text: str) -> str:
    """
    Compute MD5 of text (after normalization).
    """
    return hashlib.md5(normalize_text(text).encode('utf-8')).hexdigest()

class BratFile:
    """Representation of a BRAT standoff file: text + annotations."""

    @classmethod
    def load_from_file(cls,
                       txt_path: str,
                       ann_path: Optional[str] = None) -> 'BratFile':
        if not os.path.exists(txt_path):
            raise ValueError(f"Text file not found: {txt_path}")
        with open(txt_path, 'r', encoding='utf-8') as tf:
            raw_text = tf.read()
        text = normalize_text(raw_text)
        if ann_path is None:
            ann_path = os.path.splitext(txt_path)[0] + '.ann'
        ann_lines: List[str] = []
        if os.path.exists(ann_path):
            with open(ann_path, 'r', encoding='utf-8') as af:
                ann_lines = af.read().splitlines()
        annotations: List[BratAnnotation] = []
        for line in ann_lines:
            try:
                ann = BratAnnotation.from_ann_line(line)
                if ann:
                    ann.original_line = line
                    annotations.append(ann)
            except ValueError as e:
                logger.warning(f"Ignoring invalid line in {ann_path}: {line} ({e})")
        bf = BratFile(
            text,
            annotations,
            identifier=os.path.splitext(os.path.basename(txt_path))[0]
        )
        bf.ann_path = ann_path
        bf._text_md5 = md5_hash(text)
        return bf


    def __init__(self,
                 text: str = '',
                 annotations: List[BratAnnotation] = [],
                 identifier: Optional[str] = None):
        # text must be normalized before init
        self.text: str = text
        self.annotations: List[BratAnnotation] = annotations.copy()
        # document ID (basename without extension)
        self.identifier: Optional[str] = identifier
        self.identifier_to_annotation: Dict[str, BratAnnotation] = {}
        self.__rebuild_index()
        self.__build_relations()

    def __rebuild_index(self):
        self.identifier_to_annotation = {ann.identifier: ann for ann in self.annotations}

    def __build_relations(self):
        # clear existing relations
        for ann in self.annotations:
            ann.applied_annotations = []
        # attributes relation
        for attr in self.attributes:
            tgt = self.identifier_to_annotation.get(attr.ann_identifier)
            if tgt:
                attr.applied_annotations.append(tgt)
                tgt.applied_annotations.append(attr)
        # events relation
        for ev in self.events:
            tgt = self.identifier_to_annotation.get(ev.entity_identifier)
            if tgt:
                ev.applied_annotations.append(tgt)
                tgt.applied_annotations.append(ev)

    @property
    def entities(self) -> List[BratEntity]:
        return [a for a in self.annotations if isinstance(a, BratEntity)]

    @property
    def events(self) -> List[BratEvent]:
        return [a for a in self.annotations if isinstance(a, BratEvent)]

    @property
    def attributes(self) -> List[BratAttribute]:
        return [a for a in self.annotations if isinstance(a, BratAttribute)]

    def merge_with(self, other: 'BratFile') -> None:
        # Ensure texts match by MD5 (after normalization)
        if not hasattr(self, '_text_md5') or not hasattr(other, '_text_md5'):
            raise RuntimeError("Both files must be loaded via load_from_file for MD5 check.")
        if self._text_md5 != other._text_md5:
            raise ValueError("Cannot merge: text MD5 mismatch.")

        # Prepare for merging IDs
        next_T = max((int(e.identifier[1:]) for e in self.entities), default=0) + 1
        next_E = max((int(e.identifier[1:]) for e in self.events),   default=0) + 1
        next_A = max((int(a.identifier[1:]) for a in self.attributes), default=0) + 1

        id_map: Dict[str,str] = {}

        # Merge entities (always include, even duplicates)
        for other_ent in other.entities:
            new_id = f"T{next_T}"; next_T += 1
            cloned = other_ent.copy_with_new_id(new_id)
            # validate and log mismatches
            span_text = self.entity_text_from_spans(cloned.spans)
            if span_text != cloned.text:
                logger.warning(
                    f"Span-text mismatch for {other_ent.identifier}({cloned.identifier}): "
                    f"'{cloned.text}' vs '{span_text}' -- using anchored text"
                )
                cloned._text = span_text
            self.annotations.append(cloned)
            id_map[other_ent.identifier] = new_id

        # Merge events
        for other_ev in other.events:
            ev_clone = other_ev.deepcopy()
            # remap trigger
            if ev_clone.entity_identifier in id_map:
                ev_clone.entity_identifier = id_map[ev_clone.entity_identifier]
            # remap arguments
            for arg in ev_clone.event_args:
                if arg.identifer in id_map:
                    arg.identifer = id_map[arg.identifer]
            new_id = f"E{next_E}"; next_E += 1
            ev_clone.identifier = new_id
            self.annotations.append(ev_clone)
            id_map[other_ev.identifier] = new_id

        # Merge attributes
        for other_attr in other.attributes:
            attr_clone = deepcopy(other_attr)
            if attr_clone.ann_identifier in id_map:
                attr_clone.ann_identifier = id_map[attr_clone.ann_identifier]
            new_id = f"A{next_A}"; next_A += 1
            attr_clone.identifier = new_id
            self.annotations.append(attr_clone)
            id_map[other_attr.identifier] = new_id

        # Reindex and rebuild relations
        self.__rebuild_index()
        self.__build_relations()

    def update_identifier_nums(self) -> None:
        # 1) Sort and renumber entities by their first span start
        sorted_ents = sorted(self.entities, key=lambda e: e.spans[0][0])
        for i, ent in enumerate(sorted_ents, start=1):
            ent.identifier_num = i

        # 2) Sort and renumber events by the span start of their trigger entity
        def _event_key(ev: BratEvent):
            ent = self.identifier_to_annotation.get(ev.entity_identifier)
            return (ent.spans[0][0] if ent and ent.spans else float('inf'),
                    int(ev.identifier[1:]))
        sorted_evs = sorted(self.events, key=_event_key)
        for j, ev in enumerate(sorted_evs, start=1):
            ev.identifier_num = j

        # 3) Sort and renumber attributes by the span start of what they annotate
        def _attr_key(attr: BratAttribute):
            tgt = self.identifier_to_annotation.get(attr.ann_identifier)
            # if it's an event, use the event's trigger-entity span
            if isinstance(tgt, BratEvent):
                ent = self.identifier_to_annotation.get(tgt.entity_identifier)
                start = ent.spans[0][0] if ent and ent.spans else float('inf')
            elif isinstance(tgt, BratEntity):
                start = tgt.spans[0][0] if tgt.spans else float('inf')
            else:
                start = float('inf')
            return (start, int(attr.identifier[1:]))
        sorted_attrs = sorted(self.attributes, key=_attr_key)
        for k, attr in enumerate(sorted_attrs, start=1):
            attr.identifier_num = k

        # 4) Rebuild the single annotation list
        self.annotations = []
        self.annotations.extend(sorted_ents)
        self.annotations.extend(sorted_evs)
        self.annotations.extend(sorted_attrs)

        # 5) Rebuild the index so merges & lookups continue to work
        self.__rebuild_index()


    def entity_text_from_spans(self, spans: List[Tuple[int,int]]) -> str:
        parts = [self.text[s:e] for s,e in spans]
        joined = ' '.join(parts)
        # collapse newlines within joined parts
        return re.sub(r'\n+', ' ', joined)

    def to_brat_ann(self) -> str:
        # Validate and log any remaining mismatches
        valid: List[BratAnnotation] = []
        for ann in self.annotations:
            if isinstance(ann, BratEntity):
                txt = self.entity_text_from_spans(ann.spans)
                if ann.text != txt:
                    logger.warning(f"Final span-text mismatch for {ann.identifier}: '{ann.text}' vs '{txt}'")
                    ann._text = txt
            valid.append(ann)
        return '\n'.join(a.to_ann_line() for a in valid)

    def write_to_dir(self, directory: str) -> None:
        os.makedirs(directory, exist_ok=True)
        # write text
        with open(os.path.join(directory, f"{self.identifier}.txt"), 'w', encoding='utf-8', newline='\n') as tf:
            tf.write(self.text)
        # write annotations
        with open(os.path.join(directory, f"{self.identifier}.ann"), 'w', encoding='utf-8', newline='\n') as af:
            af.write(self.to_brat_ann())

    def find_line_num_for_text_index(self, idx: int) -> int:
        assert 0 <= idx <= len(self.text)
        return self.text[:idx].count("\n")
