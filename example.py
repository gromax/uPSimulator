from codeparser import CodeParser
from compilemanager import CompilationManager
from processorengine import ProcessorEngine

testCode = '''
s = 0
i = 0
m = input()
while i < m:
    if i % 2 == 0:
        s = s + i
        if s < 10:
            y = s * 2
            print(y)
    x = i + 3
print(s)
'''

print("programme original :")
print()
print(testCode)
print()

engine16 = ProcessorEngine()
engine12 = ProcessorEngine("12bits")
cp = CodeParser(code = testCode)
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
