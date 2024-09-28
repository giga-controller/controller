import string

from Levenshtein import distance, ratio

# TODO: We can make this threshold specific to each integration
THRESHOLD = 0.4  # For more strict matching, set the threshold HIGHER


def _process_string(input: str) -> str:
    """Strips all insignificant characters from the input string before initiating best match search"""

    # Standardise casing
    input = input.lower()

    # Remove all spaces
    input = input.replace(" ", "")

    return input


def get_most_similar_string(target: str, candidates: list[str]) -> str:
    """Returns the most similar string from the candidates list to the target"""
    most_similar: str = min(
        candidates,
        key=lambda candidate: distance(
            _process_string(candidate), _process_string(target)
        ),
    )
    # Return the original value if the similarity is less than the threshold
    if ratio(most_similar, target) < THRESHOLD:
        return target
    return most_similar
