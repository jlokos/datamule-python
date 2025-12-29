"""
Deprecated mapping dictionary for EX-99.A SDR (Security-Based Swap Data Repository) filings.

This module provides a mapping dictionary for parsing and processing SEC EX-99.A
filings related to Security-Based Swap Data Repositories. These filings are
exhibits to Form SDR, which is used by security-based swap data repositories
to register with the SEC.

.. deprecated::
    This module is deprecated and maintained for backward compatibility only.
    Use the updated mapping implementations in the non-deprecated mappings package.

Attributes:
    ex99a_sdr_dict (dict): A dictionary mapping field names to their corresponding
        values or parsing rules for EX-99.A SDR exhibit documents. Currently empty
        as the mapping structure is defined elsewhere or has been superseded.
"""

from typing import Dict, Any

ex99a_sdr_dict: Dict[str, Any] = {}