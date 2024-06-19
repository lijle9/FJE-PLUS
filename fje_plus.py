import json
import argparse
from abc import ABC, abstractmethod

# Component base class
class Component(ABC):
    @abstractmethod
    def draw(self, indent="", is_last=True):
        pass

    @abstractmethod
    def accept(self, visitor):
        pass

# Iterator for the Component tree
class ComponentIterator:
    def __init__(self, root):
        self.stack = [root]

    def __iter__(self):
        return self

    def __next__(self):
        if not self.stack:
            raise StopIteration
        current = self.stack.pop()
        if isinstance(current, (TreeContainer, RectangleContainer)):
            self.stack.extend(reversed(current.children))
        return current

# Visitor base class
class Visitor(ABC):
    @abstractmethod
    def visit(self, component):
        pass

# Concrete Visitor for drawing components
class DrawVisitor(Visitor):
    def visit(self, component):
        component.draw()

# Container class for Tree style
class TreeContainer(Component):
    def __init__(self, icons, name, level):
        self.icons = icons
        self.name = name
        self.level = level
        self.children = []

    def add(self, component):
        self.children.append(component)

    def draw(self, indent="", is_last=True, is_top=True, is_bottom=False):
        branch_icon = self.icons['last_branch_icon'] if is_last else self.icons['branch_icon']
        print(f"{indent}{branch_icon} {self.name}")
        new_indent = indent + ("   " if is_last else self.icons['vertical_line'] + "  ")
        for i, child in enumerate(self.children):
            is_last_child = i == len(self.children) - 1
            child.draw(new_indent, is_last=is_last_child)

    def accept(self, visitor):
        visitor.visit(self)

# Leaf class for Tree style
class TreeLeaf(Component):
    def __init__(self, icons, name):
        self.icons = icons
        self.name = name

    def draw(self, indent="", is_last=True, is_top=True, is_bottom=False):
        leaf_icon = self.icons['leaf_icon']
        leaf_prefix = self.icons['leaf_prefix']
        print(f"{indent}{leaf_prefix if is_last else leaf_icon} {self.name}")

    def accept(self, visitor):
        visitor.visit(self)

# Container class for Rectangle style
class RectangleContainer(Component):
    def __init__(self, icons, name, level):
        self.icons = icons
        self.name = name
        self.level = level
        self.children = []

    def add(self, component):
        self.children.append(component)

    def draw(self, indent="", is_last=True, is_top=False, is_bottom=False):
        top_left_corner = self.icons['top_left_corner']
        top_right_corner = self.icons['top_right_corner']
        bottom_left_corner = self.icons['bottom_left_corner']
        bottom_right_corner = self.icons['bottom_right_corner']
        horizontal_line = self.icons['horizontal_line']
        vertical_line = self.icons['vertical_line']
        left_branch_icon = self.icons['left_branch_icon']
        branch_icon = self.icons['branch_icon']

        # Start drawing the container box
        if is_top:
            print(f"{indent}{top_left_corner}{self.name}{horizontal_line * (33 - len(indent))}{top_right_corner}")
        else:
            print(f"{indent}{branch_icon}{self.name}{horizontal_line * (40 - len(indent) - len(self.name) - 2)}{left_branch_icon}")

        # Print children
        new_indent = indent + vertical_line + " "
        for i, child in enumerate(self.children):
            is_last_child = i == len(self.children) - 1
            child.draw(new_indent, is_last_child, is_top=False)
        
        # End drawing the container box
        if is_bottom:
            print(f"{indent}{bottom_left_corner}{horizontal_line * (40 - len(indent))}{bottom_right_corner}")

    def accept(self, visitor):
        visitor.visit(self)

# Leaf class for Rectangle style
class RectangleLeaf(Component):
    def __init__(self, icons, name):
        self.icons = icons
        self.name = name

    def draw(self, indent="", is_last=True, is_top=True, is_bottom=False):
        leaf_icon = self.icons['leaf_icon']
        horizontal_line = self.icons['horizontal_line']
        left_branch_icon = self.icons['left_branch_icon']
        print(f"{indent}{leaf_icon} {self.name}{horizontal_line * (40 - len(indent) - len(self.name) - 3)}{left_branch_icon}")

    def accept(self, visitor):
        visitor.visit(self)

# Factory class for Tree style
class TreeStyleFactory:
    def __init__(self, icon_family_file):
        self.icons = self.load_icons(icon_family_file)

    def load_icons(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def create_container(self, name, level):
        return TreeContainer(self.icons, name, level)

    def create_leaf(self, name):
        return TreeLeaf(self.icons, name)

# Factory class for Rectangle style
class RectangleStyleFactory:
    def __init__(self, icon_family_file):
        self.icons = self.load_icons(icon_family_file)

    def load_icons(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def create_container(self, name, level):
        return RectangleContainer(self.icons, name, level)

    def create_leaf(self, name):
        return RectangleLeaf(self.icons, name)

# Function to load JSON file
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Function to build tree
def build_tree(data, factory, level=0):
    if isinstance(data, dict):
        key = list(data.keys())[0]
        value = data[key]

        container = factory.create_container(key, level)

        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                if isinstance(subvalue, dict) or isinstance(subvalue, list):
                    container.add(build_tree({subkey: subvalue}, factory, level + 1))
                else:
                    container.add(factory.create_leaf(f"{subkey}: {subvalue}"))
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict) or isinstance(item, list):
                    container.add(build_tree(item, factory, level + 1))
                else:
                    container.add(factory.create_leaf(item))
        else:
            container.add(factory.create_leaf(f"{key}: {value}"))

        return container
    else:
        return factory.create_leaf(data)

# Function to display tree
def display_tree(json_file, style_factory):
    data = load_json(json_file)
    tree = []
    for key, value in data.items():
        tree.append(build_tree({key: value}, style_factory))
    for i, subtree in enumerate(tree):
        iterator = ComponentIterator(subtree)
        draw_visitor = DrawVisitor()
        is_last_tree = i == len(tree) - 1
        subtree.accept(draw_visitor)
        if is_last_tree and style_factory.__class__.__name__ == 'RectangleStyleFactory':
            subtree.draw(is_bottom=True)

# Main function for argument parsing and execution
def main():
    parser = argparse.ArgumentParser(description="Funny JSON Explorer")
    parser.add_argument("-f", "--file", required=True, help="Path to the JSON file")
    parser.add_argument("-s", "--style", choices=['tree', 'rectangle'], default='tree', help="Style of the output")
    parser.add_argument("-i", "--icon", required=True, help="Path to the icon family JSON file")

    args = parser.parse_args()

    if args.style == 'tree':
        factory = TreeStyleFactory(args.icon)
    else:
        factory = RectangleStyleFactory(args.icon)

    display_tree(args.file, factory)

if __name__ == "__main__":
    main()
