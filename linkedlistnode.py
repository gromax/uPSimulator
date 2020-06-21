"""
.. module:: linkedlistnode
   :synopsis: définition d'un noeud de liste doublement chaînée
"""

from typing import Optional, Union, List

class LinkedList:
    _head: Optional["LinkedListNode"] = None
    def __init__(self, items:List["LinkedListNode"]):
        """
        attention : les noeuds doivent être "neufs"
        Si les noeud étaient déjà inserrés dans une liste,
        on pourrait avoir des problèmes
        """
        if len(items) == 0:
            return
        self._head = items[0]
        lastInserted = self._head
        for item in items[1:]:
            lastInserted._next = item
            item._prev = lastInserted
            lastInserted = item
        lastInserted._next = self._head
        self._head._prev = lastInserted

    @property
    def head(self) -> Optional["LinkedListNode"]:
        """Accesseur

        :return: pointeur sur la tête
        :rtype: Optional["LinkedListNode"]
        """
        return self._head

    @property
    def length(self) -> int:
        """propriété

        :return: nombre d'item de la liste
        :rtype: int
        """
        if self._head is None:
            return 0
        count = 1
        node = self._head
        while node._next != self._head:
            node = node._next
            count += 1
        return count

    def delete(self, nodeToDel:"LinkedListNode") -> bool:
        """supprime l'élément node

        :param nodeToDel: élément à supprimer
        :type nodeToDel: LinkedListNode
        :return: suppression effectuée
        :rtype: bool
        """
        if self._head is None:
            return False
        if self._head == nodeToDel and self._head._next == self._head:
            # seul élément de la liste
            self._head = None
            return True
        node = self._head
        while node != nodeToDel and node._next != self._head:
            node = node._next
        if node != nodeToDel:
            return False
        nodeNext = nodeToDel._next
        nodeToDel._prev._next = nodeToDel._next
        nodeToDel._next._prev = nodeToDel._prev
        nodeToDel._next = nodeToDel
        nodeToDel._prev = nodeToDel
        if self._head == nodeToDel:
            self._head = nodeNext
        return True

    def has(self, nodeToSearch:"LinkedListNode") -> bool:
        """
        :param nodeToSearch: noeud cherché
        :type nodeToSearch: LinkedListNode
        :return: la liste contient le noeud
        :rtype: bool
        """
        if self._head is None:
            return False
        if self ._head == nodeToSearch:
            return True
        node = self._head._next
        while node != nodeToSearch and node._next != self._head:
            node = node._next
        return node == nodeToSearch

    def replace(self, nodeToReplace:"LinkedListNode", listToInsert:Union["LinkedList", "LinkedListNode"]) -> "LinkedList":
        """remplace l'élément par une liste

        :param nodeToReplace: noeud à remplacer
        :type nodeToReplace: LinkedListNode
        :param listToInsert: liste à insérer à la place
        :type: Union["LinkedList", "LinkedListNode"]
        :return: liste ayant subit l'insertion
        :rtype: LinkedList
        """
        if not self.has(nodeToReplace):
            return self
        nodeToReplace.insertRight(listToInsert)
        self.delete(nodeToReplace)
        return self

    def toList(self) -> List['LinkedListNode']:
        """Produit une liste des items enfants

        :return: liste des noeuds
        :rtype: List[LinkedListNode]
        """
        if self._head is None:
            return []
        outputList = [self._head]
        node = self._head
        while node._next != self._head:
            node = node._next
            outputList.append(node)
        return outputList

    def append(self, listToAppend:Union['LinkedListNode', 'LinkedList']) -> None:
        """ajoute le contenu de listToAppend à la suite, listToAppend s'en trouve vidée

        :param listToAppend: liste à ajouter
        :type listToAppend: Union['LinkedListNode', 'LinkedList']
        """
        if self._head is None:
            if isinstance(listToAppend, LinkedList):
                self._head = listToAppend._head
                listToAppend._head = None
                return
            else:
                self._head = listToAppend
        self._head._prev.insertRight(listToAppend)


class LinkedListNode:
    _next: "LinkedListNode"
    _prev: "LinkedListNode"
    def __init__(self):
        self._next = self
        self._prev = self
        pass

    @property
    def next(self) -> "LinkedListNode":
        """Accesseur

        :return: noeud suivant
        :rtype: LinkedListNode
        """
        return self._next

    def __str__(self) -> str:
        """Transtypage str
        :return: version texte
        :rtype: str
        """
        return "<LinkedListNode>"

    def insertRight(self, toInsert:Union["LinkedList", "LinkedListNode"]) -> "LinkedListNode":
        """Insert un noeud ou tout une chaîne à droite

        :param toInsert: point de départ de la chaîne à inserrer
        :type toInsert: Union["LinkedList", "LinkedListNode"]
        :return: noeud courant
        :rtype:: LinkedListNode
        """
        if isinstance(toInsert, LinkedList):
            nodeToInsert = toInsert._head
            toInsert._head = None
        else:
            nodeToInsert = toInsert
        if nodeToInsert is None:
            return self
        self._next._prev =  nodeToInsert._prev
        nodeToInsert._prev._next = self._next
        nodeToInsert._prev = self
        self._next = nodeToInsert
        return self

    def insertLeft(self, toInsert:Union["LinkedList", "LinkedListNode"]) -> "LinkedListNode":
        """Insert un noeud ou tout une chaîne à gauche

        :param toInsert: point de départ de la chaîne à inserrer
        :type toInsert: Union["LinkedList", "LinkedListNode"]
        :return: noeud tête de l'insertion
        :rtype:: LinkedListNode
        """
        if isinstance(toInsert, LinkedList):
            nodeToInsert = toInsert._head
            toInsert._head = None
        else:
            nodeToInsert = toInsert
        if nodeToInsert is None:
            return self
        self._prev._next = nodeToInsert
        nodeToInsert._prev._next = self
        currentPrev = self._prev
        self._prev = nodeToInsert._prev
        nodeToInsert._prev = currentPrev
        return nodeToInsert

