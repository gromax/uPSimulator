#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 19:41:27 2019

@author: gdesjouis
"""

# Je n'avais pas pensé aux entêtes, tu as raison, faut mettre des trucs comme ça


from errors import ExpressionError
import re # Tu n'as pas besoin d'expression régulière dans ce code

test=['+',
      ['*',
       [3,[],[]],
       [17,[],[]]
       ],
      ['-',
       [9,[],[]],
       [
        '*',
        ['+',
         [4,[],[]],
         [1,[],[]]
        ],
        ['+',
         [2,[],[]],
         [3,[],[]]
        ]
       ]
      ]
     ]

def leftChild(n):
    # Je ne suis pas sur que n!=[] puisse fonctionner car même si n =[], n=[] et [] feront référence à deux tableaux différents. Il vaut mieux tester len(n) != 0
    if n!=[]:
        return n[1]
    else:
        return []

def rightChild(n):
    # même chose
    if n!=[]:
        return n[2]
    else:
        return []

def isLeaf(n):
    # même chose
    return ((n[1]==[])&(n[2]==[]))

def isUnary(n):
    return (not isLeaf(n))&((n[1]==[])|(n[2]==[]))

def unaryChild(n):
    if not isUnary(n):
            raise ExpressionError(f"pas un opérateur unaire")
    if n[1]!=[]:
        return n[1]
    else:
        return n[2]

def tab2string(n):
    if isLeaf(n):
        return str(n[0])
    else:
        return '('+tab2string(leftChild(n))+str(n[0]) +tab2string(rightChild(n))  +')'

def getRegisterCost(node):
    if isLeaf(node):
        return 1
    elif leftChild(node)==[]:
        return getRegisterCost(rightChild(node))
    elif rightChild(node)==[]:
        return getRegisterCost(leftChild(node))
    else:
        return min(max(getRegisterCost(leftChild(node)),getRegisterCost(rightChild(node))+1),
                    max(getRegisterCost(leftChild(node))+1,getRegisterCost(rightChild(node)))
                    )


def compilationCalcul(node,pileReg,listeOpe):
    print(node[0],pileReg)
    if isLeaf(node):
        if len(disReg) == 0:
            raise ExpressionError(f"Pas de registre disponible'")
        # si je comprends bien, disReg est une variable globale
        # c'est une bonne idée de gérer ainsi les registres
        # mais j'y vois deux défaut : comment gérer les mémoires que l'on devra utiliser en plus
        # et qui sont en nombre inconnu ? Il serait plus pratique d'étiqueter les registres simplement par
        # un nombre. Si tu mets 5 on comprendra que c'est un registre. Un intérêt de faire ainsi est qu'on
        # peut se fixer un N qui représente le nombre de registres dispos en tout
        # et par exemple si N = 3 et qu'on parle du registre 4, on comprend tout de suite
        # que ce n'est pas vraiment un registre mais une case en mémoire
        # Le 2e défaut est qu'il faut absolument passer par des fonctions. Par exemple une fonction
        # getRegistreDispo(), qui peut faire exactement la même chose, mais le fait de nommer ainsi la
        # fonction rend le programme plus lisible
        pileReg.append(disReg.pop())
        # à ce stade de développpement, il vaudrait mieux que listeOp se complète avec
        # des items déjà décodés que l'on pourra traduire ensuite directement en programme
        # par exemple, s'il s'agit de déplacer un littéral dans le registre 1,
        # on peut rentrer le tuple ('litteral -> registre', valeur du litteral, numéro du registre)
        listeOpe.append('MOVE '+str(node[0]) + ' ' + pileReg[ - 1]  )
        # tu peux retourner pileReg et listeOpe mais ce n'est pas indispensable
        # car ces deux listes sont modifiées par la fonction
        # en retournant pileReg, tu retournes en fait une lien vers le tableau
        # et ce lien est le même que celui fourni en argument de la fonction
        return pileReg, listeOpe
    elif isUnary(node):
        # encore une fois, l'affectation ici de pileReg et listeOpe est inutile
        pileReg, listeOpe = compilationCalcul(unaryChild(node),pileReg,listeOpe)
        # pourquoi r1 = pileReg.pop() ?
        # déjà a priori, le registre utilisé devrait être r0
        # car r0 est forcément disponible pour le résultat de ce calcul et donc
        # il est plus naturel que l'opérand soit aussi dans r0 de sorte qu'on n'occupe pas inutilement
        # 2 registres. De plus à l'issu de ce calcul, pileReg diminue de 1 élement, alors que
        # l'opération libère un opérande mais son résultat vient aussitôt occupé un registre
        # le bilan est que la pile des registres occupés ne bouge pas
        # au pire, si on a utilisé r3 comme opérande, cela fait que r3 se libère, et r0 devient occupé
        r1 = pileReg.pop()
        listeOpe.append(str(node[0]) + ' ' + r1 )
        return pileReg, listeOpe
    else:
        if getRegisterCost(leftChild(node))>=getRegisterCost(rightChild(node)):
            # utilise des variables plus explicites, style childToCalcFirst
            Child1=leftChild(node)
            Child2=rightChild(node)
            TokenDirectCalc = True
        else:
            Child2=leftChild(node)
            Child1=rightChild(node)
            TokenDirectCalc = False
        pileReg, listeOpe = compilationCalcul(Child1,pileReg,listeOpe)
        # là encore, utilise de préférence des fonctions comme r0IsAvailable()
        # même si ce n'est que pour faire un test
        if not(isLeaf(Child2)) and 'r0' in pileReg:
            if getRegisterCost(Child2)>len(disReg):
                disReg.append(pileReg.pop())
                # il faudra pouvoir identifier les mémoires, il pourrait y en avoir plusieurs
                # j'aurais tendance à dire qu'elle seront consommées dans l'ordre, leur étiquetage
                # n'est pas forcément indispensable, mais pour pouvoir retrouver les données
                # il faudra savoir à quel mémoire on en est
                pileReg.append('mem')
                listeOpe.append('MOVE ' + disReg[-1] +' mem' )
            else:
                reg = pileReg.pop()
                pileReg.append(disReg.pop())
                disReg.append(reg)
        pileReg, listeOpe = compilationCalcul(Child2,pileReg,listeOpe)
        if len(pileReg)>1:
            if pileReg[-2]=='mem':
                r1 = disReg.pop()
                listeOpe.append('MOVE '+ pileReg.pop(-2) + ' ' + r1 )
                pileReg.append(r1)
        r1 = pileReg.pop()
        disReg.append(r1)
        r2 = pileReg.pop()
        disReg.append(r2)
        if TokenDirectCalc:
            listeOpe.append(str(node[0]) + ' ' + r1 + ' ' + r2)
        else:
            listeOpe.append(str(node[0]) + ' ' + r2 + ' ' + r1)
        pileReg.append(disReg.pop())
        return pileReg, listeOpe
    print(node[0], pileReg)

disReg=['r2','r1','r0']
test2=['*',
       [3,[],[]],
       [17,[],[]]
       ]
maPileReg=[]
maListeOpe=[]
compilationCalcul(test,maPileReg,maListeOpe)

