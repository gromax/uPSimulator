# uPSimulator

**Projet dans le cadre du DU CCIE**

* Chef de projet : Maxence Klein
* Membres du projet :

## Objectifs du projet

L'utilisateur fourni un programme dans un langage structuré de haut niveau.
Le programme convertit ce programme en une version assembleur exécutable sur un microprocesseur virtuel.
L'exécution peut être visualisée en mode pas à pas à l'aide d'une interface graphique.

## Le langage

Le langage respectera une syntaxe voisine de Python :
* Pas de ; en fin de ligne
* Utilisation des indentations comme marquers de blocs

Mots du langage :
* n = input() pour lecture d'un d'un entier saisi au clavier
* print(n) pour affichage d'un entier
* calcul élémentaires sur entier : +, -, *, /, %
* tests : <, >, <=, >=, ==, !=
* logique : and, not, or
* structure if then else
* structure while(condition)

## Le langage assembleur

* *PRINT registre* pour l'affichage à l'écran
* *INPUT registre* pour la lecture clavier d'un entier
* *MOV registre1, registre2* déplacer d'un registre à l'autre
* *LOAD adresse*  pour charger dans un registre fixe le contenu d'un adresse mémoire
* *SAVE adresse* pour écrire le contenu d'un registre fixe dans une adresse mémoire
* Instructions de calcul UAL
* Branchements conditionnels (Si zéro, si négatif, si positif)
* Branchement inconditionnel (GOTO)

## La structure du microprocesseur virtuel

* Quelques registres dont les registres entrée UAL, registre sortie, registre de transfert (lecture/écriture mémoire)
* Une mémoire programme / data
* un accès clavier (lié à la commande INPUT)
* un écran (lié à la commande PRINT)
* une unité de séquencement comportant le pointeur de ligne et registre programme.

## Visualisation

*A minima* :
* état des signaux de commande actifs générés par l'unité de séquencement
*ordres de lecture écriture sur les différents registres, etc.*
* contenu utile de la mémoire
* valeur du pointeur de ligne et registre programme, décodage du contenu du registre programme.
* contenu des registres
* écran d'affichage
* zone de saisie clavier
