#!/usr/bin/env python3
"""
CS4200 - Assignment 4
RV32I Datapath Simulator (Template)

Students must complete all TODO sections.

Program behavior:
  - Read instructions from hex_inst.txt
  - Simulate execution using datapath stages:
      IF → ID → EX → MEM → WB
  - Generate logs at end of execution:
      trace.log
      regs_final.log
      dmem_final.log

Restrictions:
  - No nested functions
  - No dataclasses
  - Keep code simple and readable
"""

MASK32 = 0xFFFFFFFF


# ------------------------------------------------------------
# 32-bit helpers
# ------------------------------------------------------------

def u32(x):
    """
    Return x truncated to 32 bits (unsigned).
    Hint: mask with 0xFFFFFFFF
    """
    return x & MASK32


def s32(x):
    """
    Convert a 32-bit unsigned value to signed two's complement.
    If bit 31 is 1, subtract 2^32.
    """
    x &= 0xFFFFFFFF

    return x if x < 0x80000000 else x - 0x100000000


def sign_extend(value, bits):
    """
    Sign-extend 'value' which is 'bits' wide.

    Example:
        sign_extend(0b1111, 4) -> -1
    """
    sign_bit = 1 << (bits - 1)

    return (value & (sign_bit-1)) - (value & sign_bit)


def get_bits(x, hi, lo):
    """
    Extract bits from position hi down to lo (inclusive).

    Example:
        get_bits(0b101100, 3, 1) -> 0b110
    """
    if hi < lo:

        raise ValueError("hi must be >= lo")

    mask = (1 << (hi - lo + 1) ) - 1

    return (x>>lo) & mask


# ------------------------------------------------------------
# Immediate Generators
# ------------------------------------------------------------

def imm_i(instr):
    """
    I-type immediate = bits [31:20]
    Sign extend to 32 bits
    """
    result = get_bits(instr,31,20)

    return sign_extend(result, 12)


def imm_s(instr):
    """
    S-type immediate uses:
        bits [31:25] and [11:7]
    Combine then sign extend.
    """
    imm_11_5 = get_bits(instr,31,25)

    imm_4_0 = get_bits(instr,11,7)

    imm = (imm_11_5 << 5) | imm_4_0

    return sign_extend(imm,12)


def imm_b(instr):
    """
    B-type immediate uses scattered bits:
        imm[12]   = instr[31]
        imm[11]   = instr[7]
        imm[10:5] = instr[30:25]
        imm[4:1]  = instr[11:8]
        imm[0]    = 0
    Then sign extend to 32 bits.
    """
    imm_12 = get_bits(instr,31,31)

    imm_10_5 = get_bits(instr, 30,25)

    imm_4_1 = get_bits(instr,11,8)

    imm_11 = get_bits(instr,7,7)

    imm = (imm_12 << 12) | (imm_11 << 11) | (imm_10_5 << 5) | (imm_4_1 << 1)

    return sign_extend(imm,13)


def imm_u(instr):
    """
    TODO
    U-type immediate = bits [31:12] << 12
    """
    return get_bits(instr,31,12) << 12


def imm_j(instr):
    """
    TODO
    J-type immediate for JAL instruction.
        imm[20]    = instr[31]
        imm[10:1]  = instr[30:21]
        imm[11]    = instr[20]
        imm[19:12] = instr[19:12]
        imm[0]     = 0
    Then sign extend.
    """
    imm_20 = get_bits(instr,31,31)

    imm_10_1 = get_bits(instr,30,21)

    imm_11 = get_bits(instr,20,20)

    imm_19_12 = get_bits(instr,19,12)

    imm = (imm_20<<20) | (imm_19_12<<12) | (imm_11<<11) | (imm_10_1<<1)

    return sign_extend(imm, 21)


# ------------------------------------------------------------
# Instruction Decode
# ------------------------------------------------------------

