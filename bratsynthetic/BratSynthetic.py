from collections import defaultdict
from typing import List, Tuple, Dict
from copy import deepcopy, copy
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

    def __init__(self, config: BratSyntheticConfig):
        self.simple_replacement = True if config.general.default_strategy == 'simple' else False
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

    def get_brat_text_from_spans(self, text:str, spans: List[Tuple[int, int]]):
        entity_text_lines = []
        for span in spans:
            entity_text_lines.append(text[span[0]:span[1]])
        entity_text = ' '.join(entity_text_lines)
        entity_text = re.sub(r'\n+', ' ', entity_text)
        return entity_text

    def syntheticize(self, brat_txt_path: str) -> Tuple[str, str]:
        """
        Returns synthetic text and text for annotation file.
        """
        brat_file = BratFile.load_from_file(brat_txt_path)

        new_text = brat_file.text
        new_annotations = [deepcopy(ann) for ann in brat_file.annotations]
        replacements: Dict[BratEntity, str] = self.create_replacement_text_for_entities(new_annotations)

        new_brat_annotations: List[BratEntity] = []
        offset = 0
        for index, annotation in enumerate(new_annotations):
            if annotation not in replacements or annotation.text == ",":
                if annotation.text == ",":
                    print(f'Skipping comma: {annotation}')
                new_brat_annotations.append(annotation)
                continue
            # else annotation in replacements
            assert type(annotation) == BratEntity
            current_entity: BratEntity = annotation
            replacement_text = replacements[current_entity]
            original_text = current_entity.text

            new_text = new_text[:current_entity.start() + offset] + replacement_text + new_text[current_entity.end() + offset:]
            current_entity.spans = [(current_entity.start() + offset, current_entity.start() + offset + len(replacement_text))]
            current_entity.text = self.get_brat_text_from_spans(new_text, current_entity.spans)
            print(f'{brat_file.identifier_to_annotation[current_entity.identifier]} -> {current_entity}')
            new_brat_annotations.append(current_entity)

            offset += len(replacement_text) - len(original_text)

        new_brat_file = BratFile(new_text, new_brat_annotations)

        return new_brat_file.text, new_brat_file.to_brat_ann()

    def _do_spans_overlap(self, a: Tuple[int, int], b: Tuple[int, int]) -> bool:
        if a[0] == a[1] or b[0] == b[1]:    # if either empty
            return False
        else:
            return ((a[0] <= b[1] and a[1] >= b[0]) or
                    (b[0] <= a[1] <= b[1]))

    def find_overlapping_tags(self, tags: List[BratEntity]) -> List[List[BratEntity]]:
        all_spans: List[Tuple[int, int]] = []

        for tag in tags:
            for span in tag.spans:
                if span not in all_spans:
                    all_spans.append(span)

        all_spans.sort(key=lambda span: span[1])
        tags.sort(key=lambda tag: tag.spans[-1][1])
        overlapping_tags = []
        for index, span in enumerate(all_spans):
            # if index % 100 == 0:
            #     print(f"Checking span: {index}/{len(all_spans)}")
            overlapping_tags_for_span = []
            for tag in tags:
                # This improves performance immensely
                if tag.spans[0][1] > span[1]:
                    break
                if tag.spans[-1][0] < span[0]:
                    continue
                for tag_span in tag.spans:
                    if self._do_spans_overlap(span, tag_span):
                        overlapping_tags_for_span.append(tag)

            if len(overlapping_tags_for_span) > 0:
                overlapping_tags.append(overlapping_tags_for_span)

        return overlapping_tags

    def create_replacement_text_for_entities(self, entities: List[BratEntity]) -> Dict[BratEntity, str]:

        # Divide Entities by Type so the value makers will have a list
        type_to_entities: Dict[str, List[str]] = defaultdict(lambda: [])
        for entity in entities:
            type_to_entities[entity.entity_type].append(entity)

        ret_val: Dict[BratEntity, str] = {}

        for etype in type_to_entities.keys():
            if etype not in self.entity_type_to_maker.keys():
                for entity in type_to_entities[etype]:
                    ret_val[entity] = entity.text #use original text
            else:
                print(f'Creating {len(type_to_entities[etype])} replacements for {etype}')
                if self.simple_replacement:
                    for entity in type_to_entities[etype]:
                        ret_val[entity] = f'[**{etype}**]'
                else:
                    value_maker = self.entity_type_to_maker[etype]
                    entities = type_to_entities[etype]
                    results = value_maker.make([entity.text for entity in entities])
                    ret_val.update(dict(zip(entities, results)))

        return ret_val
