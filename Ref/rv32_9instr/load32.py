# riscv32 sim, loader,  load32.py
#     version 1.0  with 9 instructions
#     18 Feb 2022
#     Prabhas Chongstitvatana

# export
#   setM(), getM(), decode(),
#   getOp(), getIm(), getIm_B(), getIm_S
#   loadobj(), prCurrentOp()

import array

op = 0      # various field of an instruction
rd = 0
f3 = 0
rs1 = 0
rs2 = 0
f7 = 0
imm = 0

MAXMEM = 1000

M = array.array('L',[0]*MAXMEM)     # memory size MAXMEM

def setM(ads,v):                    # internal address is word
    a = ads>>2
    if(a < MAXMEM):
        M[a] = v
    else:
        print("access M out of bound")

def getM(ads):
    a = ads>>2
    if(a < MAXMEM):
        return M[a]
    else:
        print("access M out of bound")
        return 0

hexdigit = "0123456789ABCDEF"

# x is a string of hex 8 digits (32 bits)
def hextodec(x):
    b16 = 16**7
    n = hexdigit.index(x[-1])  # last digit
    for d in x[:-1]:   # except the last digit
        n += hexdigit.index(d) * b16
        b16 = b16 // 16
    return n
        
def decode(c):
    global op,rd,f3,rs1,rs2,f7,imm
    
    op = c & 127
    rd = (c >> 7) & 31
    f3 = (c >> 12) & 7
    rs1 = (c >> 15) & 31
    rs2 = (c >> 20) & 31
    f7 = c >> 25
    imm = c >> 20

opstr = ['nop','add','sub','addi','lw','sw','beq','bne','blt','bge','and']

def prOp(op2):
    print(opstr[op2],end=" ")     

# encode instruction into internal code 0..9
def encodeOpx(op2,xf3,xf7):
    if( op2 == 51 and xf3 == 0):
        if(xf7 == 0):
            return 1
        elif(xf7 == 32):
            return 2
    elif(op2 == 19 and xf3 == 0):
        return 3
    elif(op2 == 3 and xf3 == 2):
        return 4
    elif(op2 == 35 and xf3 == 2):
        return 5
    elif(op2 == 99):
        if(xf3 == 0):
            return 6
        elif(xf3 == 1):
            return 7
        elif(xf3 == 4):
            return 8
        elif(xf3 == 5):
            return 9
    elif(op2 == 51 and xf3 == 7 and xf7 == 0):   # and x2,x3,x4
        return 10
    return 0

# def signx12(x):          # sign extension 12 bits
#     if( x & 0x0800 ):
#         return x | 0x0FFFFF000
#     return x

# must decode() first
# return tuple of opx with rd, rs1, rs2
def getOp():
    op2 = encodeOpx(op,f3,f7)
    return (op2,rd,rs1,rs2)

# must decode() first
def getIm():
    return imm          # sign is already extended

# must decode() first
#  extract offset S-type format for store word instruction
def getIm_S():
    return (f7<<5) + rd    # positive integer [check further]

# must decode() first
#  extract offset B-type format for branch instructions

# it is a bit complicate, took me 3 hours to get it right
def getIm_B():
    s11 = 0
    if((rd & 1) != 0):
        s11 = 0x0800       # bit[11] is 1

    # offset is 13-bit; s12 : s11: s10..5 : s4..1 : 0
    # f7 is 7-bit, s12 is f7[6] (sign)
    # s11 is rd[0]   (1-bit)
    # s10..5 is f7[5:0] (6-bit)  (hence f7 & 63) 
    # s4..1 is rd[4..1] (4-bit)
    # last bit is 0 (hence rd & 30)
    
    m = s11 | ((f7 & 63) << 5) | (rd & 30)
    if( (f7 & 0x040) != 0 ):     # negative, test bit[6] of f7
        return m - 4096          # make it negative (13-bit)
    return m 

def loadobj(fname):
    f = open(fname,"r")
    fx = f.readlines()
    a = 0
    for line in fx:
        lx = line.split()
        M[a] = hextodec(lx[0][2:])
        a += 1
    f.close()
    print("load program, last address ",a)
    
# print op follow by values of fields, similar to textbook (opcode last) 
def disassem(c):
    decode(c)
    prOp(encodeOpx(op,f3,f7))
    if( op in [51,99] ):
        print(f7,rs2, end=" ")
    elif( op in [3,19,35]):
        print(imm, end=" ")
    print(rs1, f3, rd, op)

# disassemble a range of memory
def dumpAS(ads,n):
    for i in range(ads,ads+n):
        disassem(M[i])
   
# print three registers
def pr3R(rd,rs1,rs2):
    print('x',rd," ",'x',rs1," ",'x',rs2,sep="",end="")

# print two registers and immediate
def prI(rd,rs1,im):
    print('x',rd," ",'x',rs1," ",im,sep="",end="")
    
# print load/store  op x1 8(x2)
def prLS(r,base,im):
    print('x',r," ",im,'(x',base,')',sep="",end="")
    
# print B-type
def prB(rs1,rs2,im):
    print('x',rs1," ",'x',rs2," ",im,sep="",end="")
    
# call decode() first
def prCurrentOp():
    op2 = encodeOpx(op,f3,f7)
    prOp(op2)
    if(op2 in [1,2,10]):           # add, sub, and
        pr3R(rd,rs1,rs2)
    elif(op2 == 3):             # addi
        prI(rd,rs1,imm)
    elif(op2 == 4):             # lw
        prLS(rd,rs1,imm)
    elif(op2 == 5):             # sw
        prLS(rs2,rs1,getIm_S())
    elif(op2 in [6,7,8,9]):     # branch
        prB(rs1,rs2,getIm_B())
    
#loadobj("test.obj")
#dumpM(0,9)
#dumpAS(0,9)




