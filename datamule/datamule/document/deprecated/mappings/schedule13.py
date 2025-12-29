"""
Deprecated field mappings for SEC Schedule 13 filings.

This module contains dictionary mappings that translate raw SEC EDGAR field names
to normalized field names for Schedule 13 (beneficial ownership) filings. These
mappings are used when parsing Schedule 13D and Schedule 13G forms.

.. deprecated::
    This module is deprecated. Use the current mappings module instead.

Dictionaries
------------
metadata_schedule_13_dict : dict[str, str]
    Mappings for filing metadata fields including filer credentials and submission type.

cover_schedule_13_dict : dict[str, str]
    Mappings for cover page fields including issuer information, authorized persons,
    and filing rules designation.

reporting_person_details_schedule_13_dict : dict[str, str]
    Mappings for reporting person details including ownership amounts, voting power,
    and citizenship information.

item_1_schedule_13_dict : dict[str, str]
    Mappings for Item 1 fields (Security and Issuer).

item_2_schedule_13_dict : dict[str, str]
    Mappings for Item 2 fields (Identity and Background).

item_3_schedule_13_dict : dict[str, str]
    Mappings for Item 3 fields (Source and Amount of Funds).

item_4_schedule_13_dict : dict[str, str]
    Mappings for Item 4 fields (Purpose of Transaction).

item_5_schedule_13_dict : dict[str, str]
    Mappings for Item 5 fields (Interest in Securities of the Issuer).

item_6_schedule_13_dict : dict[str, str]
    Mappings for Item 6 fields (Contracts, Arrangements, Understandings).

item_7_schedule_13_dict : dict[str, str]
    Mappings for Item 7 fields (Material to be Filed as Exhibits).

item_8_schedule_13_dict : dict[str, str]
    Mappings for Item 8 fields (Identification and Classification of Group Members).

item_9_schedule_13_dict : dict[str, str]
    Mappings for Item 9 fields (Notice of Dissolution of Group).

item_10_schedule_13_dict : dict[str, str]
    Mappings for Item 10 fields (Certifications).

signature_schedule_13_dict : dict[str, str]
    Mappings for signature block fields including name, date, and title.
"""

metadata_schedule_13_dict = {
    'filerInfo_filer_filerCredentials_ccc': 'headerFilerCredentialsCcc',
    'filerInfo_filer_filerCredentials_cik': 'headerFilerCredentialsCik',
    'filerInfo_liveTestFlag': 'headerLiveTestFlag',
    'previousAccessionNumber': 'previousAccessionNumber',
    'submissionType': 'headerSubmissionType'
}

cover_schedule_13_dict = {
    'amendmentNo': 'amendmentNo',
    'authorizedPersons_notificationInfo': 'authorizedPersonsNotificationInfo',
    'authorizedPersons_notificationInfo_personAddress_city': 'authorizedPersonsNotificationInfoPersonAddressCity',
    'authorizedPersons_notificationInfo_personAddress_stateOrCountry': 'authorizedPersonsNotificationInfoPersonAddressStateOrCountry',
    'authorizedPersons_notificationInfo_personAddress_street1': 'authorizedPersonsNotificationInfoPersonAddressStreet1',
    'authorizedPersons_notificationInfo_personAddress_street2': 'authorizedPersonsNotificationInfoPersonAddressStreet2',
    'authorizedPersons_notificationInfo_personAddress_zipCode': 'authorizedPersonsNotificationInfoPersonAddressZipCode',
    'authorizedPersons_notificationInfo_personName': 'authorizedPersonsNotificationInfoPersonName',
    'authorizedPersons_notificationInfo_personPhoneNum': 'authorizedPersonsNotificationInfoPersonPhoneNum',
    'dateOfEvent': 'dateOfEvent',
    'designateRulesPursuantThisScheduleFiled_designateRulePursuantThisScheduleFiled': 'designateRulesPursuantThisScheduleFiledDesignateRulePursuantThisScheduleFiled',
    'eventDateRequiresFilingThisStatement': 'eventDateRequiresFilingThisStatement',
    'issuerInfo_address_city': 'issuerInfoAddressCity',
    'issuerInfo_address_stateOrCountry': 'issuerInfoAddressStateOrCountry',
    'issuerInfo_address_street1': 'issuerInfoAddressStreet1',
    'issuerInfo_address_street2': 'issuerInfoAddressStreet2',
    'issuerInfo_address_zipCode': 'issuerInfoAddressZipCode',
    'issuerInfo_issuerCIK': 'issuerInfoIssuerCik',
    'issuerInfo_issuerCUSIP': 'issuerInfoIssuerCusip',
    'issuerInfo_issuerCik': 'issuerInfoIssuerCik',
    'issuerInfo_issuerCusip': 'issuerInfoIssuerCusip',
    'issuerInfo_issuerName': 'issuerInfoIssuerName',
    'issuerInfo_issuerPrincipalExecutiveOfficeAddress_city': 'issuerInfoIssuerPrincipalExecutiveOfficeAddressCity',
    'issuerInfo_issuerPrincipalExecutiveOfficeAddress_stateOrCountry': 'issuerInfoIssuerPrincipalExecutiveOfficeAddressStateOrCountry',
    'issuerInfo_issuerPrincipalExecutiveOfficeAddress_street1': 'issuerInfoIssuerPrincipalExecutiveOfficeAddressStreet1',
    'issuerInfo_issuerPrincipalExecutiveOfficeAddress_street2': 'issuerInfoIssuerPrincipalExecutiveOfficeAddressStreet2',
    'issuerInfo_issuerPrincipalExecutiveOfficeAddress_zipCode': 'issuerInfoIssuerPrincipalExecutiveOfficeAddressZipCode',
    'previouslyFiledFlag': 'previouslyFiledFlag',
    'securitiesClassTitle': 'securitiesClassTitle'
}