def decode(instr):
    """
    TODO
    Extract instruction fields and return dictionary with:
        opcode
        rd
        funct3
        rs1
        rs2
        funct7

    Also compute all immediates and store:
        imm_I
        imm_S
        imm_B
        imm_U
        imm_J
    """
    d = {}
    d["instr"]  = instr
    d["opcode"] = get_bits(instr, 6, 0)
    d["rd"]     = get_bits(instr, 11, 7)
    d["funct3"] = get_bits(instr, 14, 12)
    d["rs1"]    = get_bits(instr,19,15)
    d["rs2"]    = get_bits(instr,24,20)
    d["funct7"] = get_bits(instr,31,25)
    d["imm_I"]  = imm_i(instr)
    d["imm_S"]  = imm_s(instr)
    d["imm_B"]  = imm_b(instr)
    d["imm_U"]  = imm_u(instr)
    d["imm_J"]  = imm_j(instr)
    return d


# ------------------------------------------------------------
# Control Unit
# ------------------------------------------------------------

def main_control(d):
    """
    TODO
    Implement the main control unit.
    Based on opcode, generate control signals:
        RegWrite
        MemRead
        MemWrite
        MemToReg
        ALUSrc
        Branch
        Jump
        JumpReg
        ALUOp
        ImmSel
        BrType
    """
    c = {
        "RegWrite": 0,
        "MemRead":  0,
        "MemWrite": 0,
        "MemToReg": 0,
        "ALUSrc":   0,
        "Branch":   0,
        "Jump":     0,
        "JumpReg":  0,
        "ALUOp":    "ADDR",
        "ImmSel":   None,
        "BrType":   None,
    }


    
    if d['opcode'] == 0b0110011: # R-Type

        c["RegWrite"] = 1

        c["ALUOp"] = 'RTYPE'

    elif d['opcode'] == 0b0010011: # I-Type

        c["RegWrite"] = 1

        c["ALUSrc"]   = 1

        c["ALUOp"]    = "ITYPE"

        c["ImmSel"]   = "I"

    elif d['opcode'] == 0b0000011: # lw
        
        c["RegWrite"] = 1

        c["MemRead"]  = 1

        c["MemToReg"] = 1

        c["ALUSrc"]   = 1

        c["ALUOp"]    = "ADDR"

        c["ImmSel"]   = "I"

    elif d['opcode'] == 0b0100011: # sw

        c["MemWrite"] = 1
        
        c["ALUSrc"]   = 1
        
        c["ALUOp"]    = "ADDR"
        
        c["ImmSel"]   = "S"

    elif d['opcode'] == 0b1100011: # Branch

        c["Branch"]   = 1
        
        c["ALUOp"]    = "BRANCH"
        
        c["ImmSel"]   = "B"
        
        c["BrType"]   = d['funct3']

    elif d['opcode'] == 0b1101111: # jal

        c["RegWrite"] = 1
        
        c["Jump"]     = 1
        
        c["MemToReg"] = 2 
        
        c["ImmSel"]   = "J"

    elif d['opcode'] == 0b1100111: # jalr
        
        c["RegWrite"] = 1
        
        c["JumpReg"]  = 1
        
        c["ALUSrc"]   = 1
        
        c["MemToReg"] = 2
        
        c["ALUOp"]    = "ADDR"
        
        c["ImmSel"]   = "I"

    elif d['opcode'] == 0b0110111: # lui
        
        c["RegWrite"] = 1
        
        c["ALUSrc"]   = 1
        
        c["ALUOp"]    = "LUI"
        
        c["ImmSel"]   = "U"

    elif d['opcode'] == 0b0010111: # auipc

        c["RegWrite"] = 1

        c["ALUSrc"]   = 1

        c["ALUOp"]    = "AUIPC"
        
        c["ImmSel"]   = "U"



    return c


# ------------------------------------------------------------
# ALU Control
# ------------------------------------------------------------

