"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc=0
        self.reg=[0]*7
        self.reg.append(0xF4)
        self.ram=[0]*255
        self.IR=0
        self.sp = 7
        self.MAR=0
        self.MDR=0
        self.FL=0

        self.inst={
            0b10000010:self.LDI,
            0b01000111:self.PRN,
            0b10100010:self.MUL,
            0b01000110:self.pop,
            0b01000101:self.push,
            0b00010001:self.ret,
            0b01010000:self.call,
            0b10100000:self.ADD,
            0b10100111:self.CMP,
            0b01010100:self.JMP,
            0b01010101:self.JEQ,
            0b01010110:self.JNE
        }

        # self.enc={
        #     "LDI":0b10000010,
        #     "PRN":0b01000111,
        #     "HLT":0b00000001
        # }

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        program=[]

        with open(sys.argv[1],'r') as file:
            for line in file:
                get = line.find("#")
                if get>=0:
                    line=line[:get]
                get = line.find('\n')
                if get>=0:
                    line=line[:get]
                if len(line)>1:
                    line=line.strip()
                    program.append(line)

        for instruction in program:
            self.ram[address]=int(instruction,2)
            address+=1
            # register = None
            # extra = None
            # inst = instruction[:3]

            # if len(instruction)>3:
            #     register = int(instruction[5])
            # if len(instruction)>6:
            #     extra = int(instruction[7:])

            # self.ram[address] = self.enc[inst]
            # address += 1
            # if register!=None:
            #     self.ram[address]=register
            #     address+=1
            # if extra:
            #     self.ram[address]=extra
            #     address+=1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
            self.reg[reg_a]%=0b100000000
        elif op == "MUL":
            self.reg[reg_a]*=self.reg[reg_b]
            self.reg[reg_a]%=0b100000000
        elif op =="CMP":
            if self.reg[reg_a]==self.reg[reg_b]:
                self.FL|=1
            else:
                self.FL&=0b11111110
        elif op=="AND":
            self.reg[reg_a]&=self.reg[reg_b]
        elif op=="OR":
            self.reg[reg_a]|=self.reg[reg_b]
        elif op =="XOR":
            self.reg[reg_a]^=self.reg[reg_b]
        elif op=="NOT":
            self.reg[reg_a]^=0b11111111
        elif op=="SHL":
            self.reg[reg_a]<<1
            self.reg[reg_a]%=0b100000000
        elif op=="SHR":
            self.reg[reg_a]>>1
        elif op=="MOD":
            self.reg[reg_a]%=self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        run = True
        while run:
            self.IR = self.ram[self.pc]
            if self.IR==0b00000001:
                run=False
            else:
                self.inst[self.IR]()
                self.pc+=1


    def ram_read(self, MAR):
        return self.ram[MAR]
    
    def ram_write(self, MAR, MDR):
        self.ram[MAR]=MDR
    
    def LDI(self):
        self.pc+=1
        reg = self.ram_read(self.pc)
        self.pc+=1
        val = self.ram_read(self.pc)
        self.reg[reg] = val

    def PRN(self):
        self.pc+=1
        reg = self.ram[self.pc]
        print(self.reg[reg])

    def MUL(self):
        self.pc+=1
        reg1=self.ram_read(self.pc)
        self.pc+=1
        reg2=self.ram_read(self.pc)
        self.alu('MUL',reg1,reg2)

    def push(self):
        self.reg[self.sp]-=1
        self.pc+=1
        reg = self.ram_read(self.pc)
        self.ram_write(self.reg[self.sp], self.reg[reg])
    
    def push_data(self,data):
        self.reg[self.sp]-=1
        self.ram_write(self.reg[self.sp],data)

    def pop_data(self):
        self.MDR=self.ram_read(self.reg[self.sp])
        self.reg[self.sp]+=1

    def pop(self):
        self.pc+=1
        reg = self.ram_read(self.pc)
        data = self.ram_read(self.reg[self.sp])
        self.reg[reg]=data
        self.reg[self.sp]+=1

    def call(self):
        self.pc+=1
        self.push_data(self.pc)
        register=self.ram_read(self.pc)
        data = self.reg[register]
        self.pc=data-1
    
    def ret(self):
        self.pop_data()
        self.pc=self.MDR

    def ADD(self):
        self.pc+=1
        reg1=self.ram_read(self.pc)
        self.pc+=1
        reg2=self.ram_read(self.pc)
        self.alu("ADD",reg1,reg2)

    def ST(self):
        self.pc+=1
        dest=self.ram_read(self.pc)
        self.pc+=1
        src=self.ram_read(self.pc)
        self.ram_write(self.reg[dest],self.reg[src])

    def CMP(self):
        self.pc+=1
        reg1=self.ram_read(self.pc)
        self.pc+=1
        reg2=self.ram_read(self.pc)
        self.alu("CMP",reg1,reg2)

    def JMP(self):
        self.pc+=1
        reg_with_dest = self.ram_read(self.pc)
        self.pc = self.reg[reg_with_dest]
        self.pc-=1
    
    def JNE(self):
        test_against = self.FL & 0b00000001
        if test_against==0:
            self.JMP()
        else:
            self.pc+=1

    def JEQ(self):
        test_against = self.FL & 0b00000001
        if test_against==1:
            self.JMP()
        else:
            self.pc+=1

    def ADDI(self):
        self.pc+=1
        dest = self.ram_read(self.pc)
        self.pc+=1
        to_add = self.ram_read(self.pc)
        self.reg[dest]+=to_add