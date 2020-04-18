'''
.. module:: errors
:synopsis: classes d'erreurs

.. note:: Les erreurs viennent avec un attribut errors, un dictionnaire
    qui est renseigné quand l'erreur est levé. Lors de la compulation, on
    transmet notamment le champ "lineNumber" permettant d'indiquer à quelle
    ligne l'erreur a été commise.
'''

class ExpressionError(Exception):
    '''
    Erreur levée quand une expression arithmétique ou logique ne convient pas
    '''
    def __init__(self, message, errors = None):

        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        # Now for your custom code...
        self.errors = errors

class CompilationError(Exception):
    '''
    Erreur levée quand la compilation n'aboutit pas
    '''
    def __init__(self, message, errors = None):

        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        # Now for your custom code...
        self.errors = errors

class ParseError(Exception):
    '''
    Erreur levée quand une ligne de programme ne peut pas être interprétée
    '''
    def __init__(self, message, errors = None):

        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        # Now for your custom code...
        self.errors = errors

class AttributesError(Exception):
    '''
    Erreur levée quand le modèle de processeur n'a pas des options valables
    '''
    def __init__(self, message, errors = None):

        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        # Now for your custom code...
        self.errors = errors
