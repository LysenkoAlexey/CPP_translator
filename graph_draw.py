from graphviz import Digraph
from lexer import Lexer, Token
from parser import Parser, iter_child_nodes
import ast
# Create a Graphviz Digraph object
dot = Digraph()

# Define a function to recursively add nodes to the Digraph
def add_node(node, field_name, parent=None):
    if isinstance(node, Token):
        node_name = f'{field_name}:\n {node}'
    else:
        node_name = f'{field_name}:\n {node.__class__.__name__}'
    dot.node(str(id(node)), node_name)
    if parent:
        dot.edge(str(id(parent)), str(id(node)))
    for field_name, child in iter_child_nodes(node):
        add_node(child, field_name, node)


with open("file.cpp", 'r', encoding='utf8') as f:
    pars = Parser(Lexer(f.read()))

tree = pars.parse()

# Add nodes to the Digraph
add_node(tree, 'root')

# Render the Digraph as a PNG file
dot.format = 'png'
dot.render('my_ast', view=True)