def alu_control(c, d):
    """
    TODO
    Determine ALU operation string:
        ADD, SUB, AND, OR, XOR,
        SLL, SRL, SRA, SLT, SLTU

    Use:
        - ALUOp
        - funct3
        - funct7
    """

    if(c['ALUOp'] == 'ADDR'):

        return "ADD"
    
    elif(c['ALUOp'] == 'RTYPE'):

        if(d['funct3'] == 0x0 and d['funct7'] == 0x00):

            return "ADD"
        
        elif(d['funct3'] == 0x0 and d['funct7'] == 0x20):

            return "SUB"
        
        elif(d['funct3'] == 0x4 and d['funct7'] == 0x00):

            return "XOR"
        
        elif(d['funct3'] == 0x6 and d['funct7'] == 0x00):

            return "OR"
        
        elif(d['funct3'] == 0x7 and d['funct7'] == 0x00):

            return "AND"
        
        elif(d['funct3'] == 0x1 and d['funct7'] == 0x00):

            return "SLL"
        
        elif(d['funct3'] == 0x5 and d['funct7'] == 0x00):

            return "SRL"
        
        elif(d['funct3'] == 0x5 and d['funct7'] == 0x20):

            return "SRA"
        
        elif(d['funct3'] == 0x2 and d['funct7'] == 0x00):

            return "SLT"
        
        elif(d['funct3'] == 0x3 and d['funct7'] == 0x00):

            return "SLTU"
        
    elif(c['ALUOp'] == "BRANCH"):

        return "SUB"
    
    elif(c['ALUOp'] == "ITYPE"):

        if(d['funct3'] == 0x0):

            return "ADD"
        
        elif(d['funct3'] == 0x4):

            return "XOR"
        
        elif(d['funct3'] == 0x6):

            return "OR"
        
        elif(d['funct3'] == 0x7):

            return "AND"
        
        elif(d['funct3'] == 0x1):

            return "SLL"
        
        elif(d['funct3'] == 0x2):

            return "SLT"
        
        elif(d['funct3'] == 0x3):

            return "SLTU"
        
        elif(d['funct3'] == 0x5):

            if(d['funct7'] == 0x20):

                return "SRA"
            
            else:

                return "SRL"
    
    elif c['ALUOp'] == "LUI":
        
        return "LUI"

    elif c['ALUOp'] == "AUIPC":
        
        return "AUIPC"
        
    


# ------------------------------------------------------------
# ALU
# ------------------------------------------------------------

def alu_exec(op, a, b):
    """
    TODO
    Execute ALU operation.
    Must support:
        ADD, SUB, AND, OR, XOR,
        SLL, SRL, SRA, SLT, SLTU

    Return 32-bit result.
    """

    match op:

        case "ADD":

            return u32(a+b)
        
        case "SUB":

            return u32(a-b)
        
        case "AND":

            return a & b
        
        case "OR":

            return a | b
        
        case "XOR":

            return a ^ b
        
        case "SLL":

            return  u32(a << (b & 0b11111))
        
        case "SRL":

            return a >> (b & 0b11111)
        
        case "SRA":

            return u32(s32(a) >> (b & 0b11111))
        
        case "SLT":

            signed_a = s32(a)

            signed_b = s32(b)

            if signed_a < signed_b:

                return 1

            else:

                return  0 
        
        case "SLTU":

            if u32(a) < u32(b):

                return 1
            
            else:

                return 0
        
        case "LUI":

            return u32(b)
        
        case "AUIPC":

            return u32(a + b)
            
        case _:

            return 0


# ------------------------------------------------------------
# IF Stage
# ------------------------------------------------------------

def stage_if(pc, imem):
    """
    TODO
    Instruction Fetch stage.
    Compute:
        pc
        pc_plus4
        instr

    If PC not in instruction memory,
    return instr=None to signal halt.
    """
    out = {}
    out["pc"]       = 0
    out["pc_plus4"] = 0
    out["instr"]    = None

    if pc in imem:

        out["pc"] = pc

        out['pc_plus4'] = pc + 4

        out["instr"] = imem[pc]


    return out


# ------------------------------------------------------------
# Immediate Selector
# ------------------------------------------------------------

def select_imm(d, c):
    """
    TODO
    Return correct immediate depending on control signal ImmSel.
    """

    match c['ImmSel']:

        case 'I':

            return d['imm_I']
        
        case 'S':

            return d['imm_S']
        
        case 'B':

            return d['imm_B']
        
        case 'U':

            return d['imm_U']
        
        case 'J':

            return d['imm_J']
        
        case _:

            return 0
            


