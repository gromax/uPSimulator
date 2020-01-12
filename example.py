from codeparser import CodeParser
from compilemanager import CompilationManager
from processorengine import ProcessorEngine

tests = [
    'example.code',
    'example2.code'
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
    print(cm16.getAsm())
    print()
    print("Binaire avec la structure 16 bits :")
    print()
    print(cm16.getAsm().getBinary())
    print()


    cm12 = CompilationManager(engine12, structuredList)
    print("Assembleur avec la structure 12 bits :")
    print()
    print(cm12.getAsm())
    print()
    print("Binaire avec la structure 12 bits :")
    print()
    print(cm12.getAsm().getBinary())
    print()
