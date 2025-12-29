"""
Field mappings for SEC ownership filings (Forms 3, 4, and 5).

This module provides dictionaries that map nested XML field paths from SEC ownership
filings to simplified, flattened field names. These mappings are used to transform
the hierarchical structure of SEC EDGAR ownership documents into a more accessible
flat structure for data processing and analysis.

The module defines mappings for the following ownership filing components:

- **Non-derivative transactions**: Stock purchases, sales, and other non-derivative
  security transactions reported in Table I of Forms 4 and 5.
- **Derivative transactions**: Options, warrants, and other derivative security
  transactions reported in Table II of Forms 4 and 5.
- **Non-derivative holdings**: Current stock holdings reported in Forms 3, 4, and 5.
- **Derivative holdings**: Current derivative security holdings.
- **Reporting owner**: Information about the insider filing the report, including
  their relationship to the issuer (director, officer, 10% owner, etc.).
- **Metadata**: Filing-level information such as period of report, issuer details,
  document type, and remarks.
- **Owner signature**: Signature information for the filing.

Note:
    This module is deprecated. Use the updated mappings in the parent package.

Example:
    The mappings transform nested field paths like::

        'transactionAmounts_transactionShares_value'

    Into simplified names like::

        'transactionShares'

Attributes:
    non_derivative_transaction_ownership_dict (dict[str, str]): Maps nested field
        paths to simplified names for non-derivative transactions.
    derivative_transaction_ownership_dict (dict[str, str]): Maps nested field
        paths to simplified names for derivative transactions.
    non_derivative_holding_ownership_dict (dict[str, str]): Maps nested field
        paths to simplified names for non-derivative holdings.
    derivative_holding_ownership_dict (dict[str, str]): Maps nested field
        paths to simplified names for derivative holdings.
    reporting_owner_ownership_dict (dict[str, str]): Maps nested field
        paths to simplified names for reporting owner information.
    metadata_ownership_dict (dict[str, str]): Maps nested field paths to
        simplified names for filing metadata.
    owner_signature_ownership_dict (dict[str, str]): Maps nested field paths
        to simplified names for owner signature information.
"""

# Non-derivative transaction ownership mapping
non_derivative_transaction_ownership_dict: dict[str, str] = {
    'securityTitle_value': 'securityTitle',
    'securityTitle_footnote': 'securityTitleFootnote',
    'transactionDate_value': 'transactionDate',
    'transactionDate_footnote': 'transactionDateFootnote',
    'deemedExecutionDate_value': 'deemedExecutionDate',
    'deemedExecutionDate_footnote': 'deemedExecutionDateFootnote',
    'transactionCoding_transactionFormType': 'transactionFormType',
    'transactionCoding_transactionCode': 'transactionCode',
    'transactionCoding_equitySwapInvolved': 'equitySwapInvolved',
    'transactionCoding_footnote': 'transactionCodingFootnote',
    'transactionAmounts_transactionShares_value': 'transactionShares',
    'transactionAmounts_transactionShares_footnote': 'transactionSharesFootnote',
    'transactionAmounts_transactionPricePerShare_value': 'transactionPricePerShare',
    'transactionAmounts_transactionPricePerShare_footnote': 'transactionPricePerShareFootnote',
    'transactionAmounts_transactionAcquiredDisposedCode_value': 'transactionAcquiredDisposedCode',
    'transactionAmounts_transactionAcquiredDisposedCode_footnote': 'transactionAcquiredDisposedCodeFootnote',
    'postTransactionAmounts_sharesOwnedFollowingTransaction_value': 'sharesOwnedFollowingTransaction',
    'postTransactionAmounts_sharesOwnedFollowingTransaction_footnote': 'sharesOwnedFollowingTransactionFootnote',
    'ownershipNature_directOrIndirectOwnership_value': 'directOrIndirectOwnership',
    'ownershipNature_directOrIndirectOwnership_footnote': 'directOrIndirectOwnershipFootnote',
    'ownershipNature_natureOfOwnership_value': 'natureOfOwnership',
    'ownershipNature_natureOfOwnership_footnote': 'natureOfOwnershipFootnote',
    'transactionTimeliness_value': 'transactionTimeliness',
    'transactionTimeliness_footnote': 'transactionTimelinessFootnote',
    'postTransactionAmounts_valueOwnedFollowingTransaction_value': 'valueOwnedFollowingTransaction',
    'postTransactionAmounts_valueOwnedFollowingTransaction_footnote': 'valueOwnedFollowingTransactionFootnote'
}

