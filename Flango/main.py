from flask import Flask, request, render_template
import pandas as pd
from pymongo import MongoClient
import json


app = Flask(__name__, template_folder='Templates')
app.config['SECRET_KEY'] = 'you-will-never-guess'

with open('config.json') as f:
    conf = f.read()
    conf = json.loads(conf)
    uri = conf['URI']
    database = conf['Database']

CONNECTION = MongoClient(uri,  connect = False)
db = CONNECTION[database]

@app.route('/', methods=['GET', 'POST'])
def get_main():
    '''
    home
    '''
    boolean = False
    collections = db.collection_names()
    if request.method == 'POST':
        # check if the post request has the file part
        file = request.files.get('file')
        col = request.form.get('collection')
        sep = request.form.get('separator')
        if file and col:
            if not col in collections:
                file_extension = file.filename.rsplit('.',1)[-1]
                if file_extension == 'csv':
                    df = pd.read_csv(file, sep = sep)
                elif file_extension == 'xlsx':
                    df = pd.read_excel(file)
                columns = df.columns.values
                columns = [item for item in columns if not 'Unnamed' in item ]
                df = df[columns]
                data = df.to_dict('records')
                r = db[col].insert_many(data)
                boolean = r.acknowledged
    return render_template('index.html', collections = collections, boolean = boolean)

if __name__ == "__main__":
    app.run(port= 4999)
