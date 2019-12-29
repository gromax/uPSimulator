'''
Gestionnaire d'erreurs
'''

class ExpressionError(Exception):
    def __init__(self, message, errors = None):

        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        # Now for your custom code...
        self.errors = errors

class CompilationError(Exception):
    def __init__(self, message, errors = None):

        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        # Now for your custom code...
        self.errors = errors

class ParseError(Exception):
    def __init__(self, message, errors = None):

        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        # Now for your custom code...
        self.errors = errors

class AttributesError(Exception):
    def __init__(self, message, errors = None):

        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        # Now for your custom code...
        self.errors = errors