# ------------------------------------------------------------
# ID Stage
# ------------------------------------------------------------

def stage_id(instr, regs):
    """
    TODO
    Decode instruction
    Generate control signals
    Read register file
    Select immediate

    Return dictionary with:
        decoded instruction
        control signals
        rs1_val
        rs2_val
        rd
        immediate
    """
    out = {}
    out["d"]       = {}
    out["c"]       = {}
    out["imm"]     = 0
    out["rs1_val"] = 0
    out["rs2_val"] = 0
    out["rd"]      = 0
    out["rs1"]     = 0
    out["rs2"]     = 0

    out["d"] = decode(instr)

    out["c"] = main_control(out['d'])

    out['imm'] = select_imm(out['d'], out['c'])

    out['rd'] = out['d']['rd']

    out['rs1'] = out['d']['rs1']

    out['rs2'] = out['d']['rs2']

    out['rs1_val'] = regs[out['rs1']]

    out['rs2_val'] = regs[out['rs2']]


    return out


# ------------------------------------------------------------
# Branch Logic
# ------------------------------------------------------------

def branch_taken(br_type, rs1_val, rs2_val):
    """
    TODO
    Implement branch comparisons:
        beq, bne, blt, bge, bltu, bgeu
    """

    if(br_type == 0x0):

        #BEQ

        if (rs1_val == rs2_val):

            return True
        
        else:

            return False
    
    elif(br_type == 0x1):

        #BNE

        if (rs1_val != rs2_val):

            return True
        
        else:

            return False
        
    elif(br_type == 0x4):

        #BLT

        if (s32(rs1_val) < s32(rs2_val)):

            return True
        
        else:
            
            return False
    
    elif(br_type == 0x5):

        #BGE

        if(s32(rs1_val) >= s32(rs2_val)):

            return True
        
        else:

            return False
        
    elif(br_type == 0x6):

        #BLTU

        if (u32(rs1_val) < u32(rs2_val)):

            return True
        
        else:
            
            return False
        
    elif(br_type == 0x7):

        #BGEU

        if(u32(rs1_val) >= u32(rs2_val)):

            return True
        
        else:

            return False
    
    else:

        return False


# ------------------------------------------------------------
# EX Stage
# ------------------------------------------------------------

def stage_ex(pc, pc_plus4, id_out):
    """
    TODO
    Execute stage responsibilities:
        - determine ALU operation
        - select ALU input2
        - compute ALU result
        - evaluate branch condition
        - compute branch target
        - compute jump target
        - determine next PC
    """
    out = {}
    out["alu_op"]      = "ADD"
    out["alu_res"]     = 0
    out["next_pc"]     = pc_plus4
    out["taken"]       = False
    out["br_target"]   = 0
    out["jal_target"]  = 0
    out["jalr_target"] = 0

    out["alu_op"] = alu_control(id_out["c"], id_out['d'])

    if id_out['c']['ALUOp'] == "AUIPC":

        alu_a = pc

    else:

        alu_a = id_out['rs1_val']


    if id_out['c']["ALUSrc"] == 1:

        out["alu_res"] = alu_exec(out["alu_op"], alu_a, id_out['imm'])
    
    else:

         out["alu_res"] = alu_exec(out["alu_op"], alu_a , id_out['rs2_val'])

    if(id_out['c']['Branch'] == 1):

        out['taken'] = branch_taken(id_out['c']['BrType'], id_out['rs1_val'], id_out['rs2_val'])

        out['br_target'] = pc + id_out['imm']

        if(out['taken']):

            out['next_pc'] = out['br_target']
    
    if(id_out['c']['Jump'] == 1):

        out['jal_target'] = u32(pc + id_out['imm'])

        out['next_pc'] = out['jal_target']
    
    if(id_out['c']['JumpReg'] == 1):

        out["jalr_target"] = u32(id_out['rs1_val'] + id_out['imm']) & ~1

        out["next_pc"] = out["jalr_target"]

    return out


# ------------------------------------------------------------
# Data Memory
# ------------------------------------------------------------

