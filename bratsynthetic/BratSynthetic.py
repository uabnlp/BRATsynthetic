
from typing import List, Tuple
from bratsynthetic.brattools import BratFile, BratTag

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

        self.tag_to_maker = None
        if not self.simple_replacement:
            self.tag_to_maker = {
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
            for key, value in self.tag_to_maker.items():
                updated_tag_to_maker[key] = value
                updated_tag_to_maker[f'PHI-{key}'] = value
            self.tag_to_maker = updated_tag_to_maker

    def syntheticize(self, brat_txt_path: str) -> Tuple[str, str]:
        """
        Returns syntheticize text and text for annotation file.
        """
        brat_file = BratFile.load_from_file(brat_txt_path)

        # Filter to simplest annotation tag
        tags: List[BratTag] = [ann for ann in brat_file.annotations if type(ann) == BratTag]

        # Find overlapping tags, and only use the longest tag in each group.
        overlapping_tag_groups: List[List[BratTag]] = self.find_overlapping_tags(tags)
        tags_to_remove: List[BratTag] = []

        for tag_group in overlapping_tag_groups:
            max_len_tag = tag_group[0]
            for index, tag in enumerate(tag_group):
                if (tag.end - tag.start) > (max_len_tag.end - max_len_tag.start):
                    max_len_tag = tag

            for tag in tag_group:
                if tag != max_len_tag:
                    tags_to_remove.append(tag)

        for index, tag_to_remove in enumerate(tags_to_remove):
            tags.remove(tag_to_remove)

        new_text = brat_file.text
        replacements: List[Tuple[BratTag, str]] = []
        for tag in tags:
            replacement_text = self.create_replacement_text_for_tag(tag)
            replacements.append((tag, replacement_text))

        #Sorted replacement from first tag in text to last tag in text
        replacements.sort(key=lambda x: x[0].spans[-1]) #First element of tuple is BratTag

        delta_span = 0
        new_brat_tags: List[BratTag] = []
        for replacement in replacements:
            replacement_tag = replacement[0]
            current_text = replacement_tag.text
            replacement_text = replacement[1]

            start_span_index = replacement_tag.spans[0][0] + delta_span
            stop_span_index = replacement_tag.spans[-1][-1] + delta_span
            new_text = replacement_text.join([new_text[:start_span_index], new_text[stop_span_index:]])
            new_span = (start_span_index, start_span_index + len(replacement_text))

            new_brat_tags.append(BratTag(replacement_tag.identifier, replacement_tag.tag_type, [new_span], replacement_text))

            delta_span += (len(replacement_text) - len(current_text))

        new_brat_tags.reverse()

        new_brat_file = BratFile(new_text, new_brat_tags)

        return new_brat_file.text, new_brat_file.to_brat_ann()


    def _do_spans_overlap(self, a: Tuple[int, int], b: Tuple[int, int]) -> bool:
        if a[0] == a[1] or b[0] == b[1]:    # if either empty
            return False
        else:
            return ((a[0] <= b[1] and a[1] >= b[0]) or
                    (b[0] <= a[1] <= b[1]))

    def find_overlapping_tags(self, tags: List[BratTag]) -> List[List[BratTag]]:
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

    def create_replacement_text_for_tag(self, tag:BratTag) -> str:
        if self.simple_replacement:
            if tag.tag_type in self.tag_to_maker.keys():
                return f'[**{tag.tag_type}**]'
            else:
                return tag.text
        else:
            return self.create_fancy_replacement_text(tag)

    def create_fancy_replacement_text(self, tag: BratTag) -> str:

        for key, value in self.tag_to_maker.items():
            if tag.tag_type.upper().startswith(key):
                return value.make(tag.text)
        # ELSE
        print(f'    No Maker for tag type {tag.tag_type}. Ignoring.')
        return tag.text





