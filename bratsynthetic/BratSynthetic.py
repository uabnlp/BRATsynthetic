
from typing import List, Tuple
from bratsynthetic.newbrattools import BratFile, BratEntity

from .maker import DateMaker, StreetMaker, HospitalMaker, ZipMaker
from .maker import PatientMaker, DoctorMaker, StateMaker, AgeMaker
from .maker import PhoneMaker, CityMaker, UsernameMaker, ProfessionMaker
from .maker import OrganizationMaker, TimeMaker, CountryMaker, LocationOtherMaker
from .maker import MedicalRecordMaker, IDNumMaker, UndeterminedMaker, BioIDMaker
from .maker import DeviceMaker, EmailMaker, FaxMaker, HealthPlanMaker
from .maker import URLMaker

class BratSynthetic:

    def __init__(self, simple_replacement: bool = True):
        self.simple_replacement = simple_replacement

        self.entity_type_to_maker = None
        if not self.simple_replacement:
            self.entity_type_to_maker = {
                'AGE': AgeMaker(),
                'BIOID': BioIDMaker(),
                'CITY': CityMaker(),
                'COUNTRY': CountryMaker(),
                'DATE': DateMaker(),
                'DEVICE': DeviceMaker(),
                'DOCTOR': DoctorMaker(),
                'EMAIL': EmailMaker(),
                'FAX': FaxMaker(),
                'HEALTHPLAN': HealthPlanMaker(),
                'HOSPITAL': HospitalMaker(),
                'IDNUM': IDNumMaker(),
                'LOCATION-OTHER': LocationOtherMaker(),
                'MEDICALRECORD': MedicalRecordMaker(),
                'ORGANIZATION': OrganizationMaker(),
                'PATIENT': PatientMaker(),
                'PHONE': PhoneMaker(),
                'PROFESSION': ProfessionMaker(),
                'STATE': StateMaker(),
                'STREET': StreetMaker(),
                'TIME': TimeMaker(),
                'UNDETERMINED': UndeterminedMaker(),
                'URL': URLMaker(),
                'USERNAME': UsernameMaker(),
                'ZIP': ZipMaker(),
            }

            # Add PHI- prefix for these tags.
            updated_tag_to_maker = {}
            for key, value in self.entity_type_to_maker.items():
                updated_tag_to_maker[key] = value
                updated_tag_to_maker[f'PHI-{key}'] = value
            self.entity_type_to_maker = updated_tag_to_maker

    def syntheticize(self, brat_txt_path: str) -> Tuple[str, str]:
        """
        Returns syntheticize text and text for annotation file.
        """
        brat_file = BratFile.load_from_file(brat_txt_path)

        # Filter to simplest annotation entity
        entities: List[BratEntity] = [ann for ann in brat_file.entities]

        # Find overlapping tags, and only use the longest entity in each group.
        # This is because the code that updates the spans of each entity
        overlapping_entity_groups: List[List[BratEntity]] = self.find_overlapping_tags(entities)
        entities_to_remove: List[BratEntity] = []

        for entity_group in overlapping_entity_groups:
            max_len_tag = entity_group[0]
            for index, entity in enumerate(entity_group):
                if (entity.end() - entity.start()) > (max_len_tag.end() - max_len_tag.start()):
                    max_len_tag = entity

            for entity in entity_group:
                if entity != max_len_tag:
                    entities_to_remove.append(entity)

        for index, entity_to_remove in enumerate(entities_to_remove):
            entities.remove(entity_to_remove)

        new_text = brat_file.text
        replacements: List[Tuple[BratEntity, str]] = []
        for entity in entities:
            replacement_text = self.create_replacement_text_for_tag(entity)
            replacements.append((entity, replacement_text))

        #Sorted replacement from first entity in text to last entity in text
        replacements.sort(key=lambda x: x[0].end()) #First element of tuple is BratEntity

        delta_span = 0
        new_brat_annotations: List[BratEntity] = []
        for replacement in replacements:
            original_entity = replacement[0]
            current_text = original_entity.text
            replacement_text = replacement[1]

            # assert len(original_entity.spans) == 1  # No support for non-contiguous entities.
            start_span_index = original_entity.spans[0][0] + delta_span
            stop_span_index = original_entity.spans[-1][-1] + delta_span
            new_text = replacement_text.join([new_text[:start_span_index], new_text[stop_span_index:]])
            new_span = (start_span_index, start_span_index + len(replacement_text))

            new_entity: BratEntity = BratEntity(original_entity.identifier, original_entity.entity_type, [new_span], replacement_text)
            new_brat_annotations.append(new_entity)
            new_brat_annotations.extend(original_entity.applied_direct_attributes)
            new_brat_annotations.extend(original_entity.applied_events)

            delta_span += (len(replacement_text) - len(current_text))

        new_brat_annotations.reverse()

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

    def create_replacement_text_for_tag(self, entity: BratEntity) -> str:
        if self.simple_replacement:
            if entity.entity_type in self.entity_type_to_maker.keys():
                return f'[**{entity.entity_type}**]'
            else:
                return entity.text
        else:
            return self.create_fancy_replacement_text(entity)

    def create_fancy_replacement_text(self, entity: BratEntity) -> str:

        for key, value in self.entity_type_to_maker.items():
            if entity.entity_type.upper().startswith(key):
                return value.make(entity.text)
        # ELSE
        print(f'    No Maker for tag type {entity.entity_type}. Ignoring.')
        return entity.text





