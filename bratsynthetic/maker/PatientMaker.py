import random
import re
import sys
from typing import Union, List, Dict

import yaml
from faker import Faker

from bratsynthetic.maker import Maker

SEED = random.randint(~sys.maxsize, sys.maxsize)
Faker.seed(SEED)
random.seed = SEED


class PatientMaker(Maker):



    def make_random(self, input_list: List[str]) -> List[str]:
        ret_val: List[str] = []
        for input in input_list:
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

            ret_val.append(output)
        return ret_val

    def make_consistent_name(self, input_list: List[str]) -> List[str]:
        return self.make_markov(self, input_list, -1.0)

    def make_markov(self, input_list: List[str], transistion_probablity: float = 0.5) -> List[str]:
        ret_list: List[str] = []

        first_name_replacements: Dict[str, str] = {}
        last_name_replacements: Dict[str, str] = {}

        for original_input in input_list:

            do_transistion = random.uniform(0, 1) >= transistion_probablity

            input = original_input.strip().upper()
            words = re.split(r'[,\s]+', input)
            first_name = None
            last_name = None
            if len(words) == 0:
                pass
            elif len(words) == 1:
                # Assume last name only
                last_name = words[0]
            elif ',' in input:
                # Assume LASTNAME, FIRSTNAME
                last_name = words[0]
                first_name = words[1]
            else:
                # Assume FIRSTNAME LASTNAME
                first_name = words[0]
                last_name = words[1]

            replacement_first_name = None
            replacement_last_name = None
            if last_name is not None:
                if last_name in last_name_replacements.keys() and not do_transistion:
                    replacement_last_name = last_name_replacements[last_name]
                else:
                    replacement_last_name = self.fake.last_name()
                    last_name_replacements[last_name] = replacement_last_name

            if first_name is not None:
                if first_name in first_name_replacements.keys() and not do_transistion:
                    replacement_first_name = first_name_replacements[first_name]
                else:
                    replacement_first_name = self.fake.first_name()
                    first_name_replacements[first_name] = replacement_first_name


            replacement_name = "UNMATCHED"
            if replacement_first_name is not None and replacement_last_name is not None:
                if ',' in input:
                    replacement_name = f"{replacement_last_name}, {replacement_first_name}"
                else:
                    replacement_name = f"{replacement_first_name} {replacement_last_name}"
            elif replacement_last_name is not None:
                replacement_name = replacement_last_name
            elif replacement_first_name is not None:
                replacement_name = replacement_first_name

            output = self.match_case(input, replacement_name)
            if self.config.general.show_replacements:
                print(f"{self.__class__.__name__} - : {input} -> {output}")
            if output.upper() == 'UNMATCHED':
                output = self.match_case(self.fake.name())

            ret_list.append(output)

        return ret_list

        #
        #
        # for input in input_list:
        #     checker = True
        #     words = re.split(r'[,\s]+', input)
        #     if len(words) > 1:
        #         self.maxWords = words[1]
        #
        #     self.patient_input_name = self.match_case(input, self.patient_input_name)
        #     if re.compile(input, re.IGNORECASE) not in self.patient_dict.keys():
        #         self.patient_dict[self.patient_input_name] = self.patient_reference_name
        #
        #     # For Searching Names already in Dictionary
        #     for key, value in self.patient_dict.items():
        #         if re.compile(input, re.IGNORECASE).match(key) and key != 'None':
        #             checker = False
        #             if len(words) == 1 and input in list(self.patient_dict.keys())[-1]:
        #                 self.patient_output_name = re.split(r'[,\s]+', self.patient_dict[key])[0]
        #             else:
        #                 self.patient_output_name = self.patient_dict[key]
        #
        #     # First two cases to double check for missing elements and last three cases for using a fake name generator
        #     if checker:
        #         randomvalue = re.split(r'[,\s]+', self.patient_input_name)
        #
        #         if re.search(randomvalue[0], input, re.IGNORECASE):
        #             self.patient_output_name = self.patient_dict.get(self.patient_input_name)
        #         elif input in self.patient_dict:
        #             self.patient_output_name = self.patient_dict.get(self.patient_input_name)
        #         elif len(self.patient_dict) > 0 and len(words) == 1 and re.search(self.maxWords, input, re.IGNORECASE):
        #             value = self.patient_dict.get(list(self.patient_dict.keys())[-1])
        #             value = self.match_case(input, value)
        #
        #             if len(value.split(' ')) > 1:
        #                 value = re.split(r'[,\s]+', self.patient_output_name)[1]
        #             else:
        #                 value = re.split(r'[,\s]+', self.patient_output_name)[0]
        #             self.patient_output_name = value
        #         elif re.fullmatch(r'\w+,.*', input):  # Assume [LAST], [FIRST]
        #             self.patient_output_name = f'{self.fake.first_name()}, {self.fake.last_name()}'
        #         elif len(words) == 1:
        #             self.patient_output_name = self.fake.last_name()
        #         else:
        #             self.patient_output_name = self.fake.name()
        #
        #     self.patient_input_name = input
        #     self.patient_output_name = self.match_case(input, self.patient_output_name)
        #     self.patient_reference_name = self.patient_output_name
        #     print(f'    PatientMaker: {input} -> {self.patient_output_name}')
        #     ret_list.append(self.patient_output_name)

    def make_one(self, input: Union[str, List[str]]) -> Union[str, List[str]]:
        with open('config.yaml') as cf_file:
            config = yaml.safe_load(cf_file.read())

        #covert to str
        return_str_list = True
        if isinstance(input, str):
            input = [input]
            return_str_list = False

        if len(input) == 0:
            return [] #empty list

        ret_val: List[str] = []
        if config['show_consistent_name']:
            ret_val = self.make_consistent_name(input)
        elif config['use_markov_name']:
            markov_switch_percentage = 0.5
            if config['markov_switch_percentage']:
                markov_switch_percentage = float(config['markov_switch_percentage'])
            ret_val = self.make_markov(input, markov_switch_percentage)
        else:
            ret_val = self.make_random(input)

        if return_str_list:
            return ret_val
        else:
            return ret_val[0]


if __name__ == '__main__':

    input_list_len = 10
    switch_indices: List[int] = [0]
    switch_percentage = 1.0
    i = 1
    while i < input_list_len:
        if random.uniform(0, 1) < switch_percentage:
            switch_indices.append(i)
        i = i + 1
    switch_indices.append(input_list_len)

    print(switch_indices)



