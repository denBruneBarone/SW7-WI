from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import pprint


def parse_and_stem(text):
    # Initialize the stemmer
    stemmer = PorterStemmer()

    # Handle None or empty input
    if text is None or (isinstance(text, list) and len(text) == 0) or (isinstance(text, str) and text.strip() == ""):
        return []

    # If the input is a list, process each string in the list
    if isinstance(text, list):
        indexed_tokens = []
        token_index_offset = 0  # To keep track of the token index across multiple strings

        # Iterate over each string in the list
        for string in text:
            if string.strip():  # Skip empty strings in the list
                tokens = word_tokenize(string)

                # Tokenize and stem each token in the current string
                for index, token in enumerate(tokens):
                    stemmed_token = stemmer.stem(token)
                    indexed_tokens.append((token_index_offset + index, stemmed_token))

                # Update the offset for the next string to account for previous token indices
                token_index_offset += len(tokens)

    # If the input is a single string, process it directly
    else:
        # Tokenize the input string
        tokens = word_tokenize(text)

        # Index the tokens and stem them
        indexed_tokens = [(index, stemmer.stem(token)) for index, token in enumerate(tokens)]

    return indexed_tokens