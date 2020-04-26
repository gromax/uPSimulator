from codeparser import CodeParser
from compilemanager import CompilationManager
from processorengine import ProcessorEngine


import unittest



class CompilationTest(unittest.TestCase):
    def setUp(self):
        self.engine16 = ProcessorEngine()
        self.engine12 = ProcessorEngine("12bits")


    def test_affectation_16bits(self):
        programme = "x=3"
        cp = CodeParser(code = programme)
        structuredList = cp.getFinalStructuredList()
        cm = CompilationManager(self.engine16, structuredList)

        goodAsm = [
            "\tMOVE r0, #3",
            "\tSTORE r0, @x",
            "\tHALT",
            "@x\t0"
        ]
        assert str(cm.asm) == "\n".join(goodAsm)

        goodBinary = [
            "0100100000000011", # MOVE = 01001, r0 = 000, #3 = 00000011
            "0111000000000011", # STORE = 0111, r0 = 000, @x = 3 = 000000011
            "0000000000000000", # HALT = 00000 + bourrage de 0
            "0000000000000000"  # var x, @x = 3
        ]
        assert cm.asm.getBinary() == "\n".join(goodBinary)

    def test_affectation_12bits(self):
        programme = "x=3"
        cp = CodeParser(code = programme)
        structuredList = cp.getFinalStructuredList()
        cm = CompilationManager(self.engine12, structuredList)

        goodAsm = [
            "\tLOAD r0, @3",
            "\tSTORE r0, @x",
            "\tHALT",
            "@3\t3",
            "@x\t0"
        ]
        assert str(cm.asm) == "\n".join(goodAsm)

        goodBinary = [
            "100000000011",
            "101000000100",
            "000000000000",
            "000000000011",
            "000000000000",
        ]

        assert cm.asm.getBinary() == "\n".join(goodBinary)

    def test_example_1_16bits(self):
        filename = 'example.code'
        cp = CodeParser(filename = filename)
        structuredList = cp.getFinalStructuredList()
        cm = CompilationManager(self.engine16, structuredList)

        goodAsm = [
            "\tMOVE r0, #0",
            "\tSTORE r0, @x",
            "\tMOVE r0, #0",
            "\tSTORE r0, @y",
            "l1\t",
            "\tLOAD r0, @x",
            "\tMOVE r1, #10",
            "\tCMP r0, r1",
            "\tBLT l2",
            "\tLOAD r0, @y",
            "\tLOAD r1, @2500",
            "\tCMP r0, r1",
            "\tBLT l2",
            "\tJMP l3",
            "l2\t",
            "\tLOAD r0, @x",
            "\tADD r0, r0, #1",
            "\tSTORE r0, @x",
            "\tLOAD r0, @y",
            "\tLOAD r1, @x",
            "\tADD r0, r0, r1",
            "\tSTORE r0, @y",
            "\tJMP l1",
            "l3\t",
            "\tLOAD r0, @y",
            "\tPRINT r0",
            "\tHALT",
            "@2500\t2500",
            "@x\t0",
            "@y\t0"
        ]

        assert str(cm.asm) == "\n".join(goodAsm)

        goodBinary = [
            "0100100000000000",
            "0111000000011001",
            "0100100000000000",
            "0111000000011010",
            "0011000000011001",
            "0100100100001010",
            "0001100000100000",
            "0001010000001101",
            "0011000000011010",
            "0011001000011000",
            "0001100000100000",
            "0001010000001101",
            "0000100000010101",
            "0011000000011001",
            "1000000000000001",
            "0111000000011001",
            "0011000000011010",
            "0011001000011001",
            "0110000000000001",
            "0111000000011010",
            "0000100000000100",
            "0011000000011010",
            "0010000000000000",
            "0000000000000000",
            "0000100111000100",
            "0000000000000000",
            "0000000000000000"
        ]

        assert cm.asm.getBinary() == "\n".join(goodBinary)



if __name__ == "__main__":
    #unittest.main()


    tests = [
        'example2.code',
        'example.code'
    ]

    engine16 = ProcessorEngine()
    engine12 = ProcessorEngine("12bits")

    for testFile in tests:
        print("#### Fichier "+testFile)
        cp = CodeParser(filename = testFile)
        structuredList = cp.getFinalStructuredList()

        print("Programme structuré :")
        print()
        for item in structuredList:
            print(item)
        print()

        cm16 = CompilationManager(engine16, structuredList)
        print("Assembleur avec la structure 16 bits :")
        print()
        print(cm16.asm)
        print()
        print("Binaire avec la structure 16 bits :")
        print()
        print(cm16.asm.getBinary())
        print()


        cm12 = CompilationManager(engine12, structuredList)
        print("Assembleur avec la structure 12 bits :")
        print()
        print(cm12.asm)
        print()
        print("Binaire avec la structure 12 bits :")
        print()
        print(cm12.asm.getBinary())
        print()

