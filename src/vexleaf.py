import sys
import re
from operator import index

#Start AI patch 5.
# src/vexleaf.py starter.vexleaf
class Token():
    def __init__(self, type, lexeme,val=None,errors=None):
        self.__type=type
        self.__raw_input=lexeme
        self.__value=val
        self.__errors=errors
    @property
    def type(self):
        return self.__type
    @property
    def raw_input(self):
        return self.__raw_input
    @property
    def val(self):
        return self.__value
    @val.setter
    def val(self,new_val):
        self.__value=new_val
    @property
    def errors(self):
        return self.__errors
    def __str__(self):
        return str(self.val)


def DFA(buffer,line_num=0,next_char=""):
    """Classify one complete lexeme (with limited support for old DFA callers)."""
    keywords = [
        "int", "boolean", "if", "else", "return", "while", "print", "for",
        "string", "class", "import", "float", "list", "Block", "array",
        "inherits", "break", "continue"
    ]
    operators = [
        ">=", ">", "=", "==", "<", "<=", "!", "!=", "+", "-", "*", "/",
        "**", "++", "--", ".", "+=", "-=", "*=", "/=", ";", "{", "}",
        ",", "(", ")", "[", "]"
    ]

    # Keep compatibility with callers that pass an operator prefix and its
    # following character separately.
    if buffer in {"<", ">", "=", "+", "-", "*", "/", "!"}:
        combined = buffer + next_char
        if combined in operators and len(combined) > len(buffer):
            return Token(combined, combined, None, line_num)

    if re.fullmatch(r'"(?:\\.|[^"\\])*"', buffer):
        return Token("STRING", buffer, buffer[1:-1].replace(r'\"', '"').replace(r'\\', '\\'), line_num)
    if buffer.startswith('"'):
        return None

    if buffer in operators:
        return Token(buffer, buffer, None, line_num)

    if re.fullmatch(r"\d+\.\d+", buffer):
        return Token("FLOAT", buffer, float(buffer), line_num)
    if re.fullmatch(r"\d+", buffer):
        return Token("INT", buffer, int(buffer), line_num)

    if buffer in {"True", "False"}:
        return Token("BOOLEAN", buffer, buffer == "True", line_num)
    if buffer in {"and", "or"}:
        return Token(buffer, buffer, None, line_num)
    if buffer in keywords:
        return Token(buffer, buffer, None, line_num)
    if re.fullmatch(r"[_A-Za-z]\w*", buffer):
        return Token("IDENTIFIER", buffer, buffer, line_num)
    return None


def scanner(source_code):
    line_num = 0
    try:
        token_list=[]
        is_comment=False
        i=0
        operators = [
            ">=", "==", "<=", "!=", "**", "++", "--", "+=", "-=", "*=", "/=",
            ">", "=", "<", "!", "+", "-", "*", "/", ".", ";", "{", "}",
            ",", "(", ")", "[", "]"
        ]

        while i < len(source_code):
            if source_code.startswith("'''", i):
                is_comment = not is_comment
                i += 3
                continue
            if is_comment:
                if source_code[i] == "\n":
                    line_num += 1
                i += 1
                continue

            current = source_code[i]
            if current.isspace():
                if current == "\n":
                    line_num += 1
                i += 1
                continue

            if current == '"':
                start = i
                i += 1
                escaped = False
                while i < len(source_code):
                    char = source_code[i]
                    if char == "\n":
                        line_num += 1
                    if char == '"' and not escaped:
                        i += 1
                        break
                    if char == "\\" and not escaped:
                        escaped = True
                    else:
                        escaped = False
                    i += 1
                else:
                    return f"String from line {line_num} is NOT complete."
                lexeme = source_code[start:i]
                token = DFA(lexeme, line_num)
                if not isinstance(token, Token):
                    return f"A lexeme error occurred at line {line_num}."
                token_list.append(token)
                continue

            if current.isdigit():
                match = re.match(r"\d+(?:\.\d+)?", source_code[i:])
                lexeme = match.group(0)
                end = i + len(lexeme)
                # Reject malformed numeric continuations such as 12abc or 1.2.3.
                if end < len(source_code) and (source_code[end].isalpha() or source_code[end] == "_" or source_code[end] == "."):
                    return f"A lexeme error occurred at line {line_num}."
                token = DFA(lexeme, line_num)
                token_list.append(token)
                i = end
                continue

            if current.isalpha() or current == "_":
                match = re.match(r"[_A-Za-z]\w*", source_code[i:])
                lexeme = match.group(0)
                token = DFA(lexeme, line_num)
                if not isinstance(token, Token):
                    return f"A lexeme error occurred at line {line_num}."
                token_list.append(token)
                i += len(lexeme)
                continue

            matched_operator = next((op for op in operators if source_code.startswith(op, i)), None)
            if matched_operator is not None:
                token_list.append(Token(matched_operator, matched_operator, None, line_num))
                i += len(matched_operator)
                continue

            return f"A lexeme error occurred at line {line_num}."

        return token_list

    except Exception:
        return f"A lexeme error occurred at line {line_num}."


