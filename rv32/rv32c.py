#  risc-v 32-bit simulator with control signals, rv32c.py
#     version 1.0  with 9 instructions
#     20 Jan 2023
#     Li Keran

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
import load32 as ld

alu_add = 0b0000
alu_slt = 0b0010
alu_sltu = 0b0011
alu_xor = 0b0100
alu_or = 0b0110
alu_and = 0b0111
alu_sll = 0b0001
alu_srl = 0b0101
alu_sra = 0b1101
alu_sub = 0b1000
alu_beq = 0b1001
alu_bne = 0b1010
alu_bge = 0b1011
alu_bgeu = 0b1100



R = array.array('L',[0]*32)       # registers
PC = 0                            # internal PC, *4 for actual pc

# --- input of registers ----
op = 0                            # instruction fields
rd = 0
rs1 = 0
rs2 = 0
Rdata = 0
# -----------
imm = 0
offset = 0
# --- multiplexor wires
mx1_0 = 0 # pc = pc + 4
mx1_1 = 0 # pc = pc + offset(branch)
mx2_0 = 0 # alu_in_2 = R2
mx2_1 = 0 # alu_in_2 = imm
mx3_0 = 0 # Rdata = Aout
mx3_1 = 0 # Rdata = Mout
mx4_0 = 0 # alu_in_1 = R1
mx4_1 = 0 # alu_in_1 = pc(auipc)
# --- ALU input/output
a1 = 0
a2 = 0
zero = True
# ---- internal ----
IR = 0
R1 = 0
R2 = 0
Aout = 0
Mout = 0
# ----  memory input --
ads1 = 0
ads2 = 0
Mdata = 0

# ----- interface functions ----------

def getR(i):
    return R[i]

def setR(r1,d):
    if(r1 != 0):        # protect R[0]
        R[r1] = int(d & 0x0FFFFFFFF)    # truncate to 32-bit

def getPC():
    return PC

def setPC(n):
    PC = n
   
def checkNop():           # check if current is nop 
    return instr_name == 'nop'

#  control unit for execute, memory, writeback
# def setControl_vector():
#     global control_vector
#     control_vector = []
#     control_vector.append([0,0,0,0,0,0,0])   # nop
#     control_vector.append([0,2,0,0,0,0,1])   # add
#     control_vector.append([0,3,0,0,0,0,1])   # sub
#     control_vector.append([1,2,0,0,0,0,1])   # addi
#     control_vector.append([1,2,0,1,0,1,1])   # lw
#     control_vector.append([1,2,0,0,1,1,0])   # sw
#     control_vector.append([0,4,1,0,0,0,0])   # beq
#     control_vector.append([0,5,1,0,0,0,0])   # bne
#     control_vector.append([0,6,1,0,0,0,0])   # blt
#     control_vector.append([0,7,1,0,0,0,0])   # bge

def setControl_vector():
    '''
    control unit for execute, memory, writeback
    '''
    global control_vector
    control_vector = {
            'LUI': {'branch': 0, 'jump': 0, 'memRead': 0, 'memWrite': 0, 'regWrite': 1, 'mem2reg': 0, 'aluSrc1': 0, 'aluSrc2': 0, 'resultSel': 1, 'aluctrlop': 0},
            'AUIPC': {'branch': 0, 'jump': 0, 'memRead': 0, 'memWrite': 0, 'regWrite': 1, 'mem2reg': 0, 'aluSrc1': 1, 'aluSrc2': 1, 'resultSel': 0, 'aluctrlop': 0},
            'JAL': {'branch': 0, 'jump': 0, 'memRead': 0, 'memWrite': 0, 'regWrite': 1, 'mem2reg': 0, 'aluSrc1': 0, 'aluSrc2': 0, 'resultSel': 2, 'aluctrlop': 0},
            'JALR': {'branch': 0, 'jump': 1, 'memRead': 0, 'memWrite': 0, 'regWrite': 1, 'mem2reg': 0, 'aluSrc1': 0, 'aluSrc2': 1, 'resultSel': 2, 'aluctrlop': 0},
            'BRANCH': {'branch': 1, 'jump': 0, 'memRead': 0, 'memWrite': 0, 'regWrite': 0, 'mem2reg': 0, 'aluSrc1': 0, 'aluSrc2': 0, 'resultSel': 0, 'aluctrlop': 2},
            'LOAD': {'branch': 0, 'jump': 0, 'memRead': 1, 'memWrite': 0, 'regWrite': 1, 'mem2reg': 1, 'aluSrc1': 0, 'aluSrc2': 1, 'resultSel': 0, 'aluctrlop': 0},
            'STORE': {'branch': 0, 'jump': 0, 'memRead': 0, 'memWrite': 1, 'regWrite': 0, 'mem2reg': 0, 'aluSrc1': 0, 'aluSrc2': 1, 'resultSel': 0, 'aluctrlop': 0},
            'ALUI': {'branch': 0, 'jump': 0, 'memRead': 0, 'memWrite': 0, 'regWrite': 1, 'mem2reg': 0, 'aluSrc1': 0, 'aluSrc2': 1, 'resultSel': 0, 'aluctrlop': 1},
            'ALUR': {'branch': 0, 'jump': 0, 'memRead': 0, 'memWrite': 0, 'regWrite': 1, 'mem2reg': 0, 'aluSrc1': 0, 'aluSrc2': 0, 'resultSel': 0, 'aluctrlop': 1},
            'nop': {'branch': 0, 'jump': 0, 'memRead': 0, 'memWrite': 0, 'regWrite': 0, 'mem2reg': 0, 'aluSrc1': 0, 'aluSrc2': 0, 'resultSel': 0, 'aluctrlop': 0}}


