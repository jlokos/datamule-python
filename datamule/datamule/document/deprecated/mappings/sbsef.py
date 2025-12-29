"""SBSEF (Security-Based Swap Execution Facility) field mappings.

This module provides field name mappings for SBSEF (Security-Based Swap
Execution Facility) documents filed with the SEC. SBSEF filings contain
registration and status information for swap execution facilities.

Note:
    This module is deprecated. New code should use the updated mapping
    utilities in the non-deprecated mappings module.

Attributes:
    sbsef_dict (dict[str, str]): A dictionary mapping original SBSEF field
        names (including nested paths using underscores) to normalized,
        flattened field names. Keys represent the source field paths
        (e.g., 'filerInfo_filer_filerCredentials_ccc') and values represent
        the simplified target field names (e.g., 'filerCredentialsCcc').
"""

from typing import Dict

#: Mapping of SBSEF document field names to normalized field names.
#: This dictionary is used to transform nested field paths from raw SBSEF
#: filings into flattened, consistent field names for data processing.
sbsef_dict: Dict[str, str] = {
    'sbsefId': 'sbsefId',
    'sbsefName': 'sbsefName',
    'sbsefRegistrationDate': 'sbsefRegistrationDate',
    'sbsefStatus': 'sbsefStatus',
    'sbsefContactInfo': 'sbsefContactInfo',
    'filerInfo_filer_filerCredentials_ccc': 'filerCredentialsCcc',
    'filerInfo_filer_filerCredentials_cik': 'filerCredentialsCik',
    'filerInfo_flags_overrideInternetFlag': 'overrideInternetFlag',
    'filerInfo_liveTestFlag': 'liveTestFlag',
    'submissionType': 'submissionType'
}
