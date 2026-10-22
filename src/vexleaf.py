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







def find_break(expression,pattern):
    breaker=-1
    for i in expression:
        breaker+=1
        if re.search(pattern, i.type):
            return breaker
def parser(expression):
    if [x for x in expression if re.search(r"(={1,2})|(!=)",x.type)]:
        selection=find_break(expression,r"(={1,2})|(!=)")
        return [expression[:selection],expression[selection],expression[selection+1:]]
    if [x for x in expression if re.search(r"[><]=?",x.type)]:
        selection=find_break(expression,r"[><]=?")
        return [expression[:selection],expression[selection],expression[selection+1:]]
    if [x for x in expression if re.search(r"[+|\-]",x.type)]:
        selection=find_break(expression,r"[\+|\-]")
        return [expression[:selection],expression[selection],expression[selection+1:]]
    if [x for x in expression if re.search(r"[*/]",x.type)]:
        selection=find_break(expression,r"[><]=?")
        return [expression[:selection],expression[selection],expression[selection+1:]]
    if [x for x in expression if re.search(r"\*{2}",x.type)]:
        selection=find_break(expression,r"\*{2}")
        return [expression[:selection],expression[selection],expression[selection+1:]]

    return expression



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








