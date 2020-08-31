
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
        self.date_make = DateMaker()
        self.street_make = StreetMaker()
        self.hospital_make = HospitalMaker()
        self.zip_make = ZipMaker()
        self.patient_make = PatientMaker()
        self.doctor_make = DoctorMaker()
        self.state_make = StateMaker()
        self.age_make = AgeMaker()
        self.phone_make = PhoneMaker()
        self.city_make = CityMaker()
        self.username_make = UsernameMaker()
        self.profession_maker = ProfessionMaker()
        self.organization_maker = OrganizationMaker()
        self.time_maker = TimeMaker()
        self.country_maker = CountryMaker()
        self.location_other_maker = LocationOtherMaker()
        self.medical_record_maker = MedicalRecordMaker()
        self.idnum_maker = IDNumMaker()
        self.undetermined_maker = UndeterminedMaker()
        self.bioid_maker = BioIDMaker()
        self.device_maker = DeviceMaker()
        self.email_maker = EmailMaker()
        self.fax_maker = FaxMaker()
        self.healthplan_maker = HealthPlanMaker()
        self.url_maker = URLMaker()


    def syntheticize(self, brat_txt_path: str) -> str:

        brat_file = BratFile.load_from_file(brat_txt_path)

        # Filter to simplest annotation tag
        tags: List[BratTag] = [ann for ann in brat_file.annotations if type(ann) == BratTag]

        # Find overlapping tags, and only use the preferred tag.
        overlapping_tag_groups: List[List[BratTag]] = self.find_overlapping_tags(tags)
        tags_to_remove: List[BratTag] = []

        for index, tag_to_remove in enumerate(tags_to_remove):
            tags.remove(tag_to_remove)

        new_text = brat_file.text
        replacements: List[Tuple[BratTag, str]] = []
        for tag in tags:
            replacement_text = self.create_replacement_text_for_tag(tag)
            replacements.append((tag, replacement_text))

        #Sorted replacement from highest ending spans to smallest.
        replacements.sort(key=lambda x: x[0].spans[-1], reverse=True) #First element of tuple is BratTag

        for replacement in replacements:
            replacement_tag = replacement[0]
            replacement_text = replacement[1]
            for span in replacement_tag.spans:
                new_text = replacement_text.join([new_text[:span[0]], new_text[span[1]:]])

        return new_text


    def _do_spans_overlap(self, a: Tuple[int, int], b: Tuple[int, int]) -> bool:
        if a[0] == a[1] or b[0] == b[1]: #if either empty
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
            return f'<<{tag.tag_type}>>'
        else:
            return self.create_fancy_replacement_text(tag)

    def create_fancy_replacement_text(self, tag: BratTag) -> str:
        if tag.tag_type.startswith('DATE'):
            return self.date_make.make(tag.text)
        elif tag.tag_type.startswith('HOSPITAL'):
            return self.hospital_make.make(tag.text)
        elif tag.tag_type.startswith('STREET'):
            return self.street_make.make(tag.text)
        elif tag.tag_type.startswith('ZIP'):
            return self.zip_make.make(tag.text)
        elif tag.tag_type.startswith('PATIENT'):
            return self.patient_make.make(tag.text)
        elif tag.tag_type.startswith('DOCTOR'):
            return self.doctor_make.make(tag.text)
        elif tag.tag_type.startswith('STATE'):
            return self.state_make.make(tag.text)
        elif tag.tag_type.startswith('AGE'):
            return self.age_make.make(tag.text)
        elif tag.tag_type.startswith('PHONE'):
            return self.phone_make.make(tag.text)
        elif tag.tag_type.startswith('CITY'):
            return self.city_make.make(tag.text)
        elif tag.tag_type.startswith('USERNAME'):
            return self.username_make.make(tag.text)
        elif tag.tag_type.startswith('PROFESSION'):
            return self.profession_maker.make(tag.text)
        elif tag.tag_type.startswith('ORGANIZATION'):
            return self.organization_maker.make(tag.text)
        elif tag.tag_type.startswith('TIME'):
            return self.time_maker.make(tag.text)
        elif tag.tag_type.startswith('COUNTRY'):
            return self.country_maker.make(tag.text)
        elif tag.tag_type.startswith('LOCATION-OTHER'):
            return self.location_other_maker.make(tag.text)
        elif tag.tag_type.startswith('MEDICALRECORD'):
            return self.medical_record_maker.make(tag.text)
        elif tag.tag_type.startswith('IDNUM'):
            return self.idnum_maker.make(tag.text)
        elif tag.tag_type.startswith('UNDETERMINED'):
            return self.undetermined_maker.make(tag.text)
        elif tag.tag_type.startswith('BIOID'):
            return self.bioid_maker.make(tag.text)
        elif tag.tag_type.startswith('DEVICE'):
            return self.device_maker.make(tag.text)
        elif tag.tag_type.startswith('EMAIL'):
            return self.email_maker.make(tag.text)
        elif tag.tag_type.startswith('FAX'):
            return self.fax_maker.make(tag.text)
        elif tag.tag_type.startswith('HEALTHPLAN'):
            return self.healthplan_maker.make(tag.text)
        elif tag.tag_type.startswith('URL'):
            return self.url_maker.make(tag.text)
        else:
            print(f'Unhandled tag type for replacement text: {tag.tag_type}')
            exit()
            return f'<<{tag.tag_type}>>'





