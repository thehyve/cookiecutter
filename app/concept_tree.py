from collections import defaultdict

TM_SEP = "\\\\"


def Tree(): return defaultdict(Tree)


def add(t, path):
    for node in path:
        t = t[node]


def dicts(t): return {k: dicts(t[k]) for k in t}


def get_leafs(tree, leafs=None):
    if not leafs:
        leafs = []
    if not tree.values():
        leafs.append(tree)

def build_tree(concept_paths):
    concept_tree = Tree()
    sp = [concept.split(TM_SEP) for concept in concept_paths]
    for path in sp:
        add(concept_tree, path)
    return dicts(concept_tree)
