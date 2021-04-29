import sys
import json
import ipdb
import os
from os import path
from snowball import add_to_vars, read_vars, find_idx
from multiprocessing import Pool, Manager, Value

manager = Manager()
vars = manager.list()


def write_to_file(jsons_filepath):
    head, tail = path.split(jsons_filepath)
    index_filepath = f"{tail}.index"
    print(f"Including {jsons_filepath}... len(vars)={len(vars)}")
    try:
        if (not os.path.exists(index_filepath)):
            try:
                head_idx = vars.index(head)
            except ValueError:
                vars.append(head)
                head_idx = vars.index(head)
            try:
                tail_idx = vars.index(tail)
            except ValueError:
                vars.append(tail)
                tail_idx = vars.index(tail)
            with open(index_filepath, "w") as f_index:
                with open(jsons_filepath) as f:
                    while True:
                        start = f.tell()
                        line = f.readline()
                        if (len(line) == 0):
                            break
                        paperId = json.loads(line)["id"]
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
    filepaths = [f for f in sys.argv[4:] if 's2-corpus-' in f]
    with Pool(processes) as p:
        p.map(write_to_file, [filepaths[i]
                              for i in range(len(filepaths))])
    for filepath in filepaths:
        write_to_file(filepath)
    with open(vars_filepath, "w") as f:
        for i, var in enumerate(vars):
            f.write(f"{i},{var}\n")
