import config 
import requests
import re

import giphypop

import nltk
# from nltk.corpus import wordnet as wn

import spacy

MAX_FILE_SIZE = 3072 * 1024


# nltk.download('wordnet')
nlp = spacy.load("en_core")
giphy = giphypop.Giphy(api_key=config.GIPHY_KEY)



def is_valid_word(word):
    return (re.search(r'^[a-zA-Z][a-z0-9A-Z\._]*$', word) is not None)

def process_tweet(data):
    mentions = re.findall(r'@([A-Za-z0-9_]+)',data)

    raw_tokens = re.sub(r"@([A-Za-z0-9_]+)","",data)
    raw_tokens = raw_tokens.strip()

    raw_tokens = nlp(raw_tokens)

    tokens = dict()
    all_tokens = []
    for token in raw_tokens:
        all_tokens.append(token.text)
        if not nlp.vocab[token.text.lower()].is_stop and is_valid_word(token.text) and token.tag_ in ["NN", "NNS", "NNP", "VB"]: 
            tokens[token.tag_] = tokens.get(token.tag_,[])
            tokens[token.tag_].append(token.text)
            # print(tokens)
            # if token.tag_ != "NNP":
            #     synonyms_set = wn.synsets(token.text)
            #     print(synonyms_set)
            #     if synonyms_set:
            #         print(synonyms_set[0].lemma_names())
    
    print(all_tokens)

    return mentions, tokens, all_tokens

def write_to_file(gif_url, file_path):
    f = open(file_path, 'wb')
    f.write(requests.get(gif_url).content)
    f.close()

def get_gif(FILE_PATH, token, n_gifs = 5,random=False):
    gifs = [gif for gif in giphy.search(token, limit = n_gifs) if gif.filesize < MAX_FILE_SIZE]
    if gifs:
        url = gifs[0].media_url
        write_to_file(gif_url = url, file_path = FILE_PATH)
        return True

    return False

if __name__ == "__main__":
    print(process_tweet("@imTwif @im_Twif , i need some coffee, cover-up"))