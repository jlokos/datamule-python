"""
Mappings for SEC Form 144 (Notice of Proposed Sale of Securities).

This module contains dictionary mappings that define how raw SEC Form 144
field names are transformed into standardized, human-readable field names.
Form 144 is filed by affiliates and other restricted shareholders who intend
to sell securities under Rule 144 of the Securities Act.

Deprecated:
    This module is deprecated. Use the updated mappings in the main
    document module instead.

Attributes:
    securities_sold_in_past_3_months_144_dict (dict[str, str]):
        Mapping for securities sold in the past 3 months section.
    issuer_information_144_dict (dict[str, str]):
        Mapping for issuer information section.
    signatures_144_dict (dict[str, str]):
        Mapping for signature section.
    securities_to_be_sold_144_dict (dict[str, str]):
        Mapping for securities to be sold section.
    securities_information_144_dict (dict[str, str]):
        Mapping for securities information section.
    metadata_144_dict (dict[str, str]):
        Mapping for form metadata section.
"""

securities_sold_in_past_3_months_144_dict: dict[str, str] = {
    'accession': 'accession',
    'sellerDetails_name': 'sellerName',
    'sellerDetails_address_street1': 'sellerStreet1',
    'sellerDetails_address_street2': 'sellerStreet2',
    'sellerDetails_address_city': 'sellerCity',
    'sellerDetails_address_stateOrCountry': 'sellerState',
    'sellerDetails_address_zipCode': 'sellerZip',
    'securitiesClassTitle': 'securitiesClass',
    'saleDate': 'saleDate',
    'amountOfSecuritiesSold': 'securitiesSold',
    'grossProceeds': 'grossProceeds'
}
issuer_information_144_dict: dict[str, str] = {
    'accession': 'accession',
    'issuerCik': 'issuerCik',
    'issuerName': 'issuerName',
    'secFileNumber': 'fileNumber',
    'issuerAddress_street1': 'issuerStreet1',
    'issuerAddress_street2': 'issuerStreet2',
    'issuerAddress_city': 'issuerCity',
    'issuerAddress_stateOrCountry': 'issuerState',
    'issuerAddress_zipCode': 'issuerZip',
    'issuerContactPhone': 'issuerPhone',
    'nameOfPersonForWhoseAccountTheSecuritiesAreToBeSold': 'sellerName',
    'relationshipsToIssuer_relationshipToIssuer': 'sellerRelationship'
}
signatures_144_dict: dict[str, str] = {
    'noticeDate': 'noticeDate',
    'planAdoptionDates_planAdoptionDate': 'planAdoptionDate',
    'signature': 'signature'
}

securities_to_be_sold_144_dict: dict[str, str] = {
    'securitiesClassTitle': 'securitiesClass',
    'acquiredDate': 'acquiredDate',
    'natureOfAcquisitionTransaction': 'acquisitionNature',
    'nameOfPersonfromWhomAcquired': 'acquiredFrom',
    'isGiftTransaction': 'isGift',
    'amountOfSecuritiesAcquired': 'securitiesAmount',
    'paymentDate': 'paymentDate',
    'natureOfPayment': 'paymentNature'
}

securities_information_144_dict: dict[str, str] = {
    'securitiesClassTitle': 'securitiesClass',
    'brokerOrMarketmakerDetails_name': 'brokerName',
    'brokerOrMarketmakerDetails_address_street1': 'brokerStreet',
    'brokerOrMarketmakerDetails_address_city': 'brokerCity',
    'brokerOrMarketmakerDetails_address_stateOrCountry': 'brokerState',
    'brokerOrMarketmakerDetails_address_zipCode': 'brokerZip',
    'noOfUnitsSold': 'unitsSold',
    'aggregateMarketValue': 'marketValue',
    'noOfUnitsOutstanding': 'unitsOutstanding',
    'approxSaleDate': 'saleDate',
    'securitiesExchangeName': 'exchangeName'
}

metadata_144_dict: dict[str, str] = {
    'submissionType': 'submissionType',
    'filerInfo_filer_filerCredentials_cik': 'filerCik',
    'filerInfo_filer_filerCredentials_ccc': 'filerCcc',
    'filerInfo_liveTestFlag': 'liveTestFlag'
}