def pytest_itemcollected(item):
    """Use the test docstring (if available) as the node ID.

    The node ID is printed for each test; by default this is in the format
    filename::classname::function. If available, use the docstring instead as
    this is more readable.

    """
    node = item.obj
    item._nodeid = node.__doc__.strip() if node.__doc__ else node.__name__
