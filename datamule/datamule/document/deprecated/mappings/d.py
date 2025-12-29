"""Field mapping dictionaries for SEC Form D document parsing.

This module contains mapping dictionaries that translate internal field names
from SEC Form D filings to standardized output field names. These mappings
are used during document parsing to normalize field names across different
sections of Form D filings.

Form D is used by companies to file a notice of an exempt offering of securities
with the SEC under Regulation D.

Note:
    This module is deprecated. New code should use updated mapping implementations.

Dictionaries:
    issuer_list_d_dict: Maps issuer information fields from Form D.
    metadata_d_dict: Maps submission metadata fields.
    offering_data_d_dict: Maps offering details and sales compensation fields.
    primary_issuer_d_dict: Maps primary issuer entity information.
    related_persons_d_dict: Maps related person information fields.
"""

from typing import Dict

# Mapping for issuer list fields in Form D filings.
# Maps nested issuer fields (e.g., address, incorporation year) to flat output names.
issuer_list_d_dict: Dict[str, str] = {
    'issuer_issuerAddress_street1': 'issuerStreet1',
    'issuer_cik': 'issuerCik',
    'issuer_issuerAddress_stateOrCountryDescription': 'issuerStateOrCountryDescription',
    'issuer_issuerAddress_zipCode': 'issuerZipCode',
    'issuer_issuerPhoneNumber': 'issuerPhoneNumber',
    'issuer_yearOfInc_value': 'yearOfIncValue',
    'issuer_issuerAddress_stateOrCountry': 'issuerStateOrCountry',
    'issuer_jurisdictionOfInc': 'jurisdictionOfInc',
    'issuer_entityType': 'entityType',
    'issuer_issuerAddress_street2': 'issuerStreet2',
    'issuer_entityName': 'entityName',
    'accession': 'accession',
    'issuer_edgarPreviousNameList_value': 'edgarPreviousNameListValue',
    'issuer_entityTypeOtherDesc': 'entityTypeOtherDesc',
    'issuer_yearOfInc_yetToBeFormed': 'yearOfIncYetToBeFormed',
    'issuer_yearOfInc_withinFiveYears': 'yearOfIncWithinFiveYears',
    'issuer_issuerPreviousNameList_value': 'issuerPreviousNameListValue',
    'issuer_issuerAddress_city': 'issuerCity'
}

# Mapping for submission metadata fields in Form D filings.
# Contains basic filing information like submission type and schema version.
metadata_d_dict: Dict[str, str] = {
    "testOrLive": "testOrLive",
    "schemaVersion": "schemaVersion",
    "accession": "accession",
    "submissionType": "submissionType",
}

# Mapping for offering data fields in Form D filings.
# Contains extensive mappings for sales compensation, offering amounts,
# securities types, investor information, and signature blocks.
offering_data_d_dict: Dict[str, str] = {
    'salesCompensationList_recipient_foreignSolicitation': 'foreignSolicitation',
    'typeOfFiling_dateOfFirstSale_yetToOccur': 'dateOfFirstSaleYetToOccur',
    'industryGroup_investmentFundInfo_is40Act': 'is40Act',
    'salesCommissionsFindersFees_findersFees_dollarAmount': 'findersFeesAmount',
    'offeringSalesAmounts_totalRemaining': 'totalRemaining',
    'issuerSize_aggregateNetAssetValueRange': 'aggregateNetAssetValueRange',
    'typesOfSecuritiesOffered_isSecurityToBeAcquiredType': 'isSecurityToBeAcquiredType',
    'salesCompensationList_recipient_recipientAddress_stateOrCountryDescription': 'recipientStateOrCountryDescription',
    'typesOfSecuritiesOffered_isEquityType': 'isEquityType',
    'investors_totalNumberAlreadyInvested': 'totalNumberAlreadyInvested',
    'minimumInvestmentAccepted': 'minimumInvestmentAccepted',
    'salesCompensationList_recipient_associatedBDName': 'associatedBDName',
    'salesCompensationList_recipient_statesOfSolicitationList_state': 'statesOfSolicitationState',
    'businessCombinationTransaction_isBusinessCombinationTransaction': 'isBusinessCombinationTransaction',
    'useOfProceeds_grossProceedsUsed_isEstimate': 'grossProceedsUsedIsEstimate',
    'federalExemptionsExclusions_item': 'federalExemptionsExclusionsItem',
    'useOfProceeds_grossProceedsUsed_dollarAmount': 'grossProceedsUsedAmount',
    'industryGroup_industryGroupType': 'industryGroupType',
    'signatureBlock_signature_nameOfSigner': 'nameOfSigner',
    'signatureBlock_signature_signatureDate': 'signatureDate',
    'salesCommissionsFindersFees_salesCommissions_isEstimate': 'salesCommissionsIsEstimate',
    'typesOfSecuritiesOffered_isOtherType': 'isOtherType',
    'salesCompensationList_recipient_associatedBDCRDNumber': 'associatedBDCRDNumber',
    'salesCompensationList_recipient_recipientAddress_stateOrCountry': 'recipientStateOrCountry',
    'typesOfSecuritiesOffered_descriptionOfOtherType': 'descriptionOfOtherType',
    'salesCommissionsFindersFees_salesCommissions_dollarAmount': 'salesCommissionsAmount',
    'useOfProceeds_clarificationOfResponse': 'useOfProceedsClarification',
    'accession': 'accession',
    'typesOfSecuritiesOffered_isPooledInvestmentFundType': 'isPooledInvestmentFundType',
    'salesCompensationList_recipient_statesOfSolicitationList_value': 'statesOfSolicitationValue',
    'signatureBlock_signature_signatureName': 'signatureName',
    'typeOfFiling_newOrAmendment_isAmendment': 'isAmendment',
    'issuerSize_revenueRange': 'revenueRange',
    'salesCommissionsFindersFees_clarificationOfResponse': 'salesCommissionsFindersFeesClarification',
    'salesCompensationList_recipient_recipientAddress_zipCode': 'recipientZipCode',
    'salesCompensationList_recipient_recipientAddress_city': 'recipientCity',
    'typesOfSecuritiesOffered_isOptionToAcquireType': 'isOptionToAcquireType',
    'businessCombinationTransaction_clarificationOfResponse': 'businessCombinationClarification',
    'typesOfSecuritiesOffered_isTenantInCommonType': 'isTenantInCommonType',
    'salesCompensationList_recipient_statesOfSolicitationList_description': 'statesOfSolicitationDescription',
    'offeringSalesAmounts_totalOfferingAmount': 'totalOfferingAmount',
    'investors_numberNonAccreditedInvestors': 'numberNonAccreditedInvestors',
    'signatureBlock_authorizedRepresentative': 'authorizedRepresentative',
    'signatureBlock_signature_issuerName': 'issuerName',
    'salesCompensationList_recipient_recipientAddress_street2': 'recipientStreet2',
    'typesOfSecuritiesOffered_isDebtType': 'isDebtType',
    'salesCompensationList_recipient_recipientAddress_street1': 'recipientStreet1',
    'signatureBlock_signature_signatureTitle': 'signatureTitle',
    'industryGroup_investmentFundInfo_investmentFundType': 'investmentFundType',
    'salesCommissionsFindersFees_findersFees_isEstimate': 'findersFeesIsEstimate',
    'typeOfFiling_dateOfFirstSale_value': 'dateOfFirstSaleValue',
    'offeringSalesAmounts_totalAmountSold': 'totalAmountSold',
    'offeringSalesAmounts_clarificationOfResponse': 'offeringSalesAmountsClarification',
    'investors_hasNonAccreditedInvestors': 'hasNonAccreditedInvestors',
    'salesCompensationList_recipient_recipientCRDNumber': 'recipientCRDNumber',
    'typesOfSecuritiesOffered_isMineralPropertyType': 'isMineralPropertyType',
    'salesCompensationList_recipient_recipientName': 'recipientName',
    'durationOfOffering_moreThanOneYear': 'moreThanOneYear'
}

