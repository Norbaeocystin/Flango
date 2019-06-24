from flask import Flask, request, render_template
import pandas as pd
from pymongo import MongoClient
import json

#change to your fields which you want to be displayed on table and query dynamic webpages
HEADER = ['Company Name', 'Emails','Country','Full Address', 'Type', 'Category', 'Sub Category', 'Collection']

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
def collections_true(db, pipeline):
    collections = db.list_collection_names()
    found_in = []
    counter = 0
    match, project = pipeline
    for item in collections:
        results = db[item].count_documents(match['$match'])
        if results:
            counter += results
            found_in.append(item)
    return {'Found':counter, 'Collections':found_in}

def get_docs_from_collections(db, pipeline, collections):
    found_in = []
    match, project = pipeline
    for item in collections:
        results = db[item].find(match['$match'], project['$project'])
        records = list(results)
        for record in records:
            record['Emails'] = ', '.join(record.get('Emails',[]))
            record['Collection'] = item
        found_in.extend(records)
    return found_in

@app.route('/search', methods=['GET', 'POST'])
def get_search():
    # it is same as projected
    if request.method == 'POST':
        dir(reque)
        query = {}
        for k,v in request.form.items():
            if v:
                query[k] = v
        if query:
            pipeline = create_pipeline(query)
            result = collections_true(db, pipeline)
            flash('Found {}'.format(result['Found']))
            collections = result['Collections']
            docs = get_docs_from_collections(db, pipeline, collections)
            #delimiter is semicollon ;
            data = ';'.join(HEADER)
            data += '\n'
            for item in docs:
                data += ';'.join([str(item.get(col_name, ' ')) for col_name in HEADER])
                data += '\n'
            output = make_response(data)
            output.headers["Content-Disposition"] = "attachment; filename=export.csv"
            output.headers["Content-type"] = "text/csv"
            #return .csv file with data to download
            return output
    return render_template('search.html')

@app.route('/<query>')
def get_query(query):
    if query == "query":
        # shows raw data as webpage
        query_dict = {}
        for item in request.args:
            k,v = item, request.args.get(item, '')
            if v:
                query_dict[k] = v
        if query_dict:
            pipeline = create_pipeline(query_dict)
            result = collections_true(db, pipeline)
            collections = result['Collections']
            docs = get_docs_from_collections(db, pipeline, collections)
            data = ';'.join(HEADER)
            data += '\n'
            for item in docs:
                data += ';'.join([str(item.get(col_name, ' ')) for col_name in HEADER])
                data += '\n'
            #output = make_response(data)
            #output.headers["Content-Disposition"] = "attachment; filename=export.csv"
            #output.headers["Content-type"] = "text/csv"
            return data, 200, {'Content-Type': 'text/css; charset=utf-8'}
        
    if query == "table":
        # shows data in html table 
        query_dict = {}
        for item in request.args:
            k,v = item, request.args.get(item, '')
            if v:
                query_dict[k] = v
        if query_dict:
            pipeline = create_pipeline(query_dict)
            result = collections_true(db, pipeline)
            collections = result['Collections']
            docs = get_docs_from_collections(db, pipeline, collections)
            return render_template('table.html', data = docs, headers = HEADER)
    return "<strong>Not found</strong>", 404

if __name__ == "__main__":
    app.run(port= 4999)
