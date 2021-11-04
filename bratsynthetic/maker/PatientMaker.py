from .Maker import Maker
import yaml
import re


class PatientMaker(Maker):


    def make(self, input: str) -> str:
        with open('config.yaml') as cf_file:
            config = yaml.safe_load(cf_file.read())

        if config['show_consistent_name']:
            checker = True
            words = re.split(r'[,\s]+', input)
            if len(words) > 1:
                self.maxWords = words[1]

            self.patient_input_name = self.match_case(input, self.patient_input_name)
            if re.compile(input, re.IGNORECASE) not in self.patient_dict.keys():
                re.compile(self.patient_input_name, re.IGNORECASE)
                self.patient_dict[self.patient_input_name] = self.patient_reference_name

            # For Searching Names already in Dictionary
            for key, value in self.patient_dict.items():
                if re.compile(input, re.IGNORECASE).match(key) and key != 'None':
                    checker = False
                    if len(words) == 1 and input in list(self.patient_dict.keys())[-1]:
                        self.patient_output_name = re.split(r'[,\s]+', self.patient_dict[key])[0]
                    else:
                        self.patient_output_name = self.patient_dict[key]

            # First two cases to double check for missing elements and last three cases for using a fake name generator
            if checker:
                randomvalue = re.split(r'[,\s]+', self.patient_input_name)

                if re.search(randomvalue[0], input, re.IGNORECASE):
                    self.patient_output_name = self.patient_dict.get(self.patient_input_name)
                elif input in self.patient_dict:
                    self.patient_output_name = self.patient_dict.get(self.patient_input_name)
                elif len(self.patient_dict) > 0 and len(words) == 1 and re.search(self.maxWords, input, re.IGNORECASE):
                    value = self.patient_dict.get(list(self.patient_dict.keys())[-1])
                    value = self.match_case(input, value)

                    if len(value.split(' ')) > 1:
                        value = re.split(r'[,\s]+', self.patient_output_name)[1]
                    else:
                        value = re.split(r'[,\s]+', self.patient_output_name)[0]
                    self.patient_output_name = value
                elif re.fullmatch(r'\w+,.*', input):  # Assume [LAST], [FIRST]
                    self.patient_output_name = f'{self.fake.first_name()}, {self.fake.last_name()}'
                elif len(words) == 1:
                    self.patient_output_name = self.fake.last_name()
                else:
                    self.patient_output_name = self.fake.name()

            self.patient_input_name = input
            self.patient_output_name = self.match_case(input, self.patient_output_name)
            self.patient_reference_name = self.patient_output_name
            print(f'    PatientMaker: {input} -> {self.patient_output_name}')

            return self.patient_output_name

        else:

            words = input.split(' ')

            if re.fullmatch(r'\w+,.*', input):  # Assume [LAST], [FIRST]
                output = f'{self.fake.last_name()}, {self.fake.first_name()}'
            elif len(words) == 1:
                output = self.fake.last_name()
            else:
                output = self.fake.name()

            output = self.match_case(input, output)
            if self.show_replacements:
                print(f'    PatientMaker: {input} -> {output}')
            if output.upper() == 'UNMATCHED':
                output = self.fake.name()

            return output