reporting_person_details_schedule_13_dict = {
    'aggregateAmountExcludesCertainSharesFlag': 'aggregateAmountExcludesCertainSharesFlag',
    'citizenshipOrOrganization': 'citizenshipOrOrganization',
    'classPercent': 'classPercent',
    'comments': 'comments',
    'memberGroup': 'memberGroup',
    'reportingPersonBeneficiallyOwnedAggregateNumberOfShares': 'reportingPersonBeneficiallyOwnedAggregateNumberOfShares',
    'reportingPersonBeneficiallyOwnedNumberOfShares_sharedDispositivePower': 'reportingPersonBeneficiallyOwnedNumberOfSharesSharedDispositivePower',
    'reportingPersonBeneficiallyOwnedNumberOfShares_sharedVotingPower': 'reportingPersonBeneficiallyOwnedNumberOfSharesSharedVotingPower',
    'reportingPersonBeneficiallyOwnedNumberOfShares_soleDispositivePower': 'reportingPersonBeneficiallyOwnedNumberOfSharesSoleDispositivePower',
    'reportingPersonBeneficiallyOwnedNumberOfShares_soleVotingPower': 'reportingPersonBeneficiallyOwnedNumberOfSharesSoleVotingPower',
    'reportingPersonName': 'reportingPersonName',
    'typeOfReportingPerson': 'typeOfReportingPerson'
}
item_1_schedule_13_dict = {
    'issuerName': 'issuerName',
    'issuerPrincipalExecutiveOfficeAddress': 'issuerPrincipalExecutiveOfficeAddress'
}

item_2_schedule_13_dict = {
    'citizenship': 'citizenship',
    'filingPersonName': 'filingPersonName',
    'principalBusinessOfficeOrResidenceAddress': 'principalBusinessOfficeOrResidenceAddress'
}

item_3_schedule_13_dict = {
    'notApplicableFlag': 'notApplicableFlag',
    'otherTypeOfPersonFiling': 'otherTypeOfPersonFiling',
    'typeOfPersonFiling': 'typeOfPersonFiling'
}

item_4_schedule_13_dict = {
    'amountBeneficiallyOwned': 'amountBeneficiallyOwned',
    'classPercent': 'classPercent',
    'numberOfSharesPersonHas_sharedPowerOrDirectToDispose': 'numberOfSharesPersonHasSharedPowerOrDirectToDispose',
    'numberOfSharesPersonHas_sharedPowerOrDirectToVote': 'numberOfSharesPersonHasSharedPowerOrDirectToVote',
    'numberOfSharesPersonHas_solePowerOrDirectToDispose': 'numberOfSharesPersonHasSolePowerOrDirectToDispose',
    'numberOfSharesPersonHas_solePowerOrDirectToVote': 'numberOfSharesPersonHasSolePowerOrDirectToVote'
}

item_5_schedule_13_dict = {
    'classOwnership5PercentOrLess': 'classOwnership5PercentOrLess',
    'notApplicableFlag': 'notApplicableFlag'
}

item_6_schedule_13_dict = {
    'notApplicableFlag': 'notApplicableFlag',
    'ownershipMoreThan5PercentOnBehalfOfAnotherPerson': 'ownershipMoreThan5PercentOnBehalfOfAnotherPerson'
}

item_7_schedule_13_dict = {
    'notApplicableFlag': 'notApplicableFlag',
    'subsidiaryIdentificationAndClassification': 'subsidiaryIdentificationAndClassification'
}

item_8_schedule_13_dict = {
    'identificationAndClassificationOfGroupMembers': 'identificationAndClassificationOfGroupMembers',
    'notApplicableFlag': 'notApplicableFlag'
}

item_9_schedule_13_dict = {
    'groupDissolutionNotice': 'groupDissolutionNotice',
    'notApplicableFlag': 'notApplicableFlag'
}

item_10_schedule_13_dict = {
    'certifications': 'certifications',
    'notApplicableFlag': 'notApplicableFlag'
}

signature_schedule_13_dict = {
    'reportingPersonName': 'reportingPersonName',
    'signatureDetails': 'signatureDetails',
    'signatureDetails_date': 'signatureDetailsDate',
    'signatureDetails_signature': 'signatureDetailsSignature',
    'signatureDetails_title': 'signatureDetailsTitle'
}
