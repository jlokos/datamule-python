"""
Utility functions for table data processing.

This module provides helper functions for safely accessing nested dictionary
structures and flattening hierarchical data, commonly used when processing
SEC filing data for tabular output.
"""

from typing import Any, Dict, List, Optional, Union


def safe_get(d: Dict[str, Any], keys: List[str], default: Optional[Any] = None) -> Any:
    """
    Safely access nested dictionary keys without raising KeyError.

    Traverses a nested dictionary structure using a sequence of keys,
    returning a default value if any key in the path is missing or
    if an intermediate value is not a dictionary.

    Args:
        d: The dictionary to traverse.
        keys: A list of keys representing the path to the desired value.
        default: The value to return if the path cannot be traversed.
            Defaults to None.

    Returns:
        The value at the specified path, or the default value if the
        path is invalid or any key is missing.

    Examples:
        >>> data = {'a': {'b': {'c': 1}}}
        >>> safe_get(data, ['a', 'b', 'c'])
        1
        >>> safe_get(data, ['a', 'x', 'c'], default='not found')
        'not found'
    """
    current = d
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def flatten_dict(
    d: Union[Dict[str, Any], List[Dict[str, Any]]], parent_key: str = ''
) -> Union[Dict[str, str], List[Dict[str, str]]]:
    """
    Flatten a nested dictionary into a single-level dictionary.

    Recursively traverses nested dictionary structures, converting them
    to a flat dictionary with compound keys separated by underscores.
    All values are converted to strings in the output.

    If a list of dictionaries is provided, each dictionary in the list
    is flattened individually.

    Args:
        d: A dictionary to flatten, or a list of dictionaries to flatten
            individually.
        parent_key: Prefix to prepend to keys at this level. Used internally
            for recursive calls to build compound key names. Defaults to
            empty string.

    Returns:
        A flattened dictionary with underscore-separated compound keys
        and string values, or a list of such dictionaries if the input
        was a list.

    Examples:
        >>> flatten_dict({'a': {'b': 1, 'c': 2}})
        {'a_b': '1', 'a_c': '2'}
        >>> flatten_dict([{'x': 1}, {'y': 2}])
        [{'x': '1'}, {'y': '2'}]

    Note:
        This implementation may be modified in the future to better
        handle list values within dictionaries.
    """
    items: Dict[str, str] = {}

    if isinstance(d, list):
        return [flatten_dict(item) for item in d]

    for k, v in d.items():
        new_key = f"{parent_key}_{k}" if parent_key else k

        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key))
        else:
            items[new_key] = str(v)

    return items