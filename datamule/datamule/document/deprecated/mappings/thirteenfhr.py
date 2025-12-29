"""Field mapping dictionary for SEC Form 13F-HR filings.

This module provides a mapping dictionary for transforming nested field paths
from SEC Form 13F-HR (Institutional Investment Manager Holdings Report) filings
into simplified, flat field names.

The 13F-HR form is required to be filed quarterly by institutional investment
managers who exercise investment discretion over $100 million or more in
Section 13(f) securities.

The mapping covers:
    - Cover Page fields (filing manager info, report type, amendments)
    - Other Managers Info (CIK, name, CRD number, file numbers)
    - Summary Page fields (confidential omissions, manager counts, totals)
    - Signature Block fields (name, title, phone, signature, date)
    - Header Data fields (period of report, filer credentials, flags)
    - Schema and Metadata fields (schema location, version, accession)

Deprecated:
    This module is deprecated. Use the updated mapping system instead.

Example:
    >>> from datamule.document.deprecated.mappings.thirteenfhr import thirteenfhr_dict
    >>> original_key = 'formData_coverPage_filingManager_name'
    >>> simplified_key = thirteenfhr_dict[original_key]
    >>> print(simplified_key)
    'filingManagerName'
"""

from typing import Dict

#: Field mapping dictionary for 13F-HR (Institutional Investment Manager Holdings) filings.
#: Maps nested field paths to simplified flat field names.
thirteenfhr_dict: Dict[str, str] = {
    # Cover Page Mapping
    'formData_coverPage_reportCalendarOrQuarter': 'reportCalendarOrQuarter',
    'formData_coverPage_filingManager_name': 'filingManagerName',
    'formData_coverPage_filingManager_address_street1': 'filingManagerStreet1',
    'formData_coverPage_filingManager_address_street2': 'filingManagerStreet2',
    'formData_coverPage_filingManager_address_city': 'filingManagerCity',
    'formData_coverPage_filingManager_address_stateOrCountry': 'filingManagerStateOrCountry',
    'formData_coverPage_filingManager_address_zipCode': 'filingManagerZipCode',
    'formData_coverPage_crdNumber': 'crdNumber',
    'formData_coverPage_secFileNumber': 'secFileNumber',
    'formData_coverPage_form13FFileNumber': 'form13FFileNumber',
    'formData_coverPage_reportType': 'reportType',
    'formData_coverPage_isAmendment': 'isAmendment',
    'formData_coverPage_amendmentNo': 'amendmentNo',
    'formData_coverPage_amendmentInfo_amendmentType': 'amendmentType',
    'formData_coverPage_amendmentInfo_confDeniedExpired': 'confDeniedExpired',
    'formData_coverPage_additionalInformation': 'additionalInformation',
    'formData_coverPage_provideInfoForInstruction5': 'provideInfoForInstruction5',
    
    # Other Managers Info Mapping
    'formData_coverPage_otherManagersInfo_otherManager': 'otherManager',
    'formData_coverPage_otherManagersInfo_otherManager_cik': 'otherManagerCik',
    'formData_coverPage_otherManagersInfo_otherManager_name': 'otherManagerName',
    'formData_coverPage_otherManagersInfo_otherManager_crdNumber': 'otherManagerCrdNumber',
    'formData_coverPage_otherManagersInfo_otherManager_secFileNumber': 'otherManagerSecFileNumber',
    'formData_coverPage_otherManagersInfo_otherManager_form13FFileNumber': 'otherManagerForm13FFileNumber',
    
    # Summary Page Mapping
    'formData_summaryPage_isConfidentialOmitted': 'isConfidentialOmitted',
    'formData_summaryPage_otherIncludedManagersCount': 'otherIncludedManagersCount',
    'formData_summaryPage_tableEntryTotal': 'tableEntryTotal',
    'formData_summaryPage_tableValueTotal': 'tableValueTotal',
    
    # Other Managers 2 Info Mapping
    'formData_summaryPage_otherManagers2Info_otherManager2': 'otherManager2',
    'formData_summaryPage_otherManagers2Info_otherManager2_sequenceNumber': 'otherManager2SequenceNumber',
    'formData_summaryPage_otherManagers2Info_otherManager2_otherManager_cik': 'otherManager2Cik',
    'formData_summaryPage_otherManagers2Info_otherManager2_otherManager_name': 'otherManager2Name',
    'formData_summaryPage_otherManagers2Info_otherManager2_otherManager_crdNumber': 'otherManager2CrdNumber',
    'formData_summaryPage_otherManagers2Info_otherManager2_otherManager_secFileNumber': 'otherManager2SecFileNumber',
    'formData_summaryPage_otherManagers2Info_otherManager2_otherManager_form13FFileNumber': 'otherManager2Form13FFileNumber',
    
    # Signature Block Mapping
    'formData_signatureBlock_name': 'signatureName',
    'formData_signatureBlock_title': 'signatureTitle',
    'formData_signatureBlock_phone': 'signaturePhone',
    'formData_signatureBlock_signature': 'signature',
    'formData_signatureBlock_city': 'signatureCity',
    'formData_signatureBlock_stateOrCountry': 'signatureStateOrCountry',
    'formData_signatureBlock_signatureDate': 'signatureDate',
    
    # Header Data Mapping
    'headerData_filerInfo_periodOfReport': 'periodOfReport',
    'headerData_filerInfo_filer_fileNumber': 'filerFileNumber',
    'headerData_filerInfo_filer_credentials_cik': 'filerCik',
    'headerData_filerInfo_filer_credentials_ccc': 'filerCcc',
    'headerData_filerInfo_flags_confirmingCopyFlag': 'confirmingCopyFlag',
    'headerData_filerInfo_flags_returnCopyFlag': 'returnCopyFlag',
    'headerData_filerInfo_flags_overrideInternetFlag': 'overrideInternetFlag',
    'headerData_filerInfo_denovoRequest': 'denovoRequest',
    'headerData_filerInfo_liveTestFlag': 'liveTestFlag',
    'headerData_submissionType': 'submissionType',
    
    # Schema and Metadata Mapping
    'schemaLocation': 'schemaLocation',
    'schemaVersion': 'schemaVersion',
    'accession': 'accessionNumber'
}