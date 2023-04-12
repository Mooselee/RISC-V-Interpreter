# riscv32 sim, loader,  load32.py
#     version 1.0  with 9 instructions
#     20 Jan 2023
#     Li Keran

# export
#   setM(), getM(), decode(),
#   getOp(), getIm(), getIm_B(), getIm_S
#   loadobj(), prCurrentOp()

'''
Instructions supported:
R-type: add, sub, and
I-type: addi, lw,
S-type: sw,
B-type: beq, bne, blt, bge,
U-type:
J-type:
'''

import array

op = 0      # various field of an instruction
rd = 0
f3 = 0
rs1 = 0
rs2 = 0
f7 = 0
imm = 0

opcode_lui = 55 # U: 0110111
opcode_auipc = 23 # U: 0010111
opcode_jal =111 # J: 1101111
opcode_jalr = 103 # J: 1100111
opcode_branch = 99 # B: 1100011
opcode_load = 3 # I: 0000011
opcode_store = 35 # S: 0100011
opcode_alui = 19 # I: 0010011
opcode_alur = 51 # R: 0110011
opcode_fence = 15 # I: 0001111
opcode_system = 115 #I: 1110011


MAXMEM = 1000
Memory = array.array('L',[0]*MAXMEM)     # memory size MAXMEM

def setMemory(ads,v):                    # internal address is word, divide ads by 4, which equals to >>2
    a = ads>>2
    if(a < MAXMEM):
        Memory[a] = v
    else:
        print("access Memory out of bound")

def getMemory(ads):
    a = ads>>2
    if(a < MAXMEM):
        return Memory[a]
    else:
        print("access Memory out of bound")
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
    
    op = c & 127 # [6:0]
    rd = (c >> 7) & 31 # [11:7]
    f3 = (c >> 12) & 7 # [14:12]
    rs1 = (c >> 15) & 31 # [19:15]
    rs2 = (c >> 20) & 31 # [24:20]
    f7 = c >> 25
    imm = c >> 20

# opstr = ['nop','add','sub','addi','lw','sw','beq','bne','blt','bge','and']
opstr = {
        'R':['add','sub','sll','slt','sltu','xor','srl','sra','or','and'],
        'I':['jalr','lb','lh','lw','lbu','lhu','addi','slti','sltiu','xori','ori','andi','slli','srli','srai','fence','ecall','ebreak','csrrw','csrrs','csrrc','csrrwi','cssrrsi','csrrci'],
        'S':['sb','sh','sw'],
        'B':['beq','bne','blt','bge','bltu','bgeu'],
        'U':['lui','auipc'],
        'J':['jal']}


# def prOp(op2):
#     print(opstr[op2],end=" ")     
# def pr_instr_name(instr_name):
#     print(instr_name,end=" ")     

# encode instruction into internal code 0..9
# def encodeOpx(op2,xf3,xf7):
#     if( op2 == 51 and xf3 == 0):
#         if(xf7 == 0):
#             return 1
#         elif(xf7 == 32):
#             return 2
#     elif(op2 == 19 and xf3 == 0):
#         return 3
#     elif(op2 == 3 and xf3 == 2):
#         return 4
#     elif(op2 == 35 and xf3 == 2):
#         return 5
#     elif(op2 == 99):
#         if(xf3 == 0):
#             return 6
#         elif(xf3 == 1):
#             return 7
#         elif(xf3 == 4):
#             return 8
#         elif(xf3 == 5):
#             return 9
#     elif(op2 == 51 and xf3 == 7 and xf7 == 0):   # and x2,x3,x4
#         return 10
#     return 0


