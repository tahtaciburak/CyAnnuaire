import json
import pickle

import fasttext
from elasticsearch import Elasticsearch
from kafka import KafkaConsumer
from tunga.preprocessing import normalization
import spacy

es = Elasticsearch()

model = fasttext.load_model("/home/burak/Desktop/cc.en.300.bin")
rfc = pickle.load(open("../random_forest.model", 'rb'))
nlp = spacy.load('../../../data/buyuk')
consumer = KafkaConsumer('crawled_tweets', bootstrap_servers=['localhost:9091'])
print(consumer)
i = 1
for message in consumer:
    data = json.loads(message.value)

    tweet_text = data["tweet"]
    tweet_text = tweet_text.lower()
    tweet_text = tweet_text.strip()
    tweet_text = tweet_text.replace("\n", " ")
    tweet_text = normalization.remove_url(tweet_text)
    tweet_text = normalization.remove_hashtag(tweet_text)
    tweet_text = normalization.remove_emojis(tweet_text)

    prediction = rfc.predict([model.get_sentence_vector(tweet_text)])[0]
    if prediction == 0:
        data["class"] = "cyber"
        doc = nlp(tweet_text)
        params = {}

        for ent in doc.ents:
            lab = ent.label_.split("-")[1]
            if lab not in params:
                params[lab] = ent.text
            else:
                params[lab] = params[lab] + " " + ent.text
        data["params"] = params
    else:
        data["class"] = "non-cyber"
        data["params"] = {}

    print(data)
    res = es.index(index="tweet", id=i, body=data)
    i += 1