#start AI patch
def is_prefix_operator(expression, i):
    op = expression[i].type

    # Logical negation is a prefix operator.
    # The token "!=" is separate and remains binary.
    if op == "!":
        return True

    if op not in {"+", "-"}:
        return False

    # A sign at the beginning is unary.
    if i == 0:
        return True

    previous = expression[i - 1].type

    # These tokens indicate that an operand is expected next.
    return previous in {
        "(", "+", "-", "*", "/", "**",
        "=", "==", "!=", "<", "<=", ">", ">=",
        "and", "or", "!", ",",
        "+=", "-=", "*=", "/="
    }
#end AI patch.


def find_break(expression, pattern, rightmost=True):
    depth = 0
    matches = []

    for i, token in enumerate(expression):
        if token.type == "(":
            depth += 1
            continue

        if token.type == ")":
            depth -= 1
            continue

        if depth != 0:
            continue

        if not re.fullmatch(pattern, token.type):
            continue

        # Don't treat unary signs as binary operators.
        if token.type in {"+", "-"}:
            if is_prefix_operator(expression, i):
                continue

        matches.append(i)

    if not matches:
        return None

    return matches[-1] if rightmost else matches[0]
#end AI patch


def parser(expression,var_stack=0):
    if not isinstance(var_stack,Var_Stack):
        var_stack=Var_Stack()

    if isinstance(expression, Token):
        expression = [expression]
    if not isinstance(expression, (list, tuple)):
        return expression
    expression = list(expression)

    def has_outer_parentheses(expr):
        if (
            len(expr) < 2
            or expr[0].type != "("
            or expr[-1].type != ")"
        ):
            return False

        depth = 0
        for i, token in enumerate(expr):
            if token.type == "(":
                depth += 1
            elif token.type == ")":
                depth -= 1
            if depth < 0:
                raise SyntaxError("Unmatched closing parenthesis.")
            # The outer parentheses closed too early.
            if depth == 0 and i < len(expr) - 1:
                return False
        return depth == 0

    # Remove parentheses enclosing the entire expression.
    while has_outer_parentheses(expression):
        expression = expression[1:-1]

    if not expression:
        raise SyntaxError("An expression cannot be empty.")

    # Parse from lowest precedence to highest. Binary operators are split at
    # the rightmost occurrence for left associativity; exponentiation is right
    # associative. Recursive calls retain the same variable stack.
    precedence = [
        ("binary", r"(=)", True),
        ("binary", r"(?:==|!=)", True),
        ("binary", r"or", True),
        ("binary", r"and", True),
        ("binary", r"(?:<=|>=|<|>)", True),
        ("binary", r"[+\-]", True),
        ("binary", r"[*/]", True),
        # Unary signs bind less tightly than exponentiation.
        ("prefix", r"[-+]", False),
        ("binary", r"\*\*", False),
        # Logical negation binds tightly.
        ("prefix", r"!", False)
    ]

    for kind, pattern, rightmost in precedence:
        if kind == "binary":
            selection = find_break(expression,pattern,rightmost=rightmost)
            if selection is not None:
                if selection == 0 or selection == len(expression) - 1:
                    raise SyntaxError("Missing operand for operator.")
                return [
                    parser(expression[:selection],var_stack),
                    expression[selection],
                    parser(expression[selection + 1:],var_stack)
                ]
        elif expression and re.fullmatch(pattern,expression[0].type):
            if len(expression) == 1:
                raise SyntaxError("Missing operand for prefix operator.")
            # Unary node: [operator, operand]
            return [expression[0],parser(expression[1:],var_stack)]

    # Resolve identifiers by their lexeme, not by the token category.
    if len(expression) == 1:
        token = expression[0]
        if token.type == "IDENTIFIER":
            return var_stack.access(token.raw_input)
        if token.type in {"INT", "FLOAT", "STRING", "BOOLEAN", "Boolean"}:
            return token.val
        raise SyntaxError(f"Unexpected token {token.raw_input!r} in expression.")

    raise SyntaxError("Could not parse expression.")
    #End AI patch of original parser submission.


