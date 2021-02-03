import json
import pickle

import fasttext
from elasticsearch import Elasticsearch
from kafka import KafkaConsumer
from keras.engine.saving import model_from_json
from tunga.preprocessing import normalization
import spacy
from keras.preprocessing import sequence

es = Elasticsearch()

json_file = open('../pretrained/lstm_model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
loaded_model.load_weights("../pretrained/lstm_model.h5")

tok = pickle.load(open("../pretrained/lstm_tokenizer.model", 'rb'))

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

    test_sequences = tok.texts_to_sequences([tweet_text])

    test_sequences_matrix = sequence.pad_sequences(test_sequences, maxlen=150)
    prediction = loaded_model.predict(test_sequences_matrix)[0]

    if prediction < 0.5:
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
    print(res)
    i += 1