def dmem_load_word(dmem, addr):
    """
    TODO
    Load word from data memory.
    Enforce 4-byte alignment.
    """
    if (addr % 4 == 0):

        return dmem.get(addr,0)
    
    else:

        print("Load address misaligned")


def dmem_store_word(dmem, addr, value):
    """
    TODO
    Store word into data memory.
    Enforce 4-byte alignment.
    """

    if(addr % 4 == 0):

        dmem[addr] = u32(value)

    else:

        print("Store address misaligned")

    pass


# ------------------------------------------------------------
# MEM Stage
# ------------------------------------------------------------

def stage_mem(id_out, ex_out, dmem):
    """
    TODO
    Handle memory access.
        If lw:  read from memory
        If sw:  write to memory
    """
    out = {}
    out["mem_data"] = 0
    out["addr"]     = 0

    if(id_out['c']['MemRead'] == 1):

        out['addr'] = ex_out['alu_res']

        out['mem_data'] = dmem_load_word(dmem,out['addr'])

    elif(id_out['c']['MemWrite'] == 1):

        out["addr"] = ex_out['alu_res']

        dmem_store_word(dmem,out['addr'],id_out['rs2_val'])

        
    return out


# ------------------------------------------------------------
# WB Stage
# ------------------------------------------------------------

def stage_wb(pc_plus4, id_out, ex_out, mem_out, regs):
    """
    TODO
    Writeback stage:
        Determine writeback value.
        Write to register file if RegWrite.
        Ensure x0 always stays 0.
    """
    out = {}
    out["wb_val"]    = 0
    out["wb_rd"]     = 0
    out["did_write"] = False

    if(id_out['c']['RegWrite'] == 1):

        # Jumps

        if(id_out['c']['Jump'] == 1 or id_out['c']['JumpReg']):

            out['wb_val'] = pc_plus4
        
        #Load
        
        elif(id_out['c']['MemToReg'] == 1):

            out['wb_val'] = mem_out['mem_data']
        
        # R + I Types + LUI + AUIPC
        
        else:

            out["wb_val"] = ex_out["alu_res"]
        
        out['wb_rd'] = id_out['d']['rd']
        
        regs[out['wb_rd']] = u32(out['wb_val'])
        
        out['did_write'] = True
    
    return out



# Need inst mnemonic

def get_mnemonic(id_out):

    opcode = id_out['d']['opcode']

    f3 = id_out['d']['funct3']

    f7 = id_out['d']['funct7']

    # R-Type

    if(opcode == 0b0110011):

        if f3 == 0b000 and f7 == 0b0000000:

            return "add"
        
        elif f3 == 0b000 and f7 == 0b0100000:
        
            return "sub"
        
        elif f3 == 0b111 and f7 == 0b0000000:
        
            return "and"
        
        elif f3 == 0b110 and f7 == 0b0000000:
        
            return 'or'
        
        elif f3 == 0b100 and f7 == 0b0000000:
        
            return 'xor'
        
        elif f3 == 0b001 and f7 == 0b0000000:
        
            return 'sll'
        
        elif f3 == 0b101 and f7 == 0b0000000:
        
            return 'srl'
        
        elif f3 == 0b101 and f7 == 0b0100000:
        
            return 'sra'
        
        elif f3 == 0b010 and f7 == 0b0000000:
        
            return 'slt'
        
        elif f3 == 0b011 and f7 == 0b0000000:
        
            return 'sltu'
        
        else:
        
            return None
    
    elif(opcode == 0b0010011):

        if f3 == 0b000:

            return "addi"
        
        elif f3 == 0b111:

            return "andi"
        
        elif f3 == 0b110:
        
            return "ori"
        
        elif f3 == 0b100:
        
            return "xori"
        
        elif f3 == 0b010:
        
            return "slti"
        
        elif f3 == 0b011:
        
            return "sltiu"
        
        if f3 == 0b001 and f7 == 0b0000000:
        
            return "slli"
        
        if f3 == 0b101 and f7 == 0b0000000:
        
            return "srli"
        
        if f3 == 0b101 and f7 == 0b0100000:
        
            return "srai"
        
        return None
    
    elif(opcode == 0b0000011):

        if f3 == 0b010:
            
            return "lw"

    elif(opcode == 0b0100011):

        if f3 == 0b010:

            return "sw"
        
    elif(opcode == 0b1100011):

        mnem = {
        0b000: "beq",
        0b001: "bne",
        0b100: "blt",
        0b101: "bge",
        0b110: "bltu",
        0b111: "bgeu",
        }.get(f3)

        return mnem
    
    elif(opcode == 0b1101111):

        return "jal"
    
    elif(opcode == 0b1100111 and f3 == 0x0):

        return "jalr"
    
    elif(opcode == 0b0110111):

        return "lui"
    
    elif(opcode == 0b0010111):

        return 'auipc'
    
    else:

        return None
