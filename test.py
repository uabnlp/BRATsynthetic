"""
This is unit testing to make sure that functions are working.

It can be run from the command line:
$ python test.py
"""

import logging
import random
from typing import List
import unittest

from bratsynthetic import BratSynthetic
from bratsynthetic.bratfile import BratFile

# Load this test clinical note which is used for multiple test cases
bf_diabetes_note = BratFile.load_from_file("bratsynthetic/test_data/diabetes_note.txt")

# Required for BratSynthetic class
logger = logging.getLogger('BratSynthetic')

class GeneralSettingForTesting:
    """This is a GeneralSetting class instance created just for testing purposes."""
    errors: List[str] = []

    # Default Settings
    input_dir = None
    output_dir = None
    recursive = False
    show_replacements = True
    default_strategy = "simple"
    default_transition_probability = 0.5
    seed = random.randint(0, 2**32 - 1)  #Afraid of negative seeds...
    suppress_phi_notice = False


class BratSyntheticConfigForTesting:
    """This is BratSyntheticConfig class instance for testing purposes."""
    general = GeneralSettingForTesting()


class TestSynthecizeSimple(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        bsyn = BratSynthetic(BratSyntheticConfigForTesting(), logger)
        self.bf_synth = bsyn.syntheticize_brat_file(bf_diabetes_note)

        # print("\n" + self.bf_synth.text)

    def test_ensure_that_text_files_changed(self):
        """Make sure that there has been some kind of change to the text of the clinical notes."""
        assert self.bf_synth.text != bf_diabetes_note.text

    def test_ensure_that_phi_phrases_not_in_final_text(self):
        """Make sure that select PHI related phrases do not appear in the final text."""
        for phrase in (
            "1985",      # partial DATE
            "000123456", # MEDICALRECORD
            "Gretel",    # PATIENT
            "Hansel",    # PATIENT
            "Sweettooth", # PATIENT
            "gingerbread cottage", # LOCATION-OTHER
            "Candy Forest", # LOCATION-OTHER
        ):
            assert phrase not in self.bf_synth.text, f"The PHI phrase '{phrase}' should not be in the synthecized text."

    def test_ensure_non_phi_notes_have_the_same_text(self):
        """Test that the non PHI annotations have not been alterred by the synthetic surrogate substitution."""
        orig_non_phi_anno_dict = {anno.identifier:anno for anno in bf_diabetes_note.annotations if not anno.entity_type.isupper()}
        synth_non_phi_anno = [anno for anno in self.bf_synth.annotations if not anno.entity_type.isupper()]

        for new_anno in synth_non_phi_anno:
            # This anchors the based on the BratEntity identifer
            orig_anno = orig_non_phi_anno_dict[new_anno.identifier]

            # print(f"{orig_anno.entity_type}, {new_anno.entity_type}")
            # Did the entity type remain the same
            assert orig_anno.entity_type == new_anno.entity_type, \
                f"Entity type mismatch '{orig_anno.entity_type}' != '{new_anno.entity_type}'"

            # print(f"{bf_diabetes_note.text[orig_anno.start():orig_anno.end()]} -- {self.bf_synth.text[new_anno.start():new_anno.end()]}")
            # Is the text in the file the same?
            assert bf_diabetes_note.text[orig_anno.start():orig_anno.end()] == self.bf_synth.text[new_anno.start():new_anno.end()], \
                "Text should match, but it does not match."


class TestAddNotice(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # create BratFile object with surrogate substition with a notice
        bsyn = BratSynthetic(BratSyntheticConfigForTesting(), logger)
        self.bf_synth_notice = bsyn.syntheticize_brat_file(bf_diabetes_note)
        
        # create BratFile object with surrogate substition without a notice
        config_wo = BratSyntheticConfigForTesting()
        config_wo.general.suppress_phi_notice = True
        bsyn_wo = BratSynthetic(config_wo, logger)
        self.bf_synth = bsyn_wo.syntheticize_brat_file(bf_diabetes_note)
        
        self.phi_notice = "THIS IS NOT A REAL CLINICAL DOCUMENT. SYNTHETIC NAMES AND OTHER PERSONAL IDENTIFYING " \
            "INFORMATION (PHI) CORRESPONDING TO THE PHI OF ANY REAL PERSON IS UNINTENTIONAL"

    def test_has_phi_notice(self):
        assert self.bf_synth_notice.text.startswith(self.phi_notice), "Document self.bf_synth_notice.text is missing PHI Notice"

    def test_has_no_notice(self):
        """Make sure document w/o a notice does not start with the notice."""
        assert not self.bf_synth.text.startswith(self.phi_notice), "self.by_synth.text has a PHI Notice when it should not."

    def _annotations_match_text_document(self, bf_syth: BratFile):
        """Check that there is is 1 DATE annotation and that what is in the text document also has [**DATE**] tagged."""
        # T20 is a DATE
        date_annotations = [anno for anno in bf_syth.annotations if anno.identifier == "T20"]

        assert len(date_annotations) == 1, f"Example expected to have one DATE label, not {len(date_annotations)=}."
        
        date_annotation = date_annotations[0]
        assert date_annotation.text == "[**DATE**]", "Expected [**DATE**] tag"

        date_text = bf_syth.text[date_annotation.start():date_annotation.end()]
        assert date_text == "[**DATE**]", f"Did not find [**DATE**] between spans {date_annotation.start()}:{date_annotation.end()}, it has '{date_text}' instead"

    def test_annotations_match_text_document_with_notice(self):
        self._annotations_match_text_document(self.bf_synth_notice)

    def test_annotations_match_text_document_without_notice(self):        
        self._annotations_match_text_document(self.bf_synth)


if __name__ == "__main__":
    unittest.main()
