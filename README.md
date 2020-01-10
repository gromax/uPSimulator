# uPSimulator

**Projet dans le cadre du DU CCIE**

* Chef de projet : Maxence Klein
* Membres du projet : Véronique Reynauld, Guillaume Desjouis

## Objectifs du projet

L'utilisateur fourni un programme dans un langage structuré de haut niveau.
Le programme convertit ce programme en une version **assembleur** exécutable sur un **microprocesseur virtuel**.
L'exécution peut être visualisée en mode pas à pas à l'aide d'une **interface graphique**.

## Le langage

Le langage respectera une syntaxe voisine de Python :
* Pas de ; en fin de ligne
* Pas de ( ) autour des conditions
* Utilisation des indentations comme marqueurs de blocs
* Utilisation de : en amont de chaque bloc

Mots du langage :
* n = input() pour lecture d'un d'un entier saisi au clavier
* print(3*x + 5) pour affichage du résultat d'une formule arithmétique
* calcul élémentaires sur entier : +, -, *, /, %
* opérateurs logiques bitwise sur entiers : &, |, ^, ~
* tests : <, >, <=, >=, ==, !=
* logique : and, not, or
* structure if elif else
* structure while

## Le langage assembleur

langage pouvant être adapté selon un modèle fourni dans le paramétrage.
Le modèle par défaut retenu utilise :

* *PRINT registre* pour l'affichage à l'écran
* *INPUT registre* pour la lecture clavier d'un entier
* *MOV registreCible, registreSource* déplacer d'un registre à l'autre
* *LOAD registreCible, mémoire*  pour charger dans un registre le contenu d'une variable en mémoire
* *STORE registreSource, mémoire* pour écrire le contenu d'un registre dans une variable mémoire
* Instructions de calcul UAL, par exemple *ADD registreCible, registre1, registre2*
* Branchements conditionnels. Par exemple *BGT cible*
* Branchement inconditionnel : *GOTO*
* Possibilité d'indiquer un littéral directement dans une commande de calcul : *ADD registreCible, registre1, #litteral*
* Possibilité de transfert d'un littéral dans un registre : *MOVE registreCible, #littéral*

Le paramétrage indique les noms des commandes ainsi que leur structure et leur code binaire.
Quelques exemples :
* On peut paramétrer pour que les opérations UAL aient toujours le registre 0 comme cible si bien que la commande devient *ADD registre1, registre2*
* On peut n'autoriser les littéraux que dans certaines commandes ou aucune
* Quand un littéral est trop grand pour entrer dans une commande, on peut au choix le placer automatiquement en ligne suivante (alors l'exécution nécessitera un temps de lecture de la ligne suivante) ou en mémoire (comme une variable, la lecture du litteral passera par un *LOAD*)
* Choix du nombre de registres
* Choix de la taille d'un mot de donnée / programme
* L'absence d'une commande dans le modèle (par exemple : pas de *INPUT*) n'entraîne une erreur que si l'utilisateur fait appel à cette commande.

## La structure du microprocesseur virtuel

* Banc de registres ayant accès à l'UAL
* Une mémoire programme / data avec un registre d'adresse
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