# ---------   data path with control --------

def dofetch():
    '''
    read program memory
    '''
    global IR, ads1
    ads1 = PC
    IR = ld.getMemory(ads1)


def dodecode():
    '''
    from IR  decode all fields in an instruction
    op, rd, rs1, rs2, imm, offset
    '''
    global instr_name, opcode_type, instr_type, rd, rs1, rs2, imm, offset
    global mx2_1, mx1_1, mx1_0

    ld.decode(IR)
    (instr_name, opcode_type, instr_type, rd, rs1, rs2) = ld.getInstr()
    # imm generator, depend on instruction type
    if(instr_type == 'I' ):  # I-type
        imm = ld.getIm()
    elif(instr_type == 'S'): # S-type
        imm = ld.getIm_S() 
    elif(instr_type == 'B'): # B-type
        offset = ld.getIm_B()
    elif(instr_type == 'U'): # U-type
        imm = ld.getIm_U()
    elif(instr_type == 'J'): # J-type
        imm = ld.getIm_J()
    # offset = ld.getIm_B()    # branch offset

    # update wires
    # branch
    mx1_1 = PC + offset
    mx1_0 = PC + 4
    # I-type instruction rs2 = imm
    mx2_1 = imm

def doAlusrc1():
    '''
    mux4 select data for ALU port a1
    '''
    global a1
    if(cv['aluSrc1'] == 1): # AUIPC
        a1 = mx4_1
    else:
        a1 = mx4_0

def doAlusrc2():
    '''
    mux2 select data for ALU port a2
    '''
    global a2
    if(cv['aluSrc2'] == 1): # AUIPC/JALR/LOAD/STORE/ALUI
        a2 = mx2_1
    else:
        a2 = mx2_0

def doALUctrl():
    '''
    ALU control opcode for different instructions
    '''
    global aluop
    aop = cv['aluctrlop']
    if(aop == 0):       # Load or Store
        aluop = alu_add
    elif(aop == 1):     # ALUI/ALUR
        if(instr_name == 'addi' or instr_name == 'add'):
            aluop = alu_add
        elif(instr_name == 'slti' or instr_name == 'slt'):
            aluop = alu_slt
        elif(instr_name == 'sltiu' or instr_name == 'sltu'):
            aluop = alu_sltu
        elif(instr_name == 'xori' or instr_name == 'xor'):
            aluop = alu_xor
        elif(instr_name == 'ori' or instr_name == 'or'):
            aluop = alu_or
        elif(instr_name == 'andi' or instr_name == 'and'):
            aluop = alu_and
        elif(instr_name == 'slli' or instr_name == 'sll'):
            aluop = alu_sll
        elif(instr_name == 'srli' or instr_name == 'srl'):
            aluop = alu_srl
        elif(instr_name == 'srai' or instr_name == 'sra'):
            aluop = alu_sra
        elif(instr_name == 'sub'):
            aluop = alu_sub
    elif(aop == 2):     # Branch
        if(instr_name == 'beq'):
            aluop = alu_beq
        elif(instr_name == 'bne'):
            aluop = alu_bne
        elif(instr_name == 'blt'):
            aluop = alu_slt
        elif(instr_name == 'bge'):
            aluop = alu_bge
        elif(instr_name == 'bltu'):
            aluop = alu_sltu
        elif(instr_name == 'bgeu'):
            aluop = alu_bgeu


def doALU():
    global aluop, Aout, zero, ads2, mx3_0
    if(aluop == alu_add):
        Aout = a1 + a2
    elif(aluop == alu_beq):     # beq
        Aout = 0
        zero = a1 == a2
    elif(aluop == alu_bne):     # bne
        Aout = 0
        zero = a1 != a2
    elif(aluop == alu_slt):     # blt
        Aout = 0
        zero = a1 < a2
    elif(aluop == alu_bge):     # bge
        Aout = 0
        zero = a1 >= a2

    # update wires
    ads2 = Aout
    mx3_0 = Aout
    
def doBranch():
    global PC

    if((cv['branch'] == 1) and zero):
        print("branch taken")
        PC = mx1_1
    else:
        PC = mx1_0
    print("next pc ",PC)
        
def doexecute():
    global cv, R1, R2
    global a1, mx2_0, mx4_0,Mdata

    cv = control_vector[opcode_type]
    # print(cv)
    R1 = R[rs1]      # read registers
    R2 = R[rs2]
    # update wires
    mx4_0 = R1
    mx2_0 = R2
    Mdata = R2
    doAlusrc1()
    doAlusrc2()
    doALUctrl()
    doALU()
    doBranch()
    
def doMread():
    global Mout, mx3_1
    if(cv['memRead'] == 1):
        Mout = ld.getMemory(ads2)
        # update wire
        mx3_1 = Mout
    
def doMwrite():
    if(cv['memWrite'] == 1):
        ld.setMemory(ads2,Mdata)
    
def domemory():
    doMread()
    doMwrite()
    
def doMtoR():
    global Rdata
    if(cv['mem2reg'] == 1):
        Rdata = mx3_1
    else:
        Rdata = mx3_0

def doRwrite():
    if(cv['regWrite'] == 1):
        setR(rd,Rdata)
    
def dowriteback():
    doMtoR()
    doRwrite()

# ---- main processor simulation ----

#  complete execute one instruction
def run():
    dofetch()
    dodecode()
    doexecute()
    domemory()
    dowriteback()
  
# --- end -------
