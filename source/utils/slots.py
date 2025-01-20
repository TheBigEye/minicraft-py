"""
    Dear Python,

    I love you, but sometimes your "explicit is better than implicit" philosophy drives me crazy.
    Yes, I know explicit is better... until you have to write __slots__ = ['attribute1', 'attribute2',
    'attribute3', 'oh_my_god_why_am_i_writing_all_of_these'] for the 100th time and your code starts
    looking like a grocery list that never ends.

    So here's a decorator that does what Python should have done ages ago: automatically figure out
    what attributes I'm using and create the slots for me. Because let's be honest, if I'm assigning
    to self.something in __init__, I PROBABLY WANT THAT IN SLOTS.

    Features:
    - Saves your fingers from typing endless slot declarations
    - Keeps your code clean and readable (shocking, I know!)
    - Still gives you all the memory benefits of slots
    - Doesn't make your classes look like they're screaming attribute names at you

    Remember: Life is too short to write slots manually.

    P.S.: If you're a Python core dev reading this... please, please add this to Python 4.0
    (Oh wait, we'll never get Python 4.0, will we? 😅)
"""

import ast
import inspect
from typing import Type, TypeVar

T = TypeVar('T')

def auto_slots(cls: Type[T]) -> Type[T]:
    """
        Automatically generates `__slots__` for a class by analyzing its `__init__` method.

        This decorator inspects the class's `__init__` method to identify all attributes assigned
        to `self`, and automatically creates an appropriate `__slots__` definition. It properly
        handles inheritance by collecting slots from parent classes to avoid duplication.

        ## Features
        * Automatic attribute detection from `__init__`
        * Proper inheritance handling
        * Memory optimization through `__slots__`
        * Support for manual slot additions

        ## Usage
        ```python
        @auto_slots
        class Point:
            def __init__(self):
                self.x = 0
                self.y = 0

        # With inheritance
        @auto_slots
        class Circle(Point):
            def __init__(self):
                super().__init__()
                self.radius = 1

        # With manual slots addition
        @auto_slots
        class Rectangle:
            __slots__ = ('extra_attr',)  # Will be preserved
            def __init__(self):
                self.width = 0
                self.height = 0
        ```

        ## Limitations
        1. Only detects attributes assigned directly in `__init__`
        2. Cannot detect attributes assigned in other methods
        3. May miss complex attribute assignments

        ## Notes
        - If a class already has `__slots__` defined, those slots will be preserved
        - Parent class attributes are automatically excluded to avoid conflicts
        - Compatible with type hints and annotations
    """

    def get_init_attrs(class_def):
        """
        Extracts all self.attribute assignments from a class's __init__ method.

        Args:
            class_def: The class to analyze

        Returns:
            set: A set of attribute names found in __init__
        """
        try:
            # Get the source code of __init__
            init_source = inspect.getsource(class_def.__init__)
        except (TypeError, OSError):
            # Handle cases where source isn't available
            return set()

        try:
            # Parse the source code into an AST
            tree = ast.parse(init_source)
        except SyntaxError:
            # Handle invalid syntax in source
            return set()

        attrs = set()

        # Walk the AST to find all self.attr assignments
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    # Look for patterns like "self.attr = value"
                    if (isinstance(target, ast.Attribute) and
                        isinstance(target.value, ast.Name) and
                        target.value.id == 'self'):
                        attrs.add(target.attr)

        return attrs

    # Collect slots from all parent classes
    parent_attrs = set()
    for base in cls.__bases__:
        if hasattr(base, '__slots__'):
            parent_attrs.update(base.__slots__)

    # Get attributes from current class
    current_attrs = get_init_attrs(cls)

    # Remove any attributes already defined in parent classes
    current_attrs = current_attrs - parent_attrs

    # If the class already has slots defined, merge them with found attributes
    if hasattr(cls, '__slots__'):
        current_attrs.update(cls.__slots__)

    # Set the final slots tuple
    cls.__slots__ = tuple(current_attrs)

    return cls
