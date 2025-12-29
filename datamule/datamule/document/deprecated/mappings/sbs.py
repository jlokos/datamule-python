"""SBS (Security-Based Swap Entity) field mappings.

This module provides field name mappings for SBSE (Security-Based Swap Entity)
documents filed with the SEC. SBSE filings contain registration and status
information for security-based swap dealers and major security-based swap
participants.

Supported SEC form types include:
    - SBSE: Application for registration as a security-based swap dealer
    - SBSE-A: Application for registration as a security-based swap dealer
        (amendment)
    - SBSE-BD: Broker-dealer application for registration
    - SBSE-C: Certification for registration
    - SBSE-W: Withdrawal from registration

Note:
    This module is deprecated and currently serves as a placeholder.
    The SBS processing functionality is not yet fully implemented.
    New code should use the updated mapping utilities in the non-deprecated
    mappings module when they become available.

Attributes:
    sbs_dict (dict[str, str]): A dictionary mapping original SBS field
        names (including nested paths using underscores) to normalized,
        flattened field names. Currently empty as mappings are not yet defined.
"""

from typing import Dict

#: Mapping of SBS document field names to normalized field names.
#: This dictionary will be used to transform nested field paths from raw SBSE
#: filings into flattened, consistent field names for data processing.
#: Currently empty as the SBS processing functionality is not yet implemented.
sbs_dict: Dict[str, str] = {}
