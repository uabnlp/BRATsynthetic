
from .Maker import Maker

import random

_hospital_list = [
'Andalusia Health',
'Athens-Limestone Hospital',
'Atmore Community Hospital',
'Baptist Medical Center',
'BayPointe Hospital',
'Beacon Behavioral Hospital',
'Bibb Medical Center',
'Brookwood Baptist Medical Center',
'Bryce Hospital',
'Bullock County Hospital',
'Central AL Veterans Health Care System',
'Children’s of Alabama',
'Choctaw General Hospital',
'Citizens Baptist Medical Center',
'Clay County Hospital',
'Community Hospital',
'Coosa Valley Medical Center',
'Crenshaw Community Hospital',
'Crestwood Medical Center',
'Cullman Regional Medical Center',
'D. W. McMillan Memorial Hospital',
'Dale Medical Center',
'DCH Regional Medical Center',
'Decatur Morgan Hospital',
'DeKalb Regional Medical Center',
'East Alabama Medical Center',
'EastPointe Hospital',
'Elmore Community Hospital',
'Lakeshore Rehabilitation Hospital',
'Evergreen Medical Center',
'Fayette Medical Center',
'Flowers Hospital',
'Floyd Cherokee Medical Center',
'Gadsden Regional Medical Center',
'Grandview Medical Center',
'Greene County Hospital',
'Grove Hill Memorial Hospital',
'Hale County Hospital',
'Helen Keller Hospital',
'Highlands Medical Center',
'Hill Crest Behaviorial Health Services',
'Hill Hospital',
'Huntsville Hospital',
'Jack Hughston Memorial Hospital',
'Jackson Hospital',
'Jackson Medical Center',
'John Paul Jones Hospital',
'Lake Martin Community Hospital',
'Lakeland Community Hospital',
'Laurel Oaks Behavioral Health Center',
'Lawrence Medical Center',
'Madison Hospital',
'Marshall Medical Center North',
'Marshall Medical Center South',
'Mary Starke Harper Geriatric Psychiatry Center',
'Medical Center Barbour',
'Medical Center Enterprise',
'Medical West',
'Mizell Memorial Hospital',
'Mobile Infirmary Medical Center',
'Monroe County Hospital',
'Mountain View Hospital',
'Noland Hospital',
'North Alabama Medical Center',
'North Alabama Specialty Hospital',
'North Baldwin Infirmary',
'North Mississippi Medical Center',
'Northeast Alabama Regional Medical Center',
'Northport Medical Center',
'Northwest Medical Center',
'Prattville Baptist Hospital',
'Princeton Baptist Medical Center',
'Providence Hospital',
'Red Bay Hospital',
'Regional Medical Center of Central Alabama',
'Regional Rehabilitation Hospital',
'Riverview Regional Medical Center',
'RMC Stringfellow Memorial Hospital',
'Russell Medical',
'Russellville Hospital',
'Select Specialty Hospital',
'Shelby Baptist Medical Center',
'Shoals Hospital',
'South Baldwin Regional Medical Center',
'Southeast Health',
'Springhill Medical Center',
'St. Vincent’s',
'Tanner Medical Center',
'Taylor Hardin Secure Medical Facility',
'The Sanctuary At The Woodlands',
'Thomas Hospital',
'Thomasville Regional Medical Center',
'Troy Regional Medical Center',
'UAB Hospital',
'Unity Psychiatric Care',
'USA Health University Hospital',
'Vaughan Regional Medical Center',
'Veterans Affairs Medical Ctr.',
'Walker Baptist Medical Center',
'Washington County Hospital',
'Whitfield Regional Hospital',
'Wiregrass Medical Center'
]

def _create_acronyms():
    outputs = []
    for item in _hospital_list:
        words = item.split(' ')
        acronym = ''

        if len(words[0]) > 2 and words[0].isupper():
            acronym = words[0]
        else:
            for index, word in enumerate(words):
                if index == 0 and len(word) > 2 and word[-1] == '.':
                    acronym = acronym + word + ' '
                elif word[0].isupper():
                    acronym = acronym + word[0]
        outputs.append(acronym)
    return outputs

_hospital_acronyms = _create_acronyms()

_hospitals_short = [
'Andalusia',
'Athens',
'Atmore',
'Baptist',
'BayPointe',
'Beacon',
'Bibb',
'Brookwood',
'Bryce',
'Bullock',
'Central',
'Childrens',
'Choctaw',
'Citizens',
'Clay',
'Community',
'Coosa',
'Crenshaw',
'Crestwood',
'Cullman',
'McMillan',
'Dale',
'DCH',
'Decatur',
'DeKalb',
'East',
'EastPointe',
'Elmore',
'Lakeshore',
'Evergreen',
'Fayette',
'Flowers',
'Floyd',
'Gadsden',
'Grandview',
'Greene',
'Grove',
'Hale',
'Helen',
'Highlands',
'Hill',
'Hill',
'Huntsville',
'Jack',
'Jackson',
'Jackson',
'John',
'Lake',
'Lakeland',
'Laurel',
'Lawrence',
'Madison',
'Marshall',
'Marshall',
'Mary Starke',
'Barbour',
'Enterprise',
'Medical West',
'Mizell',
'Mobile',
'Monroe',
'Mountain',
'Noland',
'North Alabama',
'North Baldwin',
'Northeast Alabama',
'Northport',
'Northwest',
'Prattville',
'Princeton',
'Providence',
'Red Bay',
'Regional',
'Riverview',
'RMC',
'Russell',
'Russellville',
'Select',
'Shelby',
'Shoals',
'South Baldwin',
'Southeast',
'Springhill',
'Vincents',
'Tanner',
'Taylor',
'Woodlands',
'Thomas',
'Thomasville',
'Troy',
'UAB',
'Unity',
'USA Childrens',
'USA',
'Vaughan',
'Veterans',
'Walker',
'Washington',
'Whitfield',
'Wiregrass',
]

class HospitalMaker(Maker):

    #Assume full name if any of these in the Hospital name
    full_name_keyword = set([keyword.upper() for keyword in ['Hospital', 'Clinic', 'Center', 'Infirmary', 'System']])

    def is_acronym(self, input):
        if len(input) < 5:
            return True
        else:
            return False

    def is_short(self, input):
        words = input.split(' ')
        full_name_keywords = ['Hospital', 'Clinic', 'Center', 'Infirmary', 'System']

        if len(set([word.upper() for word in words]).intersection(self.full_name_keyword)) > 1 or len(words) < 3:
            return True
        else:
            return False

    def make(self, input: str) -> str:
        output = 'UNMATCHED'

        if self.is_acronym(input):
            output = random.choice(_hospital_acronyms)
        elif self.is_short(input):
            output = random.choice(_hospitals_short)
        else:
            output = random.choice(_hospital_list)
        output = self.match_case(input, output)
        if self.show_replacements:
            print(f"HospitalMaker: {input} -> {output}")
        if output.upper() == 'UNMATCHED':
            output = self.match_case(random.choice(_hospital_list))

        return output

