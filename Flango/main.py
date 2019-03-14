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

#connection to mongodb
CONNECTION = MongoClient(uri,  connect = False)
db = CONNECTION[database]

@app.route('/', methods=['GET', 'POST'])
def get_main():
    '''
    home
    '''
    boolean = False
    # get existing collections in database
    collections = db.collection_names()
    if request.method == 'POST':
        # check if the post request has the file part
        file = request.files.get('file')
        # get name for collection
        col = request.form.get('collection')
        # get separator if csv will be imported
        sep = request.form.get('separator')
        if file and col:
            # if collection name is non existent in database
            if not col in collections:
                file_extension = file.filename.rsplit('.',1)[-1]
                if file_extension == 'csv':
                    df = pd.read_csv(file, sep = sep)
                elif file_extension == 'xlsx':
                    df = pd.read_excel(file)
                columns = df.columns.values
                # drop columns which are Unnamed
                columns = [item for item in columns if not 'Unnamed' in item ]
                #replace dot in columns names
                df = df[columns]
                dot = [item for item in columns if '.' in item]
                if dot:
                    correct = {}
                    for item in dot:
                        correct[item] = item.replace('.',' ')
                    df.rename(columns = correct, inplace = True)
                #set NAN to ''
                df.fillna('', inplace = True)
                data = df.to_dict('records')
                r = db[col].insert_many(data)
                boolean = r.acknowledged
                # refresh existing collections
                collections = db.collection_names()
    return render_template('index.html', collections = collections, boolean = boolean)

if __name__ == "__main__":
    app.run(port= 4999)
