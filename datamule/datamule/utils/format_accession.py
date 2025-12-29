"""Utility for formatting SEC accession numbers.

This module provides functionality to convert SEC accession numbers between
different formats: integer, dash-separated, and non-dash formats.

SEC accession numbers are unique identifiers for filings in the EDGAR system,
typically formatted as XXXXXXXXXX-XX-XXXXXX (10 digits, 2 digits, 6 digits).
"""


def format_accession(accession: str | int, format: str) -> str | int:
    """Convert an SEC accession number to the specified format.

    SEC accession numbers can be represented in multiple formats:
    - Integer: A single integer with no separators (e.g., 123456789012345678)
    - Dash format: Standard SEC format with dashes (e.g., 1234567890-12-345678)
    - No-dash format: String without dashes, zero-padded to 18 digits

    Args:
        accession: The accession number to format. Can be provided as a string
            (with or without dashes) or as an integer.
        format: The target format. Must be one of:
            - 'int': Returns the accession as an integer
            - 'dash': Returns the accession in dash-separated format (XX-XX-XXXXXX)
            - 'no-dash': Returns as a zero-padded 18-digit string without dashes

    Returns:
        The formatted accession number. Returns an int if format is 'int',
        otherwise returns a string.

    Raises:
        ValueError: If the format parameter is not one of 'int', 'dash', or 'no-dash'.

    Examples:
        >>> format_accession('0001234567-89-012345', 'int')
        1234567890012345
        >>> format_accession(1234567890012345, 'dash')
        '0001234567-89-012345'
        >>> format_accession('0001234567-89-012345', 'no-dash')
        '000123456789012345'
    """
    if format == 'int':
        accession = int(str(accession).replace('-',''))
    elif format == 'dash':
        accession = str(int(str(accession).replace('-',''))).zfill(18)
        accession = f"{accession[:10]}-{accession[10:12]}-{accession[12:]}"
    elif format == 'no-dash':
        accession = str(int(str(accession).replace('-',''))).zfill(18)
    else:
        raise ValueError("unrecognized format")
    return accession
