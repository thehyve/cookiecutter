import json

TM_SEP = "\\"


def build_tree(concepts):
    nodes = []
    for var in concepts:
        splittage = var.path.split(TM_SEP)
        print(splittage)
        nodes.append(TreeNode(splittage, var))
    merged_node = nodes.pop(0)
    for node in nodes:
        merged_node.merge(node)
    return merged_node


class TreeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, TreeNode):
            return obj.as_dict()
        else:
            return json.JSONEncoder.default(self, obj)


class TreeNode:
    def __init__(self, path, var):
        assert var is not None
        assert path is not None
        assert len(path) > 0
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
            self.tmVariable = {'id': var.id,
                               'code': var.code,
                               'label': var.label,
                               'type': var.type,
                               }
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

    def as_dict(self):
        dict_rep = {
            'text': self.text,
            'children': [child.as_dict() for child in self.children],
            'tmVariable': self.tmVariable,
            'state': self.state,
            'icon': self.icon,
            'leaf': self.is_leaf(),
        }
        return dict_rep


def is_categorical_folder(path, var):
    is_folder = len(path) == 1  # about to add leaf
    is_cat = var.type == "CATEGORICAL_OPTION"
    return is_folder and is_cat
