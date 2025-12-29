"""
Transfer Agent (TA) field mappings for SEC document processing.

This module provides mapping dictionaries for SEC Transfer Agent form fields.
Transfer Agent forms (TA-1, TA-2, TA-W) are used by transfer agents to register
with the SEC, file annual reports, and request withdrawal from registration.

Note:
    This module is deprecated. New code should use updated mapping implementations.

Warning:
    This module is currently a placeholder. Transfer Agent mapping dictionaries
    will be populated as the TA form processing functionality is implemented.

See Also:
    - SEC Transfer Agent Registration: https://www.sec.gov/divisions/marketreg/mrtransfer.shtml
    - Form TA-1: Application for Registration as a Transfer Agent
    - Form TA-2: Annual Report of Transfer Agent Activities
    - Form TA-W: Notice of Withdrawal from Registration as Transfer Agent
"""

from typing import Dict


#: Mapping dictionary for Transfer Agent metadata fields.
#: Maps internal field names to standardized output field names.
#: Currently empty - to be populated as TA form processing is implemented.
metadata_ta_dict: Dict[str, str] = {}

#: Mapping dictionary for Transfer Agent registration fields (Form TA-1).
#: Maps internal field names to standardized output field names.
#: Currently empty - to be populated as TA form processing is implemented.
registration_ta_dict: Dict[str, str] = {}

#: Mapping dictionary for Transfer Agent annual report fields (Form TA-2).
#: Maps internal field names to standardized output field names.
#: Currently empty - to be populated as TA form processing is implemented.
annual_report_ta_dict: Dict[str, str] = {}

#: Mapping dictionary for Transfer Agent withdrawal fields (Form TA-W).
#: Maps internal field names to standardized output field names.
#: Currently empty - to be populated as TA form processing is implemented.
withdrawal_ta_dict: Dict[str, str] = {}
