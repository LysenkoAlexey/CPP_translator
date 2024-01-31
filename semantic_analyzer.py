import typing
from lexer import Lexer, Token
import parser


# ------------------------- Symbols
class Symbol():
    def __init__(self, name, _type=None):
        self.name = name
        self.type = _type
        self.hit_count = 0;

class BuiltinTypeSymbol(Symbol):
    def __init__(self, name):
        super().__init__(name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name})'>"


class VarSymbol(Symbol):
    def __init__(self, name, _type):
        super().__init__(name, _type)


    def __str__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', type='{self.type}', use_count={self.hit_count})>"

    __repr__ = __str__

class FormalVarSymbol(Symbol):
    def __init__(self, name, _type):
        super().__init__(name, _type)

    def __str__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', type='{self.type}', use_count={self.hit_count})>"

    __repr__ = __str__

class FunctionSymbol(Symbol):
    def __init__(self, name, params=None, ret_type=None):
        super(FunctionSymbol, self).__init__(name)
        # a list of formal parameters
        self.params = params if params is not None else []
        # TODO check this out
        self.ret_type = ret_type

    def __str__(self):
        return f'<{self.__class__.__name__}(name={self.name}, parameters={self.params}, ret_type={self.ret_type}), ' \
               f'use_count={self.hit_count}> '

    __repr__ = __str__


# -------------------------------- Symbol Table
class ScopedSymbolTable(object):
    def __init__(self, scope_name, scope_level, enclosing_scope=None):
        self._symbols: typing.Dict[str, Symbol]
        self._symbols = dict()
        self.scope_name = scope_name
        self.scope_level = scope_level
        self.enclosing_scope = enclosing_scope
        self.nested_scopes = dict()

    def _init_builtins(self):
        self.insert(BuiltinTypeSymbol('int'))
        self.insert(BuiltinTypeSymbol('float'))
        self.insert(BuiltinTypeSymbol('char'))
        self.insert(BuiltinTypeSymbol('string'))

    def __str__(self):
        h1 = 'SCOPE (SCOPED SYMBOL TABLE)'
        lines = ['\n', h1, '=' * len(h1)]
        for header_name, header_value in (
            ('Scope name', self.scope_name),
            ('Scope level', self.scope_level),
            ('Enclosing scope',
             self.enclosing_scope.scope_name if self.enclosing_scope else None
             )

        ):
            lines.append('%-15s: %s' % (header_name, header_value))
        h2 = 'Nested scopes'

        lines.extend([h2+ ' -' * len(h2)])
        lines.extend(
            ('%s' % (key, ))
            for key in self.nested_scopes.keys()
        )

        h2 = 'Scope (Scoped symbol table) contents'
        lines.extend([h2, '-' * len(h2)])
        lines.extend(
            ('%7s: %r' % (key, value))
            for key, value in self._symbols.items()
        )
        lines.append('\n')
        s = '\n'.join(lines)
        return s

    __repr__ = __str__

    def insert(self, symbol):
        #print('Insert: %s' % symbol.name)
        self._symbols[symbol.name] = symbol
        symbol.scope = self

    def lookup(self, name, current_scope_only=False, count=False):
        #print(f'Lookup: {name}. (Scope name: {self.scope_name})')
        # 'symbol' is either an instance of the Symbol class or None
        symbol: Symbol
        symbol = self._symbols.get(name)

        if symbol is not None:
            if count:
                self._symbols[name].hit_count += 1
            return symbol

        if current_scope_only:
            return None

        # recursively go up the chain and lookup the name
        if self.enclosing_scope is not None:
            return self.enclosing_scope.lookup(name)


class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        if isinstance(node, parser.Node):
            for field in node._fields:
                self.visit(getattr(node, field))

        else:
            raise Exception('No visit_{} method'.format(type(node).__name__))