# Derivative transaction ownership mapping
derivative_transaction_ownership_dict: dict[str, str] = {
    'securityTitle_value': 'securityTitle',
    'securityTitle_footnote': 'securityTitleFootnote',
    'conversionOrExercisePrice_value': 'conversionOrExercisePrice',
    'conversionOrExercisePrice_footnote': 'conversionOrExercisePriceFootnote',
    'transactionDate_value': 'transactionDate',
    'transactionDate_footnote': 'transactionDateFootnote',
    'deemedExecutionDate_value': 'deemedExecutionDate',
    'deemedExecutionDate_footnote': 'deemedExecutionDateFootnote',
    'transactionCoding_transactionFormType': 'transactionFormType',
    'transactionCoding_transactionCode': 'transactionCode',
    'transactionCoding_equitySwapInvolved': 'equitySwapInvolved',
    'transactionCoding_footnote': 'transactionCodingFootnote',
    'transactionAmounts_transactionShares_value': 'transactionShares',
    'transactionAmounts_transactionShares_footnote': 'transactionSharesFootnote',
    'transactionAmounts_transactionPricePerShare_value': 'transactionPricePerShare',
    'transactionAmounts_transactionPricePerShare_footnote': 'transactionPricePerShareFootnote',
    'transactionAmounts_transactionAcquiredDisposedCode_value': 'transactionAcquiredDisposedCode',
    'transactionAmounts_transactionTotalValue_value': 'transactionTotalValue',
    'transactionAmounts_transactionTotalValue_footnote': 'transactionTotalValueFootnote',
    'exerciseDate_value': 'exerciseDate',
    'exerciseDate_footnote': 'exerciseDateFootnote',
    'expirationDate_value': 'expirationDate',
    'expirationDate_footnote': 'expirationDateFootnote',
    'underlyingSecurity_underlyingSecurityTitle_value': 'underlyingSecurityTitle',
    'underlyingSecurity_underlyingSecurityTitle_footnote': 'underlyingSecurityTitleFootnote',
    'underlyingSecurity_underlyingSecurityShares_value': 'underlyingSecurityShares',
    'underlyingSecurity_underlyingSecurityShares_footnote': 'underlyingSecuritySharesFootnote',
    'underlyingSecurity_underlyingSecurityValue_value': 'underlyingSecurityValue',
    'postTransactionAmounts_sharesOwnedFollowingTransaction_value': 'sharesOwnedFollowingTransaction',
    'postTransactionAmounts_sharesOwnedFollowingTransaction_footnote': 'sharesOwnedFollowingTransactionFootnote',
    'ownershipNature_directOrIndirectOwnership_value': 'directOrIndirectOwnership',
    'ownershipNature_directOrIndirectOwnership_footnote': 'directOrIndirectOwnershipFootnote',
    'ownershipNature_natureOfOwnership_value': 'natureOfOwnership',
    'ownershipNature_natureOfOwnership_footnote': 'natureOfOwnershipFootnote',
    'transactionTimeliness_value': 'transactionTimeliness',
    'transactionTimeliness_footnote': 'transactionTimelinessFootnote',
    'postTransactionAmounts_valueOwnedFollowingTransaction_value': 'valueOwnedFollowingTransaction',
    'postTransactionAmounts_valueOwnedFollowingTransaction_footnote': 'valueOwnedFollowingTransactionFootnote',
    'transactionAmounts_transactionAcquiredDisposedCode_footnote': 'transactionAcquiredDisposedCodeFootnote',
    'underlyingSecurity_underlyingSecurityValue_footnote': 'underlyingSecurityValueFootnote'
}

# Non-derivative holding ownership mapping
non_derivative_holding_ownership_dict: dict[str, str] = {
    'securityTitle_value': 'securityTitle',
    'securityTitle_footnote': 'securityTitleFootnote',
    'postTransactionAmounts_sharesOwnedFollowingTransaction_value': 'sharesOwnedFollowingTransaction',
    'postTransactionAmounts_sharesOwnedFollowingTransaction_footnote': 'sharesOwnedFollowingTransactionFootnote',
    'ownershipNature_directOrIndirectOwnership_value': 'directOrIndirectOwnership',
    'ownershipNature_directOrIndirectOwnership_footnote': 'directOrIndirectOwnershipFootnote',
    'ownershipNature_natureOfOwnership_value': 'natureOfOwnership',
    'ownershipNature_natureOfOwnership_footnote': 'natureOfOwnershipFootnote',
    'postTransactionAmounts_valueOwnedFollowingTransaction_value': 'valueOwnedFollowingTransaction',
    'transactionCoding_footnote': 'transactionCodingFootnote',
    'transactionCoding_transactionFormType': 'transactionFormType',
    'postTransactionAmounts_valueOwnedFollowingTransaction_footnote': 'valueOwnedFollowingTransactionFootnote'
}

