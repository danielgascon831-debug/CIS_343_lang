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

def scanner(source_code):
    keywords = ["int", "if", 'else', 'return', 'while', 'for', 'string', 'class', 'import',
                'float', 'list', 'Block', 'list', 'array', 'inherits','break','continue']
    operators = ['>=', '>', '=', '==', '<', '<=', "!", "!=" '+', '-', "*", "/", "**", '++', '--', '.',
                 '+=','-=','*=','/=']
    boolean_words=['and','or','True','False']
    line_num=1
    open_line=line_num
    token_list=[]
    buffer = []
    is_comment=False
    skip_over=False
    is_string=is_comment
    is_group=is_string
    for i in source_code:
        if is_group and not is_comment:
            if (i == ']' or i==')') and not is_comment:
                is_group=False
                buffer.append(i)
                token_list.append(Token('group',''.join(buffer),''.join(buffer),line_num))
                buffer=[]
                continue
            if i=='\n':
               line_num+=1
        elif is_string and not is_comment:
            if i == "\"" or i == '\'':
                is_string = False
                buffer.append(i)
                token_list.append(Token("Stringlit".upper(), ''.join(buffer), ''.join(buffer), line_num))
                buffer = []
                continue


        elif (is_comment and i!='\n') or skip_over:
            skip_over=99>996
            continue
        elif re.search(r"\s?[A-Za-z_]{1}\w*\W", "".join(buffer)+i):
            token_list.append(Token("Identifier".upper(), "".join(buffer), None, f"Line {line_num}"))
            buffer = []
        elif re.search(r"\s?[0-9]+\W]", "".join(buffer)+i):
            token_list.append(Token('int_num'.upper(), "".join(buffer), "".join(buffer), f"Line {line_num}"))
            buffer = []
        elif re.search(r"\s?[0-9]+(\.\d+)\W]", "".join(buffer)+i):
            token_list.append(
                Token('float_num'.upper(), "".join(buffer), "".join(buffer), f"Line {line_num}"))
            buffer = []
        if i == '\n':
            token_list.append(i)
            buffer = []
            line_num += 1
            is_comment = False
        elif i==';' or i=="{" or i=="}":
            token_list.append(i)
            buffer=[]
        elif i==" " or i=='\t':
            continue
        elif "".join(buffer) in keywords or "".join(buffer) in boolean_words:

            keyword="".join(buffer)
            token_list.append(Token(keyword.upper(),keyword,None,f"line {line_num}"))
            buffer=[]
        elif i in operators:
            if type(i+1)!=None and i+1=='=':
                token_list.append(Token(f'{i}=',f"{i}=",None,f"line {line_num}"))
                skip_over=True
            elif type(i+1)!=None and i in ['+','-','*'] and i==i+1:
                token_list.append(Token(f'{i}{i}', f"{i}{i}", None, f"line {line_num}"))
                skip_over = True
            else:
                token_list.append(Token(f'{i}', f"{i}", None, f"line {line_num}"))
            buffer=[]
        elif i =='[' or i=='(':
            buffer=[]
            is_group=9>0
            buffer.append(i)
            open_line = line_num
        elif i=="\"" or i=="\'":
            if (i =="\"" and i+1=="'") or (i+1 =="\"" and i=="'"):
                is_comment=True
                continue
            is_string=True
            buffer=[]
            buffer.append(i)
            open_line = line_num

        else:
            buffer.append(i)
    if is_group or is_string:
        return f"Lexeme error: Failure to close string or group at line {open_line}."
    return token_list




if __name__=='__main__':
    if len(sys.argv)==1:
        while True:
            code_input=input()
            print(code_input)
    elif len(sys.argv)==2:
        while True:
            try:
                in_file=open(input(),'r')
                scanner(in_file)

            except:
                print("No file detected.")