def decodeInstr(op2,xf3,xf7):
    '''
    decode instruction
    '''
    global instr_name, opcode_type, instr_type

    if(op2 == opcode_lui):
        instr_name = opstr['U'][0] # 'lui'
        opcode_type = 'LUI'
        instr_type = 'U'
    elif(op2 == opcode_auipc):
        instr_name = opstr['U'][1] # 'auipc'
        opcode_type = 'AUIPC'
        instr_type = 'U'
    elif(op2 == opcode_jal):
        instr_name = opstr['J'][0] # 'jal'
        opcode_type = 'JAL'
        instr_type = 'J'
    elif(op2 == opcode_jalr):
        instr_name = opstr['I'][0] # 'jalr'
        opcode_type = 'JALR'
        instr_type = 'I'
    elif(op2 == opcode_branch):
        opcode_type = 'BRANCH'
        instr_type = 'B'
        if(xf3 == 0):
            instr_name = opstr['B'][0] # 'beq'
        elif(xf3 == 1):
            instr_name = opstr['B'][1] # 'bne'
        elif(xf3 == 4):
            instr_name = opstr['B'][2] # 'blt'
        elif(xf3 == 5):
            instr_name = opstr['B'][3] # 'bge'
        elif(xf3 == 6):
            instr_name = opstr['B'][4] # 'bltu'
        elif(xf3 == 7):
            instr_name = opstr['B'][5] # 'bgeu'
    elif(op2 == opcode_load):
        opcode_type = 'LOAD'
        instr_type = 'I'
        if(xf3 == 0):
            instr_name = opstr['I'][1] # 'lb'
        elif(xf3 == 1):
            instr_name = opstr['I'][2] # 'lh'
        elif(xf3 == 2):
            instr_name = opstr['I'][3] # 'lw'
        elif(xf3 == 4):
            instr_name = opstr['I'][4] # 'lbu'
        elif(xf3 == 5):
            instr_name = opstr['I'][5] # 'lhu'
    elif(op2 == opcode_store):
        opcode_type = 'STORE'
        instr_type = 'S'
        if(xf3 == 0):
            instr_name = opstr['S'][0] # 'sb'
        elif(xf3 == 1):
            instr_name = opstr['S'][1] # 'sh'
        elif(xf3 == 2):
            instr_name = opstr['S'][2] # 'sw'
    elif(op2 == opcode_alui):
        opcode_type = 'ALUI'
        instr_type = 'I'
        if(xf3 == 0):
            instr_name = opstr['I'][6] # 'addi'
        elif(xf3 == 2):
            instr_name = opstr['I'][7] # 'slti'
        elif(xf3 == 3):
            instr_name = opstr['I'][8] # 'sltiu'
        elif(xf3 == 4):
            instr_name = opstr['I'][9] # 'xori'
        elif(xf3 == 6):
            instr_name = opstr['I'][10] # 'ori'
        elif(xf3 == 7):
            instr_name = opstr['I'][11] # 'andi'
        elif(xf3 == 1 and xf7 == 0):
            instr_name = opstr['I'][12] # 'slli'
        elif(xf3 == 5 and xf7 == 0):
            instr_name = opstr['I'][13] # 'srli'
        elif(xf3 == 5 and xf7 == 32):
            instr_name = opstr['I'][14] # 'srai'
    elif(op2 == opcode_alur):
        opcode_type = 'ALUR'
        instr_type = 'R'
        if(xf3 == 0 and xf7 == 0):
            instr_name = opstr['R'][0] # 'add'
        elif(xf3 == 0 and xf7 == 32):
            instr_name = opstr['R'][1] # 'sub'
        elif(xf3 == 1 and xf7 == 0):
            instr_name = opstr['R'][2] # 'sll'
        elif(xf3 == 2 and xf7 == 0):
            instr_name = opstr['R'][3] # 'slt'
        elif(xf3 == 3 and xf7 == 0):
            instr_name = opstr['R'][4] # 'sltu'
        elif(xf3 == 4 and xf7 == 0):
            instr_name = opstr['R'][5] # 'xor'
        elif(xf3 == 5 and xf7 == 0):
            instr_name = opstr['R'][6] # 'srl'
        elif(xf3 == 5 and xf7 == 32):
            instr_name = opstr['R'][7] # 'sra'
        elif(xf3 == 6 and xf7 == 0):
            instr_name = opstr['R'][8] # 'or'
        elif(xf3 == 7 and xf7 == 0):
            instr_name = opstr['R'][9] # 'and'
    else:
        instr_name = 'nop'
        opcode_type = 'nop'
        instr_type = 'NaN'
    


