from flask import Flask

app = Flask(__name__)
import pickle
import fasttext

model = fasttext.load_model("/home/burak/Desktop/cc.en.300.bin")
rfc = pickle.load(open("../random_forest.model", 'rb'))

@app.route('/')
def home():
    return str(rfc.predict([model.get_sentence_vector("critical format string vulnerebility found in linux kernel v5.4.54")]))


@app.route('/classify', methods=["POST"])
def hello_world():
    return 'Hello, World!'


app.run(host="0.0.0.0", port=3000)
