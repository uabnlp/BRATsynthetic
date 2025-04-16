from collections import defaultdict
from typing import List, Tuple, Dict
from copy import deepcopy
import logging
import re

from bratsynthetic.bratfile import BratFile, BratEntity
from .BratSyntheticConfig import BratSyntheticConfig
from .maker import DateMaker, StreetMaker, HospitalMaker, ZipMaker
from .maker import DeviceMaker, EmailMaker, FaxMaker, HealthPlanMaker
from .maker import MedicalRecordMaker, IDNumMaker, UndeterminedMaker, BioIDMaker
from .maker import OrganizationMaker, TimeMaker, CountryMaker, LocationOtherMaker
from .maker import PatientMaker, DoctorMaker, StateMaker, AgeMaker
from .maker import PhoneMaker, CityMaker, UsernameMaker, ProfessionMaker
from .maker import URLMaker


class BratSynthetic:

    def __init__(self, config: BratSyntheticConfig, logger):
        self.simple_replacement = config.general.default_strategy == 'simple'
        self.config = config
        self.logger = logger
        self.entity_type_to_maker = {
            'AGE': AgeMaker(config),
            'BIOID': BioIDMaker(config),
            'CITY': CityMaker(config),
            'COUNTRY': CountryMaker(config),
            'DATE': DateMaker(config),
            'DEVICE': DeviceMaker(config),
            'DOCTOR': DoctorMaker(config),
            'EMAIL': EmailMaker(config),
            'FAX': FaxMaker(config),
            'HEALTHPLAN': HealthPlanMaker(config),
            'HOSPITAL': HospitalMaker(config),
            'IDNUM': IDNumMaker(config),
            'LOCATION-OTHER': LocationOtherMaker(config),
            'MEDICALRECORD': MedicalRecordMaker(config),
            'ORGANIZATION': OrganizationMaker(config),
            'PATIENT': PatientMaker(config),
            'PHONE': PhoneMaker(config),
            'PROFESSION': ProfessionMaker(config),
            'STATE': StateMaker(config),
            'STREET': StreetMaker(config),
            'TIME': TimeMaker(config),
            'UNDETERMINED': UndeterminedMaker(config),
            'URL': URLMaker(config),
            'USERNAME': UsernameMaker(config),
            'ZIP': ZipMaker(config),
        }

        # Add PHI- prefix for these tags.
        updated_tag_to_maker = {}
        for key, value in self.entity_type_to_maker.items():
            updated_tag_to_maker[key] = value
            updated_tag_to_maker[f'PHI-{key}'] = value
        self.entity_type_to_maker = updated_tag_to_maker

    def get_brat_text_from_spans(self, text: str, spans: List[Tuple[int, int]]):
        entity_text_lines = []
        for span in spans:
            entity_text_lines.append(text[span[0]:span[1]])
        entity_text = ' '.join(entity_text_lines)
        entity_text = re.sub(r'\n+', ' ', entity_text)
        return entity_text