# def signx12(x):          # sign extension 12 bits
#     if( x & 0x0800 ):
#         return x | 0x0FFFFF000
#     return x

# def getOp():
#     '''
#     must decode() first
#     return tuple of instr_name, rd, rs1, rs2
#     '''
#     instr_name = encodeOpx(op,f3,f7) #return a string of instr_name
#     return (instr_name,rd,rs1,rs2)

def getInstr():
    '''
    must decode() first
    return tuple of instr_name, opcode_type, instr_type
    '''
    decodeInstr(op,f3,f7)
    return (instr_name, opcode_type, instr_type, rd, rs1, rs2)
    

def getIm():
    '''
    must decode() first, extract imm_I from instr[31:12]
    '''
    return imm          # sign is already extended

def getIm_S():
    '''
    must decode() first, extract imm_S for 'sb/sh/sw' from instr[31:25] + instr[11:7]
    '''
    return (f7<<5) + rd    # positive integer [check further]


def getIm_B():
    '''
    must decode() first, extract imm_B for branch instructions from instr[31]+[7]+[30:25]+[11:8]+0
    '''
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

def getIm_U():
    '''
    must decode() first, extract imm_U for 'lui/auipc' from instr[31:12]+0
    '''
    return (((imm<<8)+(rs1<<3)+f3)<<12)


def getIm_J():
    '''
    must decode() first, extract imm_J for 'jal' from instr[31]+[19:12]+[20]+[30:21]+0
    '''
    s11 = 0
    if((rs2 & 1) != 0):
        s11 = 0x0800 # bit[11] is 1
    # Im_J[10:1] = ((f7 & 63) << 4) + (rs2 & 30)
    # Im_J[19:12] = (rs1<<3) + f3
    m = (((rs1<<3) + f3)<<12) | s11 | (((f7 & 63) << 4) + (rs2 & 30))
    if( (f7 & 0x040) != 0 ):
        return m - 1048576
    return m


def loadobj(fname):
    f = open(fname,"r")
    fx = f.readlines()
    a = 0
    for line in fx:
        lx = line.split()
        Memory[a] = hextodec(lx[0][2:])
        a += 1
    f.close()
    print("load program, last address ",a)
    

def disassem(c):
    '''
    print instruction infos followed by rd, rs1, rs2
    '''
    decode(c)
    # decodeInstr(op,f3,f7)
    # print(instr_name, opcode_type, instr_type, rd, rs1, rs2)
    pr_Current_instr()


def dumpAS(ads,n):
    '''
    disassemble a range of memory
    '''
    for i in range(ads,ads+n):
        disassem(Memory[i])

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
# def prCurrentOp():
#     instr_name = encodeOpx(op,f3,f7)
#     pr_instr_name(instr_name)
#     if(op2 in [1,2,10]):           # add, sub, and
#         pr3R(rd,rs1,rs2)
#     elif(op2 == 3):             # addi
#         prI(rd,rs1,imm)
#     elif(op2 == 4):             # lw
#         prLS(rd,rs1,imm)
#     elif(op2 == 5):             # sw
#         prLS(rs2,rs1,getIm_S())
#     elif(op2 in [6,7,8,9]):     # branch
#         prB(rs1,rs2,getIm_B())
    
def pr_Current_instr():
    decodeInstr(op,f3,f7)
    print(instr_name,end=" ")
    if(opcode_type == 'ALUR'):
        pr3R(rd,rs1,rs2)
    elif(opcode_type == 'LOAD'):
        prLS(rd,rs1,imm)
    elif(opcode_type == 'STORE'):
        prLS(rs2,rs1,getIm_S())
    elif(opcode_type == 'ALUI'):
        prI(rd,rs1,imm)
    elif(opcode_type == 'BRANCH'):
        prB(rs1,rs2,getIm_B())
    print()
  # print(instr_name, rd, rs1, rs2)


#loadobj("test.obj")
#dumpM(0,9)
#dumpAS(0,9)




