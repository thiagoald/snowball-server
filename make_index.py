import sys
import json
import ipdb
from os import path
from snowball import add_to_vars, read_vars, find_idx

vars = []
new_var_idx = 0


if __name__ == "__main__":
    print(sys.argv)
    vars_filepath = sys.argv[1]
    index_filepath = sys.argv[2]
    vars, max_idx = read_vars(vars_filepath, return_max=True)
    new_var_idx = max_idx + 1
    with open(index_filepath, 'w') as f_index:
        for file in [f for f in sys.argv[3:] if 's2-corpus-' in f]:
            head, tail = path.split(file)
            # ipdb.set_trace()
            head_idx = find_idx(vars, head)
            tail_idx = find_idx(vars, tail)
            if (head_idx is None):
                add_to_vars(vars, vars_filepath, new_var_idx, head)
                head_idx = new_var_idx
                new_var_idx += 1
            if (tail_idx is None):
                add_to_vars(vars, vars_filepath, new_var_idx, tail)
                tail_idx = new_var_idx
                new_var_idx += 1
            print(f"Including {file}...")
            with open(file) as f:
                while True:
                    start = f.tell()
                    line = f.readline()
                    if (len(line) == 0):
                        break
                    paperId = json.loads(line)["id"]
                    end = f.tell()
                    count = end-start
                    f_index.write(f"{paperId},{head_idx}/{tail_idx},{start}\n")
