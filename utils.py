import re
import random

import requests
import giphypop
import nltk
import spacy

import config

MAX_FILE_SIZE = 3072 * 1024

nlp = spacy.load("en_core")
giphy = giphypop.Giphy(api_key=config.GIPHY_KEY)

def is_valid_word(word):
    return (re.search(r'^[a-zA-Z][a-z0-9A-Z\._]*$', word) is not None)

def process_tweet(tweet):
    mentions = re.findall(r'@([A-Za-z0-9_]+)', tweet)
    raw_tokens = re.sub(r"@([A-Za-z0-9_]+)", "", tweet)
    raw_tokens = raw_tokens.strip()
    raw_tokens = nlp(raw_tokens)

    all_tokens = []
    for token in raw_tokens:
        if not nlp.vocab[token.text.lower()].is_stop and is_valid_word(token.text) and token.tag_ in ["NN", "NNS", "NNP", "VB"]:
            all_tokens.append(token.text)

    return mentions, all_tokens


def write_to_file(gif_url, file_path):
    f = open(file_path, 'wb')
    f.write(requests.get(gif_url).content)
    f.close()


def get_gif(FILE_PATH, token, n_gifs=5):
    gifs = [gif for gif in giphy.search(token, limit=n_gifs) if gif.filesize < MAX_FILE_SIZE]
    if gifs:
        index = random.randint(0, len(gifs)-1)
        url = gifs[index].media_url
        write_to_file(gif_url=url, file_path=FILE_PATH)
        return True

    return False

if __name__ == "__main__":
    print(process_tweet("@imTwif @im_Twif , i need some coffee, cover-up"))