def evaluation(parse_tree):
    try:
        if isinstance(parse_tree, Token):
            return parse_tree.val

        if not isinstance(parse_tree, (list, tuple)):
            return parse_tree

        if len(parse_tree)==3:
            operator=parse_tree[1]
            op = operator.type if isinstance(operator, Token) else operator
            if op == "+":
                return evaluation(parse_tree[0])+evaluation(parse_tree[2])
            if op == "-":
                return evaluation(parse_tree[0])-evaluation(parse_tree[2])
            if op == "*":
                return evaluation(parse_tree[0])*evaluation(parse_tree[2])
            if op == "/":
                return evaluation(parse_tree[0])/evaluation(parse_tree[2])
            if op == "**":
                return evaluation(parse_tree[0])**evaluation(parse_tree[2])
            if op == "<=":
                return evaluation(parse_tree[0])<=evaluation(parse_tree[2])
            if op == ">=":
                return evaluation(parse_tree[0])>=evaluation(parse_tree[2])
            if op == ">":
                return evaluation(parse_tree[0])>evaluation(parse_tree[2])
            if op == "<":
                return evaluation(parse_tree[0])<evaluation(parse_tree[2])
            if op == "==":
                return evaluation(parse_tree[0])==evaluation(parse_tree[2])
            if op == "!=":
                return evaluation(parse_tree[0])!=evaluation(parse_tree[2])
            if op == "and":
                return bool(evaluation(parse_tree[0])) and bool(evaluation(parse_tree[2]))
            if op == "or":
                return bool(evaluation(parse_tree[0])) or bool(evaluation(parse_tree[2]))
            if op == "=":
                raise ValueError("Assignment is a statement, not an expression.")

        if len(parse_tree)==2:
            operator=parse_tree[0]
            op = operator.type if isinstance(operator, Token) else operator
            if op == "!":
                return not bool(evaluation(parse_tree[1]))
            if op == "-":
                return -evaluation(parse_tree[1])
            if op == "+":
                return +evaluation(parse_tree[1])

        raise ValueError("Invalid parse tree.")
    except Exception:
        return "Failed to evaluate."


def print_run(statement):
    print(statement)


