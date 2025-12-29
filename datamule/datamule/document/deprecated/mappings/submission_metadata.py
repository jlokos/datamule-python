"""
Submission metadata field mappings for SEC document processing.

This module provides a mapping dictionary for submission metadata fields
used in SEC EDGAR document headers. The submission_metadata designation
is an internal convention (not an official SEC term) for the header
content within the Submission tag.

Note:
    This module is deprecated. Use the current mappings module instead.
"""

from typing import Dict

#: Mapping of submission metadata field names to their corresponding
#: output field names. Maps SEC submission header fields to standardized
#: field names for downstream processing.
document_submission_metadata_dict: Dict[str, str] = {
    'accession': 'accession',
    'type': 'type',
    'sequence': 'sequence',
    'filename': 'filename',
    'description': 'description'
}
