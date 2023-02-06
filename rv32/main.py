# Command line interface for risv-c simulator
#     version 1.0  with 9 instructions
#     20 Jan 2023
#     Li Keran

import rv32c   as rv      # cpu
import load32  as ld      # memory
from sys import argv

savePC = 0
ninst = 0                         # number of executed inst
MAXRUN = 10000                    # max simulation run

# print positive/negative 32-bit integer
def pr32(n):
    if( n < 2147483648 ):  # test positive number (32-bit)
        print(n,end="")
    else:
        print("-",(~n & 0x7FFFFFFF)+1,sep="",end="")

def show():  
    print("pc",savePC," ",end="")
    ld.pr_Current_instr()
    print("  ",end="")
    for i in range(1,11):
        print(" x",i,":",sep="",end="")
        pr32(rv.getR(i))
    print()
    
# -------------- monitor -----------------

def helpx():
    print("g - go")
    print("t - single step")
    print("d ads n - dump memory") 
    print("dis ads n - disassemble content in the memory") 
    print("r - show registers")
    print("s [xn,mn,pc] v - set [reg,mem,pc]")
    print("h - this help")
    print("q - quit")

def dumpR():
    print("  pc:",rv.getPC())
    for i in range(0,32):
        if( i%8 == 0):
            print()
        print("  x",i,":",sep="",end="")
        pr32(rv.getR(i))

def dumpMemory(ads,n):
    for i in range(ads,ads+n,4):
        print(i, ld.getMemory(i))
        
regname = ['x0','x1','x2','x3','x4','x5','x6','x7','x8','x9',
           'x10','x11','x12','x13','x14','x15','x16','x17','x18',
           'x19','x20','x21','x22','x23','x24','x25','x26','x27',
           'x28','x29','x30','x31']

def setvalue(cmd):
    a = cmd[1]
    v = int(cmd[2])
    if( a in regname ):
        i = int(a[1:])
        rv.setR(i,v)
    elif( a[0] == 'm' ):
        ld.setMemory(int(a[1:]),v)
    elif( a == "pc" ):
        rv.setPC(v)   
    else:
        print("set unknown")

# run one instruction
def runone():
    global savePC, ninst
    savePC = rv.getPC()
    rv.run()
    show()
    ninst += 1
    
def trace():
    while( 1 ):
        if( ninst > MAXRUN ):
            print("infinite loop")
            break
        else:
            runone()
            if(rv.checkNop()):       # stop at "nop"
                break
            
def interp():
    while(1):
        cmd = input(">").split()
        c = cmd[0]
        if( c == 'g'):
            trace()
        elif( c == 't'):
            runone()
        elif( c == 'r'):
            dumpR()
            print()
        elif( c == 'd'):
            dumpMemory(int(cmd[1]), int(cmd[2]))
            print()
        elif( c == 's'):
            setvalue(cmd)
        elif( c == 'h'):
            helpx()
        elif(c == 'dis'):
            ld.dumpAS(int(cmd[1]), int(cmd[2]))
        elif( c == 'q'):
            break
        else:
            print("unknown command")

# --------------------------------
  
def main():
    rv.setControl_vector()
    #inp = input("object file:").strip().split()
    script, obj_name = argv
    objfile = obj_name.strip().split()
    fname = objfile[0]
    ld.loadobj(fname)
#    ld.loadobj('add1-5.obj')
#    ld.loadobj('test.obj')
#    ld.dumpAS(0,9)   
    interp()

main()