class Var_Stack:
    def __init__(self):
        self.__float_var_stack=[{}]
        self.__int_var_stack=[{}]
        self.__string_var_stack=[{}]
        self.__bool_var_stack=[{}]
        # Type indices intentionally follow the language's declaration order:
        # int=0, boolean=1, float=2, string=3.
        self.__var_list=[ self.__int_var_stack, self.__bool_var_stack,self.__float_var_stack,self.__string_var_stack]

    def push(self):
       self.__int_var_stack.append({})
       self.__float_var_stack.append({})
       self.__string_var_stack.append({})
       self.__bool_var_stack.append({})

    def declare(self,name,type=0,val=None):
        type_names = {"int": 0, "integer": 0, "boolean": 1, "bool": 1, "float": 2, "string": 3}
        if isinstance(name, Token):
            name = name.raw_input
        if not isinstance(name, str) or not name:
            raise ValueError("A variable must have a non-empty name.")
        if isinstance(type, str):
            type = type_names.get(type.lower(), -1)
        if not isinstance(type, int) or type < 0 or type >= len(self.__var_list):
            raise ValueError("Unknown variable type.")
        if isinstance(val, Token):
            val = val.val

        # Redeclaration replaces a binding only in the current block.
        for stack in self.__var_list:
            stack[-1].pop(name, None)

        if type == 3:  # String
            if val is None:
                converted = ""
            else:
                converted = str(val)
                if len(converted) >= 2 and converted[0] == '"' and converted[-1] == '"':
                    converted = converted[1:-1]
            self.__string_var_stack[-1][name] = converted
            return converted

        if type == 2:  # Float
            try:
                converted = 0.0 if val is None else float(val)
            except (TypeError, ValueError):
                converted = 0.0
            self.__float_var_stack[-1][name] = converted
            return converted

        if type == 1:  # Boolean
            if isinstance(val, str):
                normalized = val.strip().lower()
                if normalized in {"true", "1"}:
                    converted = True
                elif normalized in {"false", "0", ""}:
                    converted = False
                else:
                    converted = bool(val)
            else:
                converted = bool(val) if val is not None else False
            self.__bool_var_stack[-1][name] = converted
            return converted

        # Integer
        try:
            converted = 0 if val is None else int(val)
        except (TypeError, ValueError, OverflowError):
            converted = 0
        self.__int_var_stack[-1][name] = converted
        return converted

    def is_empty(self):
       return not any(scope for stack in self.__var_list for scope in stack)

    def pull(self):
        if len(self.__int_var_stack) == 1:
            raise IndexError("Cannot remove the global variable scope.")
        # Pop all four type dictionaries from the same lexical scope.
        return [stack.pop() for stack in self.__var_list]

    def access(self,name):
        # Search innermost-to-outermost scope first, then the type maps within
        # that scope. This preserves shadowing even when a variable changes type.
        for scope_index in range(len(self.__int_var_stack)-1, -1, -1):
            for stack in self.__var_list:
                if name in stack[scope_index]:
                    return stack[scope_index][name]
        raise NameError(f"Within this stack of blocks, variable {name} has not been declared.")

    def change(self,name,new_val,type=0):
        type_names = {"int": 0, "integer": 0, "boolean": 1, "bool": 1, "float": 2, "string": 3}
        requested_type = type_names.get(type.lower(), -1) if isinstance(type, str) else type
        if not isinstance(requested_type, int) or requested_type < 0 or requested_type >= len(self.__var_list):
            raise ValueError("Unknown variable type.")
        if isinstance(new_val, Token):
            new_val = new_val.val

        for scope_index in range(len(self.__int_var_stack)-1, -1, -1):
            for type_index, stack in enumerate(self.__var_list):
                if name not in stack[scope_index]:
                    continue
                # type=0 is also the historical default argument, so it means
                # infer the existing variable type; an explicit nonzero type
                # can still be used to validate the requested destination.
                if requested_type != 0 and requested_type != type_index:
                    continue

                if type_index == 0:
                    try:
                        converted = int(new_val)
                    except (TypeError, ValueError, OverflowError):
                        raise ValueError(f"Cannot assign {new_val!r} to integer variable {name}.")
                elif type_index == 1:
                    if isinstance(new_val, str):
                        normalized = new_val.strip().lower()
                        if normalized in {"true", "1"}:
                            converted = True
                        elif normalized in {"false", "0", ""}:
                            converted = False
                        else:
                            converted = bool(new_val)
                    else:
                        converted = bool(new_val)
                elif type_index == 2:
                    try:
                        converted = float(new_val)
                    except (TypeError, ValueError, OverflowError):
                        raise ValueError(f"Cannot assign {new_val!r} to float variable {name}.")
                else:
                    converted = str(new_val)
                    if len(converted) >= 2 and converted[0] == '"' and converted[-1] == '"':
                        converted = converted[1:-1]

                stack[scope_index][name] = converted
                return 0

        raise NameError(f"Within this stack of blocks, variable {name} has not been declared.")


