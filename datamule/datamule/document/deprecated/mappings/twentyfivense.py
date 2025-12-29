"""
Mapping dictionary for SEC Form 25-NSE (Notification of Suspension of Exchange Listing).

This module provides field name mappings for Form 25-NSE, which is used by national
securities exchanges to notify the SEC of the suspension of trading for a listed
security. The mapping translates internal XML/JSON field names to standardized
output field names.

Deprecated:
    This module is deprecated. Use the current mappings module instead.

Example:
    >>> from datamule.document.deprecated.mappings.twentyfivense import twentyfive_nse_dict
    >>> twentyfive_nse_dict['issuer_entityName']
    'issuerName'
"""

from typing import Dict

#: Mapping dictionary from Form 25-NSE source field names to standardized output names.
#: Keys represent the original field names from SEC XML/JSON data structures,
#: and values represent the normalized output field names.
twentyfive_nse_dict: Dict[str, str] = {
    'descriptionClassSecurity': 'securityDescription',
    'exchange_cik': 'exchangeCik',
    'exchange_entityName': 'exchangeName',
    'issuer_address_city': 'issuerCity',
    'issuer_address_stateOrCountry': 'issuerStateOrCountry',
    'issuer_address_stateOrCountryCode': 'issuerStateOrCountryCode',
    'issuer_address_street1': 'issuerStreet1',
    'issuer_address_street2': 'issuerStreet2',
    'issuer_address_zipCode': 'issuerZipCode',
    'issuer_cik': 'issuerCik',
    'issuer_entityName': 'issuerName',
    'issuer_fileNumber': 'issuerFileNumber',
    'issuer_telephoneNumber': 'issuerPhone',
    'ruleProvision': 'ruleProvision',
    'schemaVersion': 'schemaVersion',
    'signatureData_signatureDate': 'signatureDate',
    'signatureData_signatureName': 'signatureName',
    'signatureData_signatureTitle': 'signatureTitle'
}