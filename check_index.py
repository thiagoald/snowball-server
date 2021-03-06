import sys
import json
from os import path
from snowball import read_vars, find_var
import ipdb

if __name__ == "__main__":
    index_filepath = sys.argv[1]
    vars_filepath = sys.argv[2]
    vars = read_vars(vars_filepath)
    i_line = 0
    with open(index_filepath, 'r') as f_index:
        try:
            while True:
                i_line += 1
                line = f_index.readline()
                if line == "":
                    break
                hash, filepath, charnumber = line.split(',')
                charnumber = int(charnumber.rstrip())
                filepath = path.join(*[find_var(vars, int(v))
                                       for v in filepath.split("/")])
                with open(filepath, 'r') as f:
                    f.seek(charnumber)
                    hash_ = json.loads(f.readline())["id"]
                    assert(hash == hash_)
        except Exception as e:
            print("ERROR")
            print(e)
            ipdb.set_trace()
