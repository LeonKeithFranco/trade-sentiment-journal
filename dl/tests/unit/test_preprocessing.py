import pytest
from utils.preprocess import process_sentence


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
    ],
)
def test_sentence_processing(sentence: str, expected_output: str) -> None:
    assert process_sentence(sentence) == expected_output
