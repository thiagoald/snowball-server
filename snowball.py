import ipdb
import os
import json
from nltk import PorterStemmer


def read_vars(filename, return_max=False):
    vars = []
    with open(filename) as f_vars:
        for line in f_vars:
            if line != "\n":
                idx, var = line.split(",")
                idx = int(idx)
                vars.append((idx, var.rstrip()))
    if (not return_max):
        return vars
    else:
        return vars, max([v[0] for v in vars], default=0)


def add_to_vars(vars, vars_filepath, new_var_idx, new_var):
    vars.append((new_var_idx, new_var.rstrip()))
    with open(vars_filepath, "a") as f_vars:
        f_vars.write(f"\n{new_var_idx},{new_var}")


def find_var(vars, idx_var):
    try:
        return vars[[v[0] for v in vars].index(idx_var)][1]
    except ValueError:
        return None


def find_idx(vars, var):
    try:
        return vars[[v[1] for v in vars].index(var)][0]
    except ValueError:
        return None


class Node:
    def __init__(self):
        self.hash = None
        self.filename = None
        self.charstart = None
        self.node_left = None
        self.node_right = None
        self.start = None
        self.end = None

    def __repr__(self, start=""):
        if (self.node_left == self.node_right == None):
            return f"{start} {self.hash}"
        elif (self.node_left == None):
            return f"{start} {self.hash}\n{self.node_right.__repr__(start + '  ')}"
        elif (self.node_right == None):
            return f"{start} {self.hash}\n{self.node_left.__repr__(start + '  ')}"
        else:
            return (f"{start} {self.hash}\n{self.node_left.__repr__(start + '  ')}\n"
                    f"{start} {self.node_right.__repr__(start + '  ')}")

    def count(self, start=0):
        if (self.node_left == self.node_right == None):
            return start+1
        elif (self.node_left == None):
            return self.node_right.count(start+1)
        elif (self.node_right == None):
            return self.node_left.count(start+1)
        else:
            return (self.node_left.count(start+1) +
                    self.node_right.count(start+1))

    def height(self, start=0):
        if (self.node_left == self.node_right == None):
            return start
        elif (self.node_left == None):
            return self.node_right.height(start+1)
        elif (self.node_right == None):
            return self.node_left.height(start+1)
        else:
            return max(self.node_left.height(start+1),
                       self.node_right.height(start+1))

    def search(self, file, hash, start, end):
        if (self.hash == None):
            self.start = start
            self.end = end
            file.seek(start + (end-start)//2)
            file.readline()
            line = file.readline()
            self.hash, self.filename, self.charstart = line.split(",")
        if (hash == self.hash):
            return self
        elif (end - start <= 1):
            return None
        else:
            if (hash < self.hash):
                if (self.node_left == None):
                    self.node_left = Node()
                return self.node_left.search(
                    file, hash, start, start + (end-start)//2)
            else:
                if (self.node_right == None):
                    self.node_right = Node()
                self.node_right = Node()
                return self.node_right.search(
                    file, hash, start + (end-start)//2, end)


def search(hash, index_filename, vars):
    f = open(index_filename, "r")
    f.seek(0, os.SEEK_END)
    size = f.tell()
    start = 0
    end = size
    last_line = None
    found = False
    while True:
        mid = start + (end-start)//2
        # print(end-start, start, mid, end)
        # Go to start of line
        curr = mid
        f.seek(curr)
        while (curr > 0 and f.read(1) != "\n"):
            f.seek(curr)
            curr -= 1
        # f.seek(mid)

        line = f.readline()
        if last_line != None and line == last_line:
            break
        else:
            last_line = line
        # line = f.readline()
        # print(line.split(","))
        hash_, file, charstart = line.split(",")
        if (hash == hash_):
            found = True
            break
        else:
            if (hash > hash_):
                start = mid
            else:
                end = mid
    # print(f"Steps: {i}")
    if (found):
        return fetch_paper_from_fs(file, charstart, vars)
    else:
        # ipdb.set_trace()
        print(f"Could not find {hash} in index")
        return None


def fetch_paper_from_fs(filename, charstart, vars):
    head_idx, tail_idx = filename.split("/")
    head = find_var(vars, int(head_idx))
    tail = find_var(vars, int(tail_idx))
    file = os.path.join(head, tail)
    charstart = int(charstart.rstrip())
    with open(file) as f:
        f.seek(charstart)
        str_ = f.readline()
        try:
            json_ = json.loads(str_)
        except:
            ipdb.set_trace()
            print(f"Could not fech paper from {file}. Incorrect JSON")
            return None
        return json_


def snowball(vars_filepath, index_filepath, hashes, words_to_include, min_year, max_papers=None):
    ps = PorterStemmer()
    vars = read_vars(vars_filepath)

    words_to_include = [ps.stem(word) for word in words_to_include]
    papers = []
    for h in hashes:
        paper = search(h, index_filepath, vars)
        if paper is not None:
            papers.append(paper)
        else:
            print(f"Failed to find {h}")
    papersIn = {}
    for hash in hashes:
        papersIn[hash] = True
    stack = [p for p in papers]
    final_papers = []
    while stack:
        paper = stack.pop(0)
        hashes = paper["inCitations"] + paper["outCitations"]
        print((f"Stack {len(stack)}"
               f" | Final {len(final_papers)}"
               f" | Paper = {paper['id']}"
               f" | Citations = {len(hashes)}"))
        for i, h in enumerate(hashes):
            if h not in papersIn:
                paper = search(h, index_filepath, vars)
                if (paper is not None and
                        all([word in paper["title"].lower() or
                             word in paper["paperAbstract"].lower() for word in words_to_include]) and
                        (paper['year'] is None or paper['year'] > min_year)):
                    stack.append(paper)
                    final_papers.append(paper)
                    papersIn[paper["id"]] = True
                    if (not (max_papers is None) and len(final_papers) >= max_papers):
                        return final_papers
    return []


if __name__ == "__main__":
    papers = snowball("vars",
                      "index",
                      ["3898ac5cde941c4ccace3f63e84c6f4960ff3ad4"],
                      ["surface", "bacteria", "antibacterial"],
                      2010, 1000)
    print(papers)
