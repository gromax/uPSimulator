import sys
from errors import *
from lineparser import *



if __name__=="__main__":

    if len(sys.argv) > 1:
        fileName = sys.argv[1]
    else:
        fileName = "example.py"

    # Lecture de toutes les lignes du fichier
    file = open(fileName, "r")
    lines = file.readlines()
    file.close()

    #Instanciation VariableManager
    VM = VariableManager()

    #liste des éléments sous forme d'un dictionnaire post traitement des lignes
    listingCode = []

    #On boucle sur les lignes
    for num, line in enumerate(lines):

        objDictLine = {}
        objLine = LineParser(line,num)

        #Uniquement si ligne parsée correctement
        if objLine.result :

            #Ajout des éléments communs
            objDictLine['type'] = objLine.type
            objDictLine['lineNumber'] = objLine.lineNumber
            objDictLine['indent'] = objLine.indent

            if objLine.type == 'print':
                objDictLine['expression'] = objLine.expression

            elif objLine.type == 'input' or objLine.type == 'affectation':
                objDictLine['variable'] = VM.addVariableByName(objLine.variable)
                objDictLine['expression'] = objLine.expression #A voir si utile

            elif objLine.type in ['while','if','elif']:
                objDictLine['condition'] = objLine.condition

            elif objLine.type == 'else':
                pass

            else:
                raise ExpressionError(f"Type <{objLine.type}> non traitée !")

            #Ajout des informations parsées dans le listing
            listingCode.append(objDictLine)

    #Parcours du listing pour ranger les enfants









    print(listingCode)


# #Exemple pour tester LineParser
# txt = '    while ( A < B) : #comment'
# #txt = 'if (A==B):'
# # txt = 'print("coucou")  #comment'
# ## txt = 'A=" mon  texte "' #buildExpression ne traite pas les string ""
# # txt = 'A=A+1  #comment'
# # txt = 'variable = input("valeur ?")'
#
# ligne = LineParser(txt,1)
# print(f"indent : {ligne.indent}")
# print(f"lineNumber : {ligne.lineNumber}")
# print(f"type : {ligne.type}")
# print(f"result : {ligne.result}")
# print(f"condition : {ligne.condition}")
# print(f"variable : {ligne.variable}")
# print(f"expression : {ligne.expression}")