# Mapping for primary issuer fields in Form D filings.
# Maps entity details including name, address, incorporation, and previous names.
primary_issuer_d_dict: Dict[str, str] = {
    'yearOfInc_withinFiveYears': 'yearOfIncWithinFiveYears',
    'entityTypeOtherDesc': 'entityTypeOtherDesc',
    'jurisdictionOfInc': 'jurisdictionOfInc',
    'issuerAddress_street1': 'issuerStreet1',
    'issuerAddress_zipCode': 'issuerZipCode',
    'issuerPreviousNameList_previousName': 'issuerPreviousName',
    'entityType': 'entityType',
    'issuerPreviousNameList_value': 'issuerPreviousNameListValue',
    'issuerPhoneNumber': 'issuerPhoneNumber',
    'yearOfInc_value': 'yearOfIncValue',
    'yearOfInc_yetToBeFormed': 'yearOfIncYetToBeFormed',
    'edgarPreviousNameList_previousName': 'edgarPreviousName',
    'edgarPreviousNameList_value': 'edgarPreviousNameListValue',
    'issuerAddress_stateOrCountry': 'issuerStateOrCountry',
    'entityName': 'entityName',
    'accession': 'accession',
    'issuerAddress_street2': 'issuerStreet2',
    'issuerAddress_city': 'issuerCity',
    'issuerAddress_stateOrCountryDescription': 'issuerStateOrCountryDescription',
    'cik': 'cik',
    'yearOfInc_overFiveYears': 'yearOfIncOverFiveYears'
}

# Mapping for related persons fields in Form D filings.
# Maps person name, address, and relationship information for related parties.
related_persons_d_dict: Dict[str, str] = {
    'relatedPersonInfo_relatedPersonAddress_stateOrCountry': 'relatedPersonStateOrCountry',
    'relatedPersonInfo_relatedPersonRelationshipList_relationship': 'relatedPersonRelationship',
    'relatedPersonInfo_relationshipClarification': 'relationshipClarification',
    'relatedPersonInfo_relatedPersonName_lastName': 'relatedPersonLastName',
    'accession': 'accession',
    'relatedPersonInfo_relatedPersonName_middleName': 'relatedPersonMiddleName',
    'relatedPersonInfo_relatedPersonAddress_zipCode': 'relatedPersonZipCode',
    'relatedPersonInfo_relatedPersonAddress_city': 'relatedPersonCity',
    'relatedPersonInfo_relatedPersonAddress_street1': 'relatedPersonStreet1',
    'relatedPersonInfo_relatedPersonAddress_stateOrCountryDescription': 'relatedPersonStateOrCountryDescription',
    'relatedPersonInfo_relatedPersonName_firstName': 'relatedPersonFirstName',
    'relatedPersonInfo_relatedPersonAddress_street2': 'relatedPersonStreet2'
}
