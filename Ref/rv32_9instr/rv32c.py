#  risc-v 32-bit simulator with control signals, rv32c.py
#     version 1.0  with 9 instructions
#     20 Feb 2022
#     Prabhas Chongstitvatana

import array
import load32 as ld

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
mx1_0 = 0
mx1_1 = 0
mx2_0 = 0
mx2_1 = 0
mx3_0 = 0
mx3_1 = 0
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
    return op == 0

#  control unit for execute, memory, writeback
def setControl_vector():
    global control_vector
    control_vector = []
    control_vector.append([0,0,0,0,0,0,0])   # nop
    control_vector.append([0,2,0,0,0,0,1])   # add
    control_vector.append([0,3,0,0,0,0,1])   # sub
    control_vector.append([1,2,0,0,0,0,1])   # addi
    control_vector.append([1,2,0,1,0,1,1])   # lw
    control_vector.append([1,2,0,0,1,1,0])   # sw
    control_vector.append([0,4,1,0,0,0,0])   # beq
    control_vector.append([0,5,1,0,0,0,0])   # bne
    control_vector.append([0,6,1,0,0,0,0])   # blt
    control_vector.append([0,7,1,0,0,0,0])   # bge


# ---------   data path with control --------

def dofetch():
    global IR, ads1
    ads1 = PC
    IR = ld.getM(ads1)      # read program memory

# from IR  decode all fields in an instruction
#   op, rd, rs1, rs2, imm, offset
def dodecode():
    global op, rd, rs1, rs2, imm, offset
    global mx2_1, mx1_1, mx1_0
    
    ld.decode(IR)
    (op,rd,rs1,rs2) = ld.getOp()
    # imm generator, depend on instruction type
    if(op == 3 or op == 4):  # addi, lw
        imm = ld.getIm()
    elif(op == 5):           # sw
        imm = ld.getIm_S()
    offset = ld.getIm_B()    # branch offset

    # update wires
    mx2_1 = imm
    mx1_1 = PC + offset
    mx1_0 = PC + 4

def doAsrc():          # mux2 select data for ALU port a2
    global a2
    if (cv[0] == 1):
        a2 = mx2_1
    else:
        a2 = mx2_0

def doALU():
    global Aout, zero, ads2, mx3_0
    aop = cv[1]
    if(aop == 0):       # and no implement
        Aout = 0
    elif(aop == 1):     # or not implement
        Aout = 0
    elif(aop == 2):     # add
        Aout = a1 + a2
    elif(aop == 3):     # sub
        Aout = a1 - a2
    elif(aop == 4):     # eq
        Aout = 0
        zero = a1 == a2
    elif(aop == 5):     # ne
        Aout = 0
        zero = a1 != a2  
    elif(aop == 6):     # lt
        Aout = 0
        zero = a1 < a2
    elif(aop == 7):     # ge
        Aout = 0
        zero = a1 >= a2

    # update wires
    ads2 = Aout
    mx3_0 = Aout
    
def doBranch():
    global PC

    if((cv[2] == 1) and zero):
        print("branch taken")
        PC = mx1_1
    else:
        PC = mx1_0
    print("next pc ",PC)
        
def doexecute():
    global cv, R1, R2
    global a1, mx2_0, Mdata

    cv = control_vector[op]
    print(cv)
    R1 = R[rs1]      # read registers
    R2 = R[rs2]
    # update wires
    a1 = R1
    mx2_0 = R2
    Mdata = R2
    doAsrc()
    doALU()
    doBranch()
    
def doMread():
    global Mout, mx3_1
    if(cv[3] == 1):
        Mout = ld.getM(ads2)
        # update wire
        mx3_1 = Mout
    
def doMwrite():
    if(cv[4] == 1):
        ld.setM(ads2,Mdata)
    
def domemory():
    doMread()
    doMwrite()
    
def doMtoR():
    global Rdata
    if(cv[5] == 1):
        Rdata = mx3_1
    else:
        Rdata = mx3_0

def doRwrite():
    if(cv[6] == 1):
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
