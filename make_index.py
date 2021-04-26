import sys
import json
import ipdb
import os
from os import path
from snowball import add_to_vars, read_vars, find_idx
from multiprocessing import Pool, Manager, Value

manager = Manager()
vars = manager.list()
new_var_idx = manager


def write_to_file(jsons_filepath):
    head, tail = path.split(jsons_filepath)
    index_filepath = f"{tail}_.index"
    print(f"Including {jsons_filepath}...")
    try:
        if (not os.path.exists(index_filepath)):
            head_idx = find_idx(vars, head)
            tail_idx = find_idx(vars, tail)
            if (head_idx is None):
                add_to_vars(vars, vars_filepath, new_var_idx.value, head)
                head_idx = new_var_idx.value
                new_var_idx.value += 1
            if (tail_idx is None):
                add_to_vars(vars, vars_filepath, new_var_idx.value, tail)
                tail_idx = new_var_idx.value
                new_var_idx.value += 1
            with open(index_filepath, "a") as f_index:
                with open(jsons_filepath) as f:
                    while True:
                        start = f.tell()
                        line = f.readline()
                        if (len(line) == 0):
                            break
                        paperId = json.loads(line)["id"]
                        end = f.tell()
                        f_index.write(
                            f"{paperId},{head_idx}/{tail_idx},{start}\n")
        else:
            print(f"{index_filepath} already exists!")
    except KeyboardInterrupt:
        os.remove(index_filepath)


if __name__ == "__main__":
    print(sys.argv)
    vars_filepath = sys.argv[1]
    index_filepath = sys.argv[2]
    try:
        processes = int(sys.argv[3])
    except:
        processes = 1
    if (os.path.exists(vars_filepath)):
        vars_, max_idx = read_vars(vars_filepath, return_max=True)
        vars = Manager().list(vars_)
    else:
        vars, max_idx = Manager().list(), 0
    new_var_idx = Value('i', max_idx + 1)
    filepaths = [f for f in sys.argv[4:] if 's2-corpus-' in f]
    with Pool(processes) as p:
        p.map(write_to_file, [filepaths[i]
                              for i in range(len(filepaths))])
