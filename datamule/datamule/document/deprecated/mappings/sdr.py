"""
SDR (Security-based Swap Data Repository) field mappings module.

This module provides field name mappings for SEC Form SDR filings, which are used
for registration and amendment of Security-based Swap Data Repositories under
the Securities Exchange Act of 1934.

The mappings transform verbose nested field paths from the original XML/JSON
structure into simplified, more readable field names for data processing and
analysis.

Deprecated:
    This module is deprecated. Use the updated mappings in the non-deprecated
    mappings package instead.

Attributes:
    sdr_dict (Dict[str, str]): A dictionary mapping original SDR form field paths
        to simplified field names. Keys are dot-separated paths representing the
        nested structure of form data, values are the simplified field names.
    config_sdr (Dict[str, Dict[str, Any]]): Configuration dictionary containing
        the XML path and field mapping for SDR form processing.

Example:
    >>> from datamule.document.deprecated.mappings.sdr import sdr_dict, config_sdr
    >>> # Get simplified name for a field
    >>> sdr_dict['formData_generalInfo_business_businessAddress_city']
    'businessCity'
"""

from typing import Any, Dict

sdr_dict: Dict[str, str] = {
    'formData_generalInfo_applicantCategory_applcntTypeConfFlag': 'applicantTypeConfFlag',
    'formData_generalInfo_applicantCategory_applicantType': 'applicantType',
    'formData_generalInfo_applicantCategory_applicantTypeOtherDesc': 'applicantTypeOtherDesc',
    'formData_generalInfo_assetClasses_assetClassesConfFlag': 'assetClassesConfFlag',
    'formData_generalInfo_assetClasses_assetClassesList': 'assetClassesList',
    'formData_generalInfo_business_businessAddress_businessAddressConfFlag': 'businessAddressConfFlag',
    'formData_generalInfo_business_businessAddress_city': 'businessCity',
    'formData_generalInfo_business_businessAddress_stateOrCountry': 'businessStateOrCountry',
    'formData_generalInfo_business_businessAddress_street1': 'businessStreet1',
    'formData_generalInfo_business_businessAddress_zipCode': 'businessZipCode',
    'formData_generalInfo_business_businessName_nameOnBusinessConfFlag': 'nameOnBusinessConfFlag',
    'formData_generalInfo_business_previousBusinessName_previousBusinessNameConfFlag': 'previousBusinessNameConfFlag',
    'formData_generalInfo_consentAddress_city': 'consentCity',
    'formData_generalInfo_consentAddress_consentAddressConfFlag': 'consentAddressConfFlag',
    'formData_generalInfo_consentAddress_stateCountry': 'consentStateCountry',
    'formData_generalInfo_consentAddress_street1': 'consentStreet1',
    'formData_generalInfo_consentAddress_zipCode': 'consentZipCode',
    'formData_generalInfo_consentName_applicantNameOrApplcblEntity': 'applicantNameOrApplcblEntity',
    'formData_generalInfo_consentName_consentNameConfFlag': 'consentNameConfFlag',
    'formData_generalInfo_consentName_personNameOrOfficerTitle': 'personNameOrOfficerTitle',
    'formData_generalInfo_consentPhone_consentPhoneConfFlag': 'consentPhoneConfFlag',
    'formData_generalInfo_consentPhone_phone': 'consentPhone',
    'formData_generalInfo_corpOrgInfo_corprtnOrgConfFlag': 'corporationOrgConfFlag',
    'formData_generalInfo_corpOrgInfo_dateOfCoperationOrg': 'dateOfCooperationOrg',
    'formData_generalInfo_corpOrgInfo_stateCorperationOrOrg': 'stateCorporationOrOrg',
    'formData_generalInfo_functionDescription_functionDescriptionConfFlag': 'functionDescriptionConfFlag',
    'formData_generalInfo_functionDescription_functionDescriptionPerformed': 'functionDescriptionPerformed',
    'formData_generalInfo_officeInfo_officeConfFlag': 'officeConfFlag',
    'formData_generalInfo_officeInfo_office_city': 'officeCity',
    'formData_generalInfo_officeInfo_office_officeName': 'officeName',
    'formData_generalInfo_officeInfo_office_stateOrCountry': 'officeStateOrCountry',
    'formData_generalInfo_officeInfo_office_street1': 'officeStreet1',
    'formData_generalInfo_officeInfo_office_zipCode': 'officeZipCode',
    'formData_generalInfo_partnershipInfo_filingPrtnrConfFlag': 'filingPartnerConfFlag',
    'formData_generalInfo_successor_predecessorCikFlag': 'predecessorCikFlag',
    'formData_generalInfo_successor_predecessorNameAddressFlag': 'predecessorNameAddressFlag',
    'formData_generalInfo_successor_successionDateFlag': 'successionDateFlag',
    'formData_generalInfo_successor_successionFlag': 'successionFlag',
    'formData_generalInfo_successor_successorConfFlag': 'successorConfFlag',
    'formData_principalInfo_amendedItemsList': 'amendedItemsList',
    'formData_principalInfo_applicantName': 'principalInfoApplicantName',
    'formData_principalInfo_city': 'principalInfoCity',
    'formData_principalInfo_prncpalConfFlag': 'principalConfFlag',
    'formData_principalInfo_stateOrCountry': 'principalInfoStateOrCountry',
    'formData_principalInfo_street1': 'principalInfoStreet1',
    'formData_principalInfo_zipCode': 'principalInfoZipCode',
    'formData_signatureInfo_signature': 'signature',
    'formData_signatureInfo_signatureApplicantName': 'signatureApplicantName',
    'formData_signatureInfo_signatureConfflag': 'signatureConfFlag',
    'formData_signatureInfo_signatureDate': 'signatureInfoDate',
    'formData_signatureInfo_signatureTitle': 'signatureInfoTitle',
    'headerData_filerInfo_contact_contactEmailAddress': 'contactEmailAddress',
    'headerData_filerInfo_contact_contactName': 'contactName',
    'headerData_filerInfo_contact_contactPhoneNumber': 'contactPhoneNumber',
    'headerData_filerInfo_filer_filerCredentials_ccc': 'headerFilerCredentialsCcc',
    'headerData_filerInfo_filer_filerCredentials_cik': 'headerFilerCredentialsCik',
    'headerData_filerInfo_flags_confirmingCopyFlag': 'headerConfirmingCopyFlag',
    'headerData_filerInfo_flags_overrideInternetFlag': 'headerOverrideInternetFlag',
    'headerData_filerInfo_flags_returnCopyFlag': 'headerReturnCopyFlag',
    'headerData_filerInfo_liveTestFlag': 'headerLiveTestFlag',
    'headerData_submissionType': 'headerSubmissionType'
}

config_sdr: Dict[str, Dict[str, Any]] = {
    'sdr': {
        'path': 'edgarSubmission',
        'mapping': sdr_dict
    }
}