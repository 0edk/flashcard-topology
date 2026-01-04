# Flashcard Topology
`flashcard_topology` helps you make complex, scalable note types in Anki and intuitive editors for them.
The library gives a framework for add-ons that abstracts away their common features.

## Usage
1. Download `flashcard_topology` to a subdirectory of where you'll [develop an add-on]( https://addon-docs.ankiweb.net/ ).
2. Write your add-on's `__init__.py` to import the library:
    ```py
    from .flashcard_topology import NoteTopology, TopologyDialog
    ```
3. Make subclasses of `NoteTopology` and `TopologyDialog` for your new note type.
4. From those parent classes, implement all abstract methods.
    See the library's source code for details.
5. At the end of your `__init__.py`:
    ```py
    YourTopology(aqt.mw)
    ```
6. Check your code with [mypy]( https://mypy-lang.org/ ) or the like, early and often.
    It's faster than restarting Anki only to find your add-on's broken.
