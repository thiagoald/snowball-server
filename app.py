import ipdb
import os
import sys
import json
import traceback
from flask import request, Flask, Response
from flask_cors import CORS, cross_origin
from snowball import search, read_vars, find_var, Node, snowball

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
vars = []
tree = None
index_filepath = None


@app.route('/query')
@cross_origin()
def query():
    global tree
    f_index_sorted = open(index_filepath)
    f_index_sorted.seek(0, os.SEEK_END)
    size = f_index_sorted.tell()
    # print("Searching...")
    key = request.args.get('key')
    node = tree.search(f_index_sorted, key, 0, size)
    if (node is not None):
        file, charstart = node.filename, node.charstart
        # file, charstart = search(key, 'index_sorted')
        head_idx, tail_idx = file.split("/")
        head = find_var(vars, int(head_idx))
        tail = find_var(vars, int(tail_idx))
        file = os.path.join(head, tail)
        charstart = int(charstart.rstrip())
        with open(file) as f2:
            f2.seek(charstart)
            str_ = f2.readline()
            json_ = json.loads(str_)
            json_["paperId"] = json_["id"]
            json_["abstract"] = json_["paperAbstract"]
            return Response(json.dumps(json_), status=200, mimetype='application/json')
    else:
        return Response("{}", status=200, mimetype='application/json')


@app.route('/queries')
@cross_origin()
def queries():
    jsons = []
    keys = request.args.get('keys').split(",")
    for key in keys:
        file, charstart = search(key, index_filepath)
        head_idx, tail_idx = file.split("/")
        head = find_var(vars, int(head_idx))
        tail = find_var(vars, int(tail_idx))
        file = os.path.join(head, tail)
        charstart = int(charstart.rstrip())
        with open(file) as f2:
            f2.seek(charstart)
            str_ = f2.readline()
            json_ = json.loads(str_)
            json_["paperId"] = json_["id"]
            json_["abstract"] = json_["paperAbstract"]
            jsons.append(json_)
    return Response(json.dumps(jsons), status=200, mimetype='application/json')


@app.route('/paper')
@cross_origin()
def get_paper():
    try:
        id = request.args.get('id')
        paper = search(id, index_filepath, vars)
        return Response(json.dumps(paper), status=200, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps({"error": traceback.print_exc()}), status=200, mimetype='application/json')


@ app.route('/snowball')
@ cross_origin()
def snowball_route():
    try:
        keys = request.args.get('ids').split(",")
    except:
        keys = []
    try:
        include = request.args.get('include').split(",")
    except:
        include = []
    try:
        min_year = int(request.args.get('minYear'))
    except:
        min_year = float('-inf')
    try:
        max_papers = int(request.args.get('maxPapers'))
    except:
        max_papers = 200
    snowball_result = snowball(
        vars_filepath, index_filepath, keys, include, min_year, max_papers)
    return Response(json.dumps(snowball_result),
                    status=200,
                    mimetype='application/json')


if __name__ == "__main__":
    index_filepath = sys.argv[1]
    vars_filepath = sys.argv[2]
    vars = read_vars(vars_filepath)
    app.run(debug=True, port=5001)