if __name__=='__main__':
    if len(sys.argv) != 2:
        print("Usage: python vexleaf.py <source-file>")
        sys.exit(1)

    try:
        with open(sys.argv[1], "r", encoding="utf-8") as in_file:
            source_tokens = scanner(in_file.read())
    except OSError as error:
        print(f"Could not open source file: {error}")
        sys.exit(1)

    if isinstance(source_tokens, str):
        print(source_tokens)
        sys.exit(1)

    var_hold=Var_Stack()
    i=0
    declaration_types = {"int": 0, "boolean": 1, "float": 2, "string": 3}

    while i < len(source_tokens):
        current = source_tokens[i]

        if current.type == ";":
            i += 1
            continue

        if current.type == "print":
            i += 1
            expression_tokens=[]
            while i < len(source_tokens) and source_tokens[i].type != ";":
                expression_tokens.append(source_tokens[i])
                i += 1
            if i >= len(source_tokens):
                print("Failed to close statement.")
                sys.exit(1)
            print_run(evaluation(parser(expression_tokens,var_hold)))
            i += 1
            continue

        if current.type in declaration_types:
            declared_type = declaration_types[current.type]
            i += 1
            if i >= len(source_tokens) or source_tokens[i].type != "IDENTIFIER":
                print(f"Expected a variable name after {current.raw_input}.")
                sys.exit(1)
            variable_name = source_tokens[i].raw_input
            i += 1
            initial_value = None
            if i < len(source_tokens) and source_tokens[i].type == "=":
                i += 1
                expression_tokens=[]
                while i < len(source_tokens) and source_tokens[i].type != ";":
                    expression_tokens.append(source_tokens[i])
                    i += 1
                if not expression_tokens:
                    print(f"Missing initial value for {variable_name}.")
                    sys.exit(1)
                initial_value = evaluation(parser(expression_tokens,var_hold))
            else:
                while i < len(source_tokens) and source_tokens[i].type != ";":
                    print(f"Unexpected token {source_tokens[i].raw_input!r} in declaration.")
                    sys.exit(1)
            if i >= len(source_tokens):
                print("Failed to close statement.")
                sys.exit(1)
            var_hold.declare(variable_name,declared_type,initial_value)
            i += 1
            continue
        if current.type == "{":
            var_hold.push()
            continue
        if current.type=="}":
            var_hold.pull()

        if current.type == "IDENTIFIER":
            variable_name = current.raw_input
            i += 1
            if i >= len(source_tokens) or source_tokens[i].type not in {"=", "+=", "-=", "*=", "/="}:
                print(f"Expected an assignment after variable {variable_name}.")
                sys.exit(1)
            assignment_operator = source_tokens[i].type
            i += 1
            expression_tokens=[]
            while i < len(source_tokens) and source_tokens[i].type != ";":
                expression_tokens.append(source_tokens[i])
                i += 1
            if i >= len(source_tokens):
                print("Failed to close statement.")
                sys.exit(1)
            if not expression_tokens:
                print(f"Missing assigned value for {variable_name}.")
                sys.exit(1)
            new_value = evaluation(parser(expression_tokens,var_hold))
            if new_value == "Failed to evaluate.":
                print(new_value)
                sys.exit(1)
            if assignment_operator != "=":
                old_value = var_hold.access(variable_name)
                if assignment_operator == "+=":
                    new_value = old_value + new_value
                elif assignment_operator == "-=":
                    new_value = old_value - new_value
                elif assignment_operator == "*=":
                    new_value = old_value * new_value
                elif assignment_operator == "/=":
                    new_value = old_value / new_value
            var_hold.change(variable_name,new_value)
            i += 1
            continue

        print(f"Unexpected token {current.raw_input!r}.")
        sys.exit(1)
        #End AI patch of code made for lab 5.
