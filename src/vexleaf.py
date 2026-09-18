import sys

# src/vexleaf.py starter.vexleaf

if __name__=='__main__':
    if len(sys.argv)==1:
        while True:
            code_input=input()
            print(code_input)
    elif len(sys.argv)==2:
        while True:
            try:
                in_file=open(input(),'r')
                print(in_file)
            except:
                print("No file detected.")





