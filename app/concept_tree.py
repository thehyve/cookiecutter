TM_SEP = "\\\\"


def build_tree(concepts):
    nodes = []
    for var in concepts:
        splittage = var.path.split(TM_SEP)
        nodes.append(TreeNode(splittage, var))
    merged_node = nodes.pop(0)
    for node in nodes:
        merged_node.merge(node)
    return [merged_node]


class TreeNode:
    def __init__(self, path, var):
        assert var is not None
        assert path is not None
        self.text = ''
        self.children = []
        self.tmVariable = {}
        self.state = {}
        self.icon = ''
        f = path.pop(0)
        self.text = f
        if len(path) > 0 and not is_categorical_folder(path, var):
            self.children.append(TreeNode(path, var))
        else:
            self.tmVariable = var
        if not self.is_leaf():
            self.state['opened'] = True
            self.icon = None
        else:
            self.icon = "jstree-file"

    def is_leaf(self):
        return len(self.children) == 0

    def merge(self, another):
        if self.text == another.text:
            for anotherChild in another.children:
                merged_any = False
                for ownChild in self.children:
                    merged = ownChild.merge(anotherChild)
                    if merged:
                        merged_any = True
                if not merged_any:
                    self.children.append(anotherChild)
            if not self.is_leaf():
                self.state['opened'] = True
                self.icon = None
            else:
                self.icon = "jstree-file"
            return True
        else:
            return False


def is_categorical_folder(path, var):
    isFolder = len(path) == 1  # about to add leaf
    isCat = var.type == "CATEGORICAL_OPTION"
    return isFolder and isCat
