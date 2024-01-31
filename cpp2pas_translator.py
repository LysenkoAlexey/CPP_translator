import re
import typing

import parser
import lexer
import semantic_analyzer as san

builtins_translate = {'float': 'real',
                      'int': 'integer',
                      'char': 'char',
                      'bool': 'boolean',
                      'string': 'string',
                      }
operators_translate = {'==': '=',
                       '&&': 'and',
                       '||': 'or'
                       }


class SourceToSourceTranslator(san.NodeVisitor):
    def __init__(self, sym_table_scopes, optimize=False):
        self.current_scope = None
        self.output = None
        self._sym_table_scopes = sym_table_scopes
        self._optimize = optimize
        self.log: typing.List[str]
        self.log = []

    def output_clean(self):
        # dirty hack, but working
        self.output = re.sub(r'end;([\s,\n]+)else', r'end\1else', self.output)

    def generic_visit(self, node):
        if isinstance(node, parser.Node):
            result = []
            for field in node._fields:
                result.append(self.visit(getattr(node, field)))
            return '\n'.join(result)
        else:
            raise Exception('No visit_{} method'.format(type(node).__name__))

    def visit_NodeBlock(self, node: parser.NodeBlock):

        result_str = 'begin\n'
        results=[]
        for el in node.children:
            result = self.visit(el)
            if result:
                results.extend(result.splitlines())

        result_str += '\n'.join('   ' + line for line in results)
        result_str +=  '\nend'
        return result_str

        # return '\n'.join('   ' + line for line in results)

    def visit_NodeProgram(self, node):
        program_name = 'translated'
        result_str = f'program {program_name};\n'

        global_scope = self._sym_table_scopes['global']
        self.current_scope = global_scope

        # looking for variable declaration in main
        self.current_scope = self._sym_table_scopes['main']
        result_str += self.get_var_section_text()

        self.current_scope = global_scope
        # first visit subtree, looking only for nested functions
        for func in node.block:
            if isinstance(func, parser.NodeFunction):
                if func.name.value != 'main':
                    content = self.visit(func)
                    if content:
                        result_str += '\n'.join('   ' + line for line in content.splitlines())

        # second  visit subtree looking for main to make it program body
        # result_str += 'begin\n'
        result_str += '\n'
        for func in node.block:
            if isinstance(func, parser.NodeFunction):
                if func.name.value == 'main':
                    block = self.visit(func)
                    if block:
                        result_str += '\n'.join('' + line for line in block.splitlines())
                    break
        result_str += '.'
        result_str += ' {END OF %s}' % program_name
        self.output = result_str

        self.current_scope = self.current_scope.enclosing_scope

    def get_var_section_text(self):
        # making var section
        var_str = []
        record: san.VarSymbol
        for name, record in self.current_scope._symbols.items():
            if isinstance(record, san.VarSymbol):
                if self._optimize:
                    if record.hit_count < 1:
                        self.log.append(
                            '*' * 20 + f"removed: Unused variable declaration '{name}'" \
                            + f" in scope '{self.current_scope.scope_name}' ")
                    else:
                        var_str.append(
                            f'var {record.name}: {builtins_translate.get(record.type.name, record.type.name)};')

                else:
                    var_str.append(
                        f'var {record.name}: {builtins_translate.get(record.type.name, record.type.name)};')
        if var_str:
            return '\n'.join(var_str)
        else:
            return ''

    def visit_main(self, node):
        # Scope for parameters and local variables
        func_name = func_name = node.name.value
        func_scope = self._sym_table_scopes[func_name]
        self.current_scope = func_scope
        result_str = ''
        # result_str += self.get_var_section_text()
        block = self.visit(node.block)
        if block:
            result_str = '\n'.join(line for line in block.splitlines())
        # result_str += '' # ; не нужен перед последним end.

        self.current_scope = self.current_scope.enclosing_scope
        return result_str

    def visit_NodeFunction(self, node: parser.NodeFunction):
        func_name = node.name.value
        if func_name == 'main':
            return self.visit_main(node)  # special case

        result_str = '\n'
        ret_type = node.ret_type.value
        if ret_type == 'void':
            result_str += f'procedure {func_name}'
        else:
            result_str += f'function {func_name}'

        # Scope for parameters and local variables
        func_scope = self._sym_table_scopes[func_name]
        self.current_scope = func_scope

        # function/procedure formal parameters
        result_str += '('
        if node.formal_params.params:
            formal_params = []
            for param in node.formal_params.params:
                param_type = self.current_scope.lookup(param.type.value)
                param_name = param.name.value
                formal_params.append(
                    '%s : %s' % (param_name, builtins_translate.get(param_type.name, param_type.name))
                )
            result_str += '; '.join(formal_params)
            #    if node.formal_params.params:
        result_str += ')'
        # if not procedure set output type
        if ret_type != 'void':
            result_str += f':{builtins_translate.get(ret_type, ret_type)}'
        result_str += ';'
        result_str += '\n'
        # filling var section
        result_str += self.get_var_section_text()

        # first visit subtree, looking only for nested functions
        for func in node.block.children:
            if isinstance(func, parser.NodeFunction):
                content = self.visit(func)
                if content:
                    result_str += '\n'.join('   ' + line for line in content.splitlines())
                result_str += '\n'

        result_str += 'begin\n'
        for non_func in node.block.children:

            if (not isinstance(func, parser.NodeFunction)) and (not isinstance(func, parser.NodeDeclaration)):
                content = self.visit(non_func)
                if content:
                    result_str += '\n'.join('   ' + line for line in content.splitlines())

        result_str += '\nend'
        result_str += f'; {{END OF {func_name}}}'
        result_str += '\n'

        # indent function text
        # result_str = '\n'.join('   ' + line for line in result_str.splitlines())

        self.current_scope = self.current_scope.enclosing_scope

        return result_str

    def visit_NodeDeclaration(self, node):

        return None  # no need to something special, all check must be made in semantic analyzer

    def visit_NodeAssigning(self, node):
        t2 = self.visit(node.right_side)
        t1 = self.visit(node.left_side)
        return '%s %s %s;' % (t1, ':=', t2)

    def visit_NodeBinaryOperator(self, node: parser.NodeBinaryOperator):
        t1 = self.visit(node.left)
        t2 = self.visit(node.right)
        op = operators_translate.get(node.op.value, node.op.value)
        if op in {'and', 'or', '=', '<', '>', '<=', '>='}:
            return '(%s %s %s)' % (t1, op, t2)
        else:
            return '%s %s %s' % (t1, op, t2)

    def visit_NodeIfConstruction(self, node: parser.NodeIfConstruction):
        match node.__class__:
            case parser.NodeIfConstruction:
                op = 'if'
                block_begin = 'then'
            case parser.NodeWhileConstruction:
                op = 'while'
                block_begin = 'do'
            case parser.NodeElseBlock:
                op = 'else'
                block_begin = ''
        if op == 'else':
            condition = ''
        else:
            condition = self.visit(node.condition)
        result_str = f'{op} {condition} {block_begin}\n'

        block = self.visit(node.block)
        if block:
            result_str += '\n'.join('' + line for line in block.splitlines())
        # block = self.visit(node.block)
        # result_str += block + ';'
        result_str += ';'
        return result_str

    visit_NodeWhileConstruction = visit_NodeIfConstruction
    visit_NodeElseBlock = visit_NodeIfConstruction

    def visit_NodeVar(self, node):
        return f'{node.name.value}'

        var_name = node.name.value
        var_symbol = self.current_scope.lookup(var_name)
        if var_symbol is None:
            raise Exception(
                "Error: Symbol(identifier) not found '%s'" % var_name
            )
        scope_level = str(var_symbol.scope.scope_level)
        return '<%s:%s>' % (var_name + scope_level, var_symbol.type.name)

    # visit_NodeFunctionCall = visit_NodeVar

    def visit_NodeCin(self, node: parser.NodeCin):
        var_name = node.variables[0].name.value
        return f'readln({var_name});'

    def visit_NodeCout(self, node: parser.NodeCout):
        result = []
        for el in node.variables:
            if isinstance(el, parser.NodeID):
                result.append(self.visit(el.name))
            else:
                result.append(self.visit(el.value))
        return f'writeln({", ".join(result)});'
        # return f'writeln({", ".join(el.name.value for el in node.variables)});'

    def visit_NodeReturnStatement(self, node: parser.NodeReturnStatement):
        return f'Exit({self.visit(node.expression)});'

    def visit_NodeComment(self, node: parser.NodeComment):
        return f"{{{node.comment.value}}}"

    def visit_list(self, node):
        result = []
        for el in node:
            text = self.visit(el);
            if text:
                result.append(text)
        return '\n'.join(result)

    def visit_Token(selfself, node: lexer.Token):
        # print(node)
        if node.name in {lexer.Token.STRING_LITERAL_1, lexer.Token.STRING_LITERAL_2}:
            return f"'{node.value}'"
        return f'{node.value}'


def process_file(filename, *, verbose=False, optimize=True) -> SourceToSourceTranslator:
    with open(filename, 'r', encoding='utf8') as f:
        parser_obj = parser.Parser(lexer.Lexer(f.read()))
        tree = parser_obj.parse()
        semantic_analyzer = san.SemanticAnalyzer(verbose=verbose)
        semantic_analyzer.visit(tree)
        source_translator = SourceToSourceTranslator(semantic_analyzer.scopes, optimize=optimize)
        source_translator.visit(tree)
        source_translator.output_clean()
        return source_translator, semantic_analyzer


if __name__ == '__main__':
    semntc_ananlyzer: san.SemanticAnalyzer
    src_translator, semntc_ananlyzer = process_file("file.cpp", verbose=True, optimize=True)
    if semntc_ananlyzer.error_count:
        print('\n'.join([error for error in semntc_ananlyzer.errors]))

    print(src_translator._sym_table_scopes)
    # with open('translated.pas', 'w', encoding='utf8') as wf:
    #    wf.write(src_translator.output)
    print(src_translator.output)
