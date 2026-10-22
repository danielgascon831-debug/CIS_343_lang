import sys
import re
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
        return self.val
def DFA(buffer,line_num=0,next_char=""):
    is_string=False
    keywords = ["int", "if", 'else', 'return', 'while', 'for', 'string', 'class', 'import',
                'float', 'list', 'Block', 'list', 'array', 'inherits', 'break', 'continue']
    operators = ['>=', '>', '=', '==', '<', '<=', "!", "!=", '+', '-', "*", "/", "**", '++', '--','.',
                 '+=', '-=', '*=', '/=', ";","{","}",","]
    boolean_words = ['and', 'or', 'True', 'False']
    if re.fullmatch(r'\"[^"]*\"',buffer):
        return Token("string".upper(),buffer,buffer,line_num)
    if re.fullmatch(r"\"[^\"]*",buffer):
        return
    if buffer in operators:
        if re.fullmatch(r"[<>=+\-*/!][+\-*=]",buffer+next_char):
            return Token(buffer+next_char,buffer+next_char,None,line_num)
        return Token(buffer,buffer,None,line_num)
    if buffer=="(":
        return Token(buffer,buffer,None,line_num)
    if buffer==")":
        return Token(buffer,buffer,None,line_num)
    if buffer=="[":
        return Token(buffer,buffer,None,line_num)
    if buffer=="]":
        return Token(buffer,buffer,None,line_num)
    if re.fullmatch(r"\d+\.\d+\D",buffer+next_char):
        return Token('float'.upper(),buffer,float(buffer),line_num)
    if re.fullmatch(r"\d+[^\d.]",buffer+next_char):
        return Token('int'.upper(),buffer,int(buffer),line_num)
    if re.fullmatch(r"[_A-Za-z]\w*\W",buffer+next_char):
        if buffer in keywords or buffer in boolean_words:
            return Token(buffer, buffer, None, line_num)
        return Token('identifier'.upper(), buffer,buffer, line_num)
    return None






def scanner(source_code):
    line_num = 0
    try:
        token_list=[]
        is_comment=False
        start_cursor=0
        buffer=""
        for i in range(len(source_code)):
            buffer=source_code[start_cursor:i+1]
            if "\'\'\'" in buffer:
                is_comment=not(is_comment)
                start_cursor=i+1
                continue
            if source_code[i]=="\n":
                line_num+=1
                is_comment=False
                start_cursor=i+1
                continue
            if re.search(r"\s",buffer) and not(re.fullmatch(r"\"[^\"]*",buffer)):
                start_cursor=i+1
                continue
            if not is_comment:
                next_char = source_code[i + 1] if i + 1 < len(source_code) else " "
                token_state = DFA(buffer, line_num, next_char)
                if type(token_state)==Token:
                    token_list.append(token_state)
                    start_cursor=i+1+bool(re.fullmatch(r"[<>=+\-*/!][+\-*=]",token_state.type))
                    continue
        if re.fullmatch(r"\"[^\"]*[^\"]",buffer):
            return f"String from line {line_num} is {'not'.upper()} complete."

        return token_list

    except:
        return f"A lexeme error occured at line {line_num}."



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
def parser(expression):

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

            # The outer parentheses closed too early.
            if depth == 0 and i < len(expr) - 1:
                return False

        return depth == 0

    # Remove parentheses enclosing the entire expression.
    while has_outer_parentheses(expression):
        expression = expression[1:-1]

    # Parse from lowest precedence to highest.
    precedence = [
        ("binary", r"(?:==|!=|=)", True),
        ("binary", r"or", True),
        ("binary", r"and", True),
        ("binary", r"[><]=?", True),
        ("binary", r"[+\-]", True),
        ("binary", r"[*/]", True),

        # Unary signs bind less tightly than exponentiation.
        ("prefix", r"[-+]", False),

        ("binary", r"\*\*", False),

        # Logical negation binds tightly.
        ("prefix", r"!", False),
    ]

    for kind, pattern, rightmost in precedence:

        if kind == "binary":
            selection = find_break(expression,pattern,rightmost=rightmost)

            if selection is not None:
                return [parser(expression[:selection]),expression[selection],parser(expression[selection + 1:]) ]

        elif expression and re.fullmatch(pattern, expression[0].type):
            # Unary node: [operator, operand]
            return [expression[0],parser(expression[1:])]

    # Base case: a literal, identifier, or other single token.
    return expression
    #End AI patch of original parser submission.
def evaluation(parse_tree):
    if len(parse_tree)==3:
        operator=parse_tree[1]
        if operator=="=":
            parse_tree[0].val=parse_tree[2]
            return parse_tree[0].val
        if operator.type=="+":
            return parse_tree[0]+parse_tree[2]
        if operator.type=="-":
            return parse_tree[0]-parse_tree[2]
        if operator.type=="*":
            return parse_tree[0]*parse_tree[2]
        if operator.type=="/":
            return parse_tree[0]/parse_tree[2]
        if operator.type=="**":
            return parse_tree[0]**parse_tree[2]
        if operator=="<=":
            return parse_tree[0]<=parse_tree[2]
        if operator==">=":
            return parse_tree[0]>=parse_tree[2]
        if operator=="==":
            return parse_tree[0]==parse_tree[2]

    if len(parse_tree)==2:
        operator=parse_tree[0]
        if operator=="!":
            return not([parse_tree[1]])
        if operator=="-":
            return -1 * parse_tree[1]
    return parse_tree



if __name__=='__main__':
    if len(sys.argv)==1:
        while True:
            code_input=input()
            print(code_input)
    elif len(sys.argv)==2:
        while True:

            try:
                with open(sys.argv[1], "r", encoding="utf-8") as in_file:
                    source_tokens = scanner(in_file.read())



            except:
                print("No file detected.") 








