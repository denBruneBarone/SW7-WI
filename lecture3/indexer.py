from parser import parse_and_stem
import json
from collections import defaultdict
import pprint
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize


def build_inverted_index(file_path):
    # Load the JSON file
    with open(file_path, 'r') as f:
        url_backlog = json.load(f)

    url_to_doc_id = {url: idx for idx, url in enumerate(url_backlog.keys())}
    with open("url_to_doc_id.json", 'w') as f:
        json.dump(url_to_doc_id, f, indent=2)

    token_to_docs = defaultdict(set)

    for url, data in url_backlog.items():
        doc_id = url_to_doc_id[url]

        indexed_tokens = parse_and_stem(data)

        unique_stemmed_tokens = set(stemmed_token for _, stemmed_token in indexed_tokens)

        for stemmed_token in unique_stemmed_tokens:
            token_to_docs[stemmed_token].add(doc_id)

    # Construct the final inverted index in the desired format (token, doc_freq, [docIDs])
    inverted_index = []
    for token, doc_set in token_to_docs.items():
        doc_list = list(doc_set)  # Convert the set to a list
        doc_freq = len(doc_list)  # Frequency is the number of unique docs
        inverted_index.append((token, doc_freq, doc_list))

    return inverted_index


def query(string):
    tokens = word_tokenize(string)
    for token in tokens:
        # add
        pass




if __name__ == '__main__':
    result = build_inverted_index("../lecture2/url_backlog.json")
    with open('inverted_index.json', 'w') as file:
        json.dump(result, file, indent=2)

