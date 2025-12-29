"""
SEC submissions downloader module.

This module provides functionality to download SEC EDGAR submissions and save them
as tar archives. It wraps the streaming functionality to provide a simple download
interface that writes submissions directly to disk.
"""

import os
from typing import Any, List, Optional, Union

from .streamer import stream
from secsgml import write_sgml_file_to_tar
from tqdm import tqdm

from ...helper import _process_cik_and_metadata_filters


def download(
    cik: Optional[Union[str, int, List[Union[str, int]]]] = None,
    submission_type: Optional[Union[str, List[str]]] = None,
    filing_date: Optional[Union[str, tuple]] = None,
    location: Optional[str] = None,
    name: Optional[str] = None,
    requests_per_second: int = 5,
    output_dir: str = "filings",
    filtered_accession_numbers: Optional[List[str]] = None,
    quiet: bool = False,
    keep_document_types: Optional[List[str]] = None,
    keep_filtered_metadata: bool = False,
    standardize_metadata: bool = True,
    skip_accession_numbers: Optional[List[str]] = None,
    ticker: Optional[Union[str, List[str]]] = None,
    **kwargs: Any
) -> None:
    """
    Download SEC submissions and save them as tar archives.

    This function streams SEC EDGAR submissions matching the specified criteria
    and writes each submission to a separate tar file in the output directory.
    It uses the streaming API internally but provides a simpler interface for
    bulk downloads.

    Args:
        cik: Central Index Key(s) to filter by. Can be a single CIK or a list.
        submission_type: SEC form type(s) to filter by (e.g., '10-K', '10-Q').
        filing_date: Filing date filter. Can be a single date string or a tuple
            of (start_date, end_date) for a range.
        location: Geographic location filter for filer's state/country.
        name: Company name filter (partial match supported).
        requests_per_second: Rate limit for API requests. Defaults to 5.
        output_dir: Directory path where tar files will be saved. Defaults to "filings".
        filtered_accession_numbers: List of specific accession numbers to download.
        quiet: If True, suppress progress bar output. Defaults to False.
        keep_document_types: List of document types to include in the tar archive.
            If None or empty, all document types are included.
        keep_filtered_metadata: If True, retain metadata for filtered-out documents.
            Defaults to False.
        standardize_metadata: If True, standardize metadata field names to lowercase.
            Defaults to True.
        skip_accession_numbers: List of accession numbers to exclude from download.
        ticker: Stock ticker symbol(s) to filter by. Can be a single ticker or a list.
        **kwargs: Additional keyword arguments passed to the metadata filter processor.

    Returns:
        None. Files are written to the specified output directory.

    Example:
        >>> download(ticker='AAPL', submission_type='10-K', output_dir='apple_filings')
        >>> download(cik='0000320193', filing_date=('2023-01-01', '2023-12-31'))
    """
    if keep_document_types is None:
        keep_document_types = []
    if skip_accession_numbers is None:
        skip_accession_numbers = []

    os.makedirs(output_dir, exist_ok=True)

    pbar = tqdm(desc="Writing", unit=" submissions", disable=quiet, position=2)

    async def callback_wrapper(hit: dict, content: bytes, cik: str, accno: str, url: str) -> None:
        """
        Async callback that writes submission content to a tar archive.

        This callback is invoked for each submission received from the streaming API.
        It writes the SGML content to a tar file named after the accession number.

        Args:
            hit: Metadata dictionary for the submission.
            content: Raw bytes content of the SGML submission file.
            cik: Central Index Key of the filer.
            accno: Accession number of the submission (with dashes).
            url: Source URL of the submission.
        """
        output_path = os.path.join(output_dir, accno.replace('-', '') + '.tar')
        write_sgml_file_to_tar(
            output_path,
            bytes_content=content,
            filter_document_types=keep_document_types,
            keep_filtered_metadata=keep_filtered_metadata,
            standardize_metadata=standardize_metadata
        )
        pbar.update(1)

    cik = _process_cik_and_metadata_filters(cik, ticker, **kwargs)

    return stream(
        cik=cik,
        name=name,
        submission_type=submission_type,
        filing_date=filing_date,
        location=location,
        requests_per_second=requests_per_second,
        document_callback=callback_wrapper,
        filtered_accession_numbers=filtered_accession_numbers,
        skip_accession_numbers=skip_accession_numbers,
        quiet=quiet
    )