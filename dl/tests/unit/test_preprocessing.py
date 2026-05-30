from pathlib import Path

import pytest
from pytest_mock import MockFixture
from utils.preprocess import map_sentence, process_sentence


@pytest.mark.parametrize(
    "sentence,expected_output",
    [
        (
            "The shares carry a right to dividend and other shareholder rights as from their registration with the Finnish Trade Register .",
            "the shares carry a right to dividend and other shareholder rights as from their registration with the finnish trade register",
        ),
        (
            "Also the city 's insurance company , If P & C Insurance , has said it will not pay compensation .",
            "also the city 's insurance company if p c insurance has said it will not pay compensation",
        ),
        (
            "The Americas represents 25 % of Gemalto 's billing , and Latin America is one of the fastest growing regions for the company .",
            "the americas represents <NUM> of gemalto 's billing and latin america is one of the fastest growing regions for the company",
        ),
        (
            "Dubai Nokia has announced the launch of `` Comes with Music '' , its ground-breaking service which introduces a new way for people to enjoy music .",
            "dubai nokia has announced the launch of comes with music its ground-breaking service which introduces a new way for people to enjoy music",
        ),
        (
            "A local waste management company , Turun Seudun J+Ætehuolto , has planned to set up a 150,000 tonne waste-burning facility .",
            "a local waste management company turun seudun has planned to set up a <NUM> tonne waste-burning facility",
        ),
        (
            "www.countryelements.co.uk Designed by Patricia Burt , this is just one of a selection of distinctive hooked rugs created with recycled materials and dyed natural dyes .",
            "designed by patricia burt this is just one of a selection of distinctive hooked rugs created with recycled materials and dyed natural dyes",
        ),
    ],
)
def test_sentence_processing(sentence: str, expected_output: str) -> None:
    assert process_sentence(sentence) == expected_output


@pytest.mark.parametrize(
    "sentence,expected_output",
    [
        (
            "The shares carry a right to dividend and other shareholder rights as from their registration with the Finnish Trade Register .",
            [
                6616,
                5925,
                1042,
                109,
                5585,
                6689,
                1884,
                377,
                4614,
                5920,
                5587,
                489,
                2653,
                6618,
                5382,
                7292,
                6616,
                2498,
                6749,
                5380,
            ],
        ),
        (
            "Also the city 's insurance company , If P & C Insurance , has said it will not pay compensation .",
            [
                329,
                6616,
                1199,
                10,
                3274,
                1324,
                3113,
                4660,
                963,
                3274,
                2922,
                5695,
                3394,
                7264,
                4422,
                4752,
                1336,
            ],
        ),
        (
            "The Americas represents 25 % of Gemalto 's billing , and Latin America is one of the fastest growing regions for the company .",
            [
                6616,
                354,
                5481,
                2,
                4487,
                2732,
                10,
                768,
                377,
                3630,
                352,
                3378,
                4527,
                4487,
                6616,
                2411,
                2841,
                5379,
                2569,
                6616,
                1324,
            ],
        ),
        (
            "Dubai Nokia has announced the launch of `` Comes with Music '' , its ground-breaking service which introduces a new way for people to enjoy music .",
            [
                1966,
                4384,
                2922,
                391,
                6616,
                3637,
                4487,
                1289,
                7292,
                4260,
                3402,
                2836,
                5888,
                7241,
                3332,
                109,
                4343,
                7190,
                2569,
                4789,
                6689,
                2150,
                4260,
            ],
        ),
        (
            "A local waste management company , Turun Seudun J+Ætehuolto , has planned to set up a 150,000 tonne waste-burning facility .",
            [
                109,
                3789,
                7176,
                3922,
                1324,
                6846,
                1,
                2922,
                4884,
                6689,
                5895,
                6948,
                109,
                2,
                6706,
                1,
                2378,
            ],
        ),
        (
            "www.countryelements.co.uk Designed by Patricia Burt , this is just one of a selection of distinctive hooked rugs created with recycled materials and dyed natural dyes .",
            [
                1759,
                960,
                4743,
                945,
                6642,
                3378,
                3476,
                4527,
                4487,
                109,
                5849,
                4487,
                1864,
                3040,
                5664,
                1568,
                7292,
                5333,
                3991,
                377,
                1983,
                4299,
                1984,
            ],
        ),
    ],
)
def test_sentence_mapping(sentence: str, expected_output: list[int]) -> None:
    assert map_sentence(process_sentence(sentence)) == expected_output


def test_sentence_mapping_no_file(mocker: MockFixture) -> None:
    fake_file = Path("/not-real-directory/not-real-file.json")

    mocker.patch("utils.constants.VOCAB_MAPPING_FILE_PATH", new=fake_file)

    with pytest.raises(
        FileNotFoundError,
        match=f"{fake_file.name} not found. Please run get_and_cache_data.py to generate the file",
    ):
        map_sentence("this is a sentence")