# ------------------------------------------------------------
# Trace Generation
# ------------------------------------------------------------

def trace_line(step, if_out, id_out, ex_out, mem_out, wb_out):
    """
    TODO
    Produce readable trace string containing:
        step
        PC
        instruction
        ALU result
        memory access
        register writeback
        next PC
    """

    # Line 1: step, pc, instruction and mnemonic

    line  = f"step={step} | pc=0x{if_out['pc']:08X} | instr=0x{if_out['instr']:08X} | mn={get_mnemonic(id_out)}\n"

    # Line 2: control signals

    line += f"RegW={id_out['c']['RegWrite']} MemR={id_out['c']['MemRead']} MemW={id_out['c']['MemWrite']} ALUSrc={id_out['c']['ALUSrc']} Br={id_out['c']['Branch']}\n"

    # Line 3: ALU operation and result

    line += f"alu={ex_out['alu_op']} res=0x{ex_out['alu_res']:08X}\n"

    # Line 4: writeback

    if wb_out['did_write']:
    
        line += f"wb=x{wb_out['wb_rd']}<-0x{wb_out['wb_val']:08X}\n"

    else:

        line += "wb=---\n"

    # Line 5: next PC
    line += f"next_pc=0x{ex_out['next_pc']:08X}\n"

    return line


# ------------------------------------------------------------
# Program Loader
# ------------------------------------------------------------

def load_imem_from_file(path):
    imem = {}
    pc = 0
    f = open(path)
    for line in f:
        s = line.strip()
        if not s:
            continue
        instr = int(s, 16) & MASK32
        imem[pc] = instr
        pc += 4
    f.close()
    return imem


# ------------------------------------------------------------
# Log Writers
# ------------------------------------------------------------

def write_trace_log(lines):
    f = open("trace.log", "w")
    for l in lines:
        f.write(l + "\n")
    f.close()


def write_regs_log(regs):
    f = open("regs_final.log", "w")
    for i in range(32):
        f.write("x%d = 0x%08X\n" % (i, regs[i]))
    f.close()


def write_dmem_log(dmem):
    f = open("dmem_final.log", "w")
    for a in sorted(dmem.keys()):
        f.write("0x%08X : 0x%08X\n" % (a, dmem[a]))
    f.close()


# ------------------------------------------------------------
# Main Simulation Loop
# ------------------------------------------------------------

def main():
    imem = load_imem_from_file("hex_inst.txt")
    regs = [0] * 32
    dmem = {}
    pc = 0
    steps = 0
    trace_lines = []

    while True:
        if_out = stage_if(pc, imem)
        if if_out["instr"] is None:
            break

        pc_plus4 = if_out["pc_plus4"]
        instr    = if_out["instr"]

        id_out  = stage_id(instr, regs)
        ex_out  = stage_ex(pc, pc_plus4, id_out)
        mem_out = stage_mem(id_out, ex_out, dmem)
        wb_out  = stage_wb(pc_plus4, id_out, ex_out, mem_out, regs)

        trace_lines.append(
            trace_line(steps, if_out, id_out, ex_out, mem_out, wb_out)
        )

        pc = ex_out["next_pc"]
        regs[0] = 0
        steps += 1

    write_trace_log(trace_lines)
    write_regs_log(regs)
    write_dmem_log(dmem)

    print("HALT")
    print("steps =", steps)


if __name__ == "__main__":
    main()