# BratSynthetic.py

    def syntheticize(self, brat_txt_path: str) -> Tuple[str, str]:
        """
        Returns synthetic text and text for annotation file.
        """
        brat_file = BratFile.load_from_file(brat_txt_path)

        text = brat_file.text
        annotations = [deepcopy(ann) for ann in brat_file.annotations]

        PHI_TAGS = set(self.entity_type_to_maker.keys())

        # Collect entities to be replaced⟶  **only PHI**
        entities = [
            ann for ann in annotations
            if isinstance(ann, BratEntity) and ann.entity_type in PHI_TAGS
    ]

        # Create replacements for entities, using identifiers as keys
        replacements = self.create_replacement_text_for_entities(entities)

        # Map from entity identifiers to entities
        id_to_entity = {entity.identifier: entity for entity in entities}

        # Build a mapping from spans to list of entities
        span_to_entities = defaultdict(list)
        for entity in entities:
            span = (entity.start(), entity.end())
            span_to_entities[span].append(entity)

        # Get list of spans sorted in reverse order
        spans = sorted(span_to_entities.keys(), key=lambda s: s[0], reverse=True)

        # Now process spans in reverse order
        for span in spans:
            entities_in_span = span_to_entities[span]
            start, end = span

            # Build the replacement text
            # For overlapping entities with same spans, ensure unique replacements
            replacement_texts = [replacements[entity.identifier] for entity in entities_in_span if entity.identifier in replacements]

            # Combine replacement texts or pick one (here we pick the first)
            if replacement_texts:
                replacement_text = replacement_texts[0]

                # Replace text in the text string
                text = text[:start] + replacement_text + text[end:]

                # Calculate length difference
                original_length = end - start
                delta_len = len(replacement_text) - original_length

                # Adjust spans of entities in entities_in_span
                for entity in entities_in_span:
                    # Update the entity's spans
                    entity.spans = [(start, start + len(replacement_text))]
                    entity.text = replacement_text

                # Adjust spans of other annotations
                for ann in annotations:
                    if ann in entities_in_span:
                        continue
                    if hasattr(ann, 'spans'):
                        adjusted_spans = []
                        for s_start, s_end in ann.spans:
                            if s_end <= start:
                                # No adjustment needed
                                adjusted_spans.append((s_start, s_end))
                            elif s_start >= end:
                                # Shift the span
                                adjusted_spans.append((s_start + delta_len, s_end + delta_len))
                            else:
                                # Overlaps with the replaced span
                                # Need to adjust accordingly
                                if s_start < start and s_end > end:
                                    # Span wraps around the replaced entity
                                    adjusted_spans.append((s_start, s_end + delta_len))
                                elif s_start >= start and s_end <= end:
                                    # Span is within the replaced entity
                                    # Adjust to match the replacement span
                                    adjusted_spans.append((start, start + len(replacement_text)))
                                elif s_start < start < s_end <= end:
                                    # Left overlap
                                    adjusted_spans.append((s_start, start))
                                elif start <= s_start < end < s_end:
                                    # Right overlap
                                    adjusted_spans.append((start + len(replacement_text), s_end + delta_len))
                                else:
                                    # Partial overlap
                                    adjusted_spans.append((s_start + delta_len, s_end + delta_len))
                        ann.spans = adjusted_spans
                        ann.text = self.get_brat_text_from_spans(text, ann.spans)

        # Update attributes and events if they reference entities
        for ann in annotations:
            if hasattr(ann, 'referenced_annotation'):
                ref_ann = ann.referenced_annotation
                if isinstance(ref_ann, str) and ref_ann in id_to_entity:
                    ann.referenced_annotation = id_to_entity[ref_ann]
            if hasattr(ann, 'annotations'):
                # For events that reference multiple annotations
                updated_annotations = []
                for ref_ann in ann.annotations:
                    if isinstance(ref_ann, str) and ref_ann in id_to_entity:
                        updated_annotations.append(id_to_entity[ref_ann])
                    else:
                        updated_annotations.append(ref_ann)
                    ann.annotations = updated_annotations

        # Rebuild the brat file with updated annotations
        new_brat_file = BratFile(text, annotations)
        return new_brat_file.text, new_brat_file.to_brat_ann()


    def create_replacement_text_for_entities(self, entities: List[BratEntity]) -> Dict[str, str]:
        # Use entity identifiers as keys
        type_to_entities: Dict[str, List[BratEntity]] = defaultdict(list)
        for entity in entities:
            type_to_entities[entity.entity_type].append(entity)

        ret_val: Dict[str, str] = {}

        for etype in type_to_entities.keys():
            if etype not in self.entity_type_to_maker.keys():
                for entity in type_to_entities[etype]:
                    ret_val[entity.identifier] = entity.text  # use original text
            else:
                self.logger.info(f'Creating {len(type_to_entities[etype])} replacements for {etype}')
                if self.simple_replacement:
                    for entity in type_to_entities[etype]:
                        ret_val[entity.identifier] = f'[**{etype}**]'
                else:
                    value_maker = self.entity_type_to_maker[etype]
                    entities_list = type_to_entities[etype]
                    results = value_maker.make([entity.text for entity in entities_list])
                    ret_val.update(dict(zip([e.identifier for e in entities_list], results)))

        return ret_val