# Derivative holding ownership mapping
derivative_holding_ownership_dict: dict[str, str] = {
    'securityTitle_value': 'securityTitle',
    'securityTitle_footnote': 'securityTitleFootnote',
    'conversionOrExercisePrice_value': 'conversionOrExercisePrice',
    'conversionOrExercisePrice_footnote': 'conversionOrExercisePriceFootnote',
    'exerciseDate_value': 'exerciseDate',
    'exerciseDate_footnote': 'exerciseDateFootnote',
    'expirationDate_value': 'expirationDate',
    'expirationDate_footnote': 'expirationDateFootnote',
    'underlyingSecurity_underlyingSecurityTitle_value': 'underlyingSecurityTitle',
    'underlyingSecurity_underlyingSecurityTitle_footnote': 'underlyingSecurityTitleFootnote',
    'underlyingSecurity_underlyingSecurityShares_value': 'underlyingSecurityShares',
    'underlyingSecurity_underlyingSecurityShares_footnote': 'underlyingSecuritySharesFootnote',
    'underlyingSecurity_underlyingSecurityValue_value': 'underlyingSecurityValue',
    'underlyingSecurity_underlyingSecurityValue_footnote': 'underlyingSecurityValueFootnote',
    'ownershipNature_directOrIndirectOwnership_value': 'directOrIndirectOwnership',
    'ownershipNature_directOrIndirectOwnership_footnote': 'directOrIndirectOwnershipFootnote',
    'ownershipNature_natureOfOwnership_value': 'natureOfOwnership',
    'ownershipNature_natureOfOwnership_footnote': 'natureOfOwnershipFootnote',
    'postTransactionAmounts_sharesOwnedFollowingTransaction_value': 'sharesOwnedFollowingTransaction',
    'postTransactionAmounts_sharesOwnedFollowingTransaction_footnote': 'sharesOwnedFollowingTransactionFootnote',
    'postTransactionAmounts_valueOwnedFollowingTransaction_value': 'valueOwnedFollowingTransaction',
    'postTransactionAmounts_valueOwnedFollowingTransaction_footnote': 'valueOwnedFollowingTransactionFootnote',
    'transactionCoding_transactionFormType': 'transactionFormType',
    'transactionCoding_footnote': 'transactionCodingFootnote'
}

# Reporting owner ownership mapping
reporting_owner_ownership_dict: dict[str, str] = {
    'reportingOwnerAddress_rptOwnerCity': 'rptOwnerCity',
    'reportingOwnerAddress_rptOwnerState': 'rptOwnerState',
    'reportingOwnerAddress_rptOwnerStateDescription': 'rptOwnerStateDescription',
    'reportingOwnerAddress_rptOwnerStreet1': 'rptOwnerStreet1',
    'reportingOwnerAddress_rptOwnerStreet2': 'rptOwnerStreet2',
    'reportingOwnerAddress_rptOwnerZipCode': 'rptOwnerZipCode',
    'reportingOwnerId_rptOwnerCik': 'rptOwnerCik',
    'reportingOwnerId_rptOwnerName': 'rptOwnerName',
    'reportingOwnerRelationship_isDirector': 'rptOwnerIsDirector',
    'reportingOwnerRelationship_isOfficer': 'rptOwnerIsOfficer',
    'reportingOwnerRelationship_isTenPercentOwner': 'rptOwnerIsTenPercentOwner',
    'reportingOwnerRelationship_isOther': 'rptOwnerIsOther',
    'reportingOwnerRelationship_officerTitle': 'rptOwnerOfficerTitle',
    'reportingOwnerRelationship_otherText': 'rptOwnerOtherText'
}

# Metadata ownership mapping
metadata_ownership_dict: dict[str, str] = {
    'periodOfReport': 'periodOfReport',
    'issuer_issuerCik': 'issuerCik',
    'issuer_issuerName': 'issuerName',
    'issuer_issuerTradingSymbol': 'issuerTradingSymbol',
    'documentType': 'documentType',
    'remarks': 'remarks',
    'documentDescription': 'documentDescription',
    'footnotes': 'footnotes',
    'notSubjectToSection16': 'notSubjectToSection16',
    'form3HoldingsReported': 'form3HoldingsReported',
    'form4TransactionsReported': 'form4TransactionsReported',
    'noSecuritiesOwned': 'noSecuritiesOwned',
    'aff10b5One': 'aff10b5One',
    'dateOfOriginalSubmission': 'dateOfOriginalSubmission',
    'schemaVersion': 'schemaVersion'
}

# Owner signature ownership mapping
owner_signature_ownership_dict: dict[str, str] = {
    'signatureName': 'signatureName',
    'signatureDate': 'signatureDate'
}

