import sys
from snowball import read_vars, snowball_search, Node, search


if __name__ == "__main__":
    hash = sys.argv[1]
    vars_filename = sys.argv[2]
    index_filename = sys.argv[3]
    tree = Node()
    # papers = snowball_search(
    #     index_filename, [hash], tree, read_vars(vars_filename))
    # print(papers)
    paper = search(hash, index_filename, read_vars(vars_filename))
    print(paper)