class SemanticAnalyzer(NodeVisitor):
    def __init__(self, verbose=False):
        #self.scope = ScopedSymbolTable(scope_name='global', scope_level=1)
        self.current_scope = None
        self.error_count = 0
        self.errors = []
        self.scopes = dict()
        self.verbose = verbose

    def error(self, msg, lineno, pos):
        #raise RuntimeError(
        error_msg = f'Ошибка семантического анализа: {msg} ({lineno}, {pos})'
        self.error_count += 1
        self.errors.append(error_msg)
        if self.verbose:
            print(error_msg)

    def visit_NodeProgram(self, node: parser.NodeProgram):
        #print('ENTER scope: global')
        global_scope = ScopedSymbolTable(
            scope_name='global',
            scope_level=0,
            enclosing_scope=self.current_scope, # None
        )
        self.current_scope = global_scope
        self.scopes['global'] = global_scope
        global_scope._init_builtins() # init built-in types just once in global scope

        # visit subtree
        self.visit(node.block)

        #print(global_scope)

        self.current_scope = self.current_scope.enclosing_scope
        if not self.scopes.get('main', None):
            self.error("No 'main' function found", 0,0)
        #print('LEAVE scope: global')


    def visit_NodeFunction(self, node: parser.NodeFunction):
        func_name = node.name.value
        func_ret_type = node.ret_type.value
        func_symbol = FunctionSymbol(func_name, ret_type=func_ret_type)
        self.current_scope.insert(func_symbol)

        #print(f'ENTER scope: {func_name}')
        # Scope for parameters and local variables

        function_scope = ScopedSymbolTable(
            scope_name=func_name,
            scope_level=self.current_scope.scope_level + 1,
            enclosing_scope=self.current_scope,
        )
        self.current_scope.nested_scopes[func_name] = function_scope
        self.current_scope = function_scope
        self.scopes[func_name] = function_scope

        # Insert parameters into the procedure scope
        for param in node.formal_params.params:
            param_type = self.current_scope.lookup(param.type.value, count=True)
            if not param_type:
                self.error(f'Undefined type {param.type.value}', param.type.lineno, param.type.pos)
            param_name = param.name.value
            var_symbol = FormalVarSymbol(param_name, param_type)
            self.current_scope.insert(var_symbol)
            func_symbol.params.append(var_symbol)

        self.visit(node.block)

        #print(function_scope)

        self.current_scope = self.current_scope.enclosing_scope
        #print(f'LEAVE scope: {func_name}')

    def visit_VarDecl(self, node):
        type_name = node.type_node.value
        type_symbol = self.current_scope.lookup(type_name, count=True)

        # We have all the information we need to create a variable symbol.
        # Create the symbol and insert it into the symbol table.
        var_name = node.var_node.value
        var_symbol = VarSymbol(var_name, type_symbol)

        self.current_scope.insert(var_symbol)


    def visit_NodeDeclaration(self, node: Token):
        type_name = node.type.value
        type_symbol = self.current_scope.lookup(type_name, count=True)

        var_name = node.name.value
        var_symbol = VarSymbol(var_name, type_symbol)

        # Signal an error if the table already has a symbol with the same name
        if self.current_scope.lookup(var_name, current_scope_only=True, count = False):
            self.error(f"Повторное объявление '{var_name}'",node.name.lineno,node.name.pos)

        self.current_scope.insert(var_symbol)

    def visit_NodeVar(self, node):
        var_name = node.name.value
        var_symbol = self.current_scope.lookup(var_name, count=True)
        if var_symbol is None:
            self.error(f"Идентификатор не найден '{var_name}'", node.name.lineno,node.name.pos)

    # todo semantic chech on call and declaration params
    visit_NodeID = visit_NodeVar

    visit_NodeFunctionCall = visit_NodeVar

    def visit_list(self, node):
        for el in node:
            self.visit(el)

    def visit_Token(selfself, node):
        #print(node)
        pass

if __name__ == '__main__':
    with open("file.cpp", 'r', encoding='utf8') as f:
        parser_obj= parser.Parser(Lexer(f.read()))

    tree = parser_obj.parse()

    semantic_analyzer = SemanticAnalyzer(verbose=False)
    semantic_analyzer.visit(tree)
    print(f"Найдено семантических ошибок {semantic_analyzer.error_count}")
    for error in semantic_analyzer.errors:
        print(error)

    for _, scope in semantic_analyzer.scopes.items():
        print(scope)
