"""
SEC EDGAR Submissions Streamer Module.

This module provides functionality for streaming SEC EDGAR filings
by querying the EFTS (EDGAR Full-Text Search) API and downloading
the actual submission documents. It extends the EFTSQuery class
to add document streaming capabilities with rate limiting and
progress tracking.

Classes:
    Streamer: Async streamer that queries EFTS and downloads submissions.

Functions:
    fix_filing_url: Corrects malformed SEC filing URLs.
    stream: Convenience function to stream SEC filings synchronously.
"""

import asyncio
from urllib.parse import urlencode
from typing import Optional, List, Callable, Any, Tuple, Union
from tqdm import tqdm
import re

from .eftsquery import EFTSQuery


def fix_filing_url(url: str) -> str:
    """
    Fix malformed SEC filing URLs by reformatting the accession number.

    Some SEC URLs have incorrectly formatted accession numbers in the
    filename portion. This function detects and corrects these URLs
    by inserting dashes in the proper positions.

    Args:
        url: The SEC filing URL to check and potentially fix.

    Returns:
        The corrected URL if a fix was needed, otherwise the original URL.

    Example:
        >>> fix_filing_url("https://www.sec.gov/.../0001234567890123456789/1234.txt")
        "https://www.sec.gov/.../0001234567890123456789/0001234567-89-012345-1234.txt"
    """
    match_suffix = re.search(r'/(\d{4})\.(.+?)$', url)
    if match_suffix:
        suffix_number = match_suffix.group(1)
        file_ext = match_suffix.group(2)
        match_accession = re.search(r'/(\d{18})/', url)
        if match_accession:
            accession_number = match_accession.group(1)
            formatted_accession_number = f"{accession_number[:10]}-{accession_number[10:12]}-{accession_number[12:]}"
            new_url = url.rsplit('/', 1)[0] + f'/{formatted_accession_number}-{suffix_number}.{file_ext}'
            return new_url
    return url

class Streamer(EFTSQuery):
    """
    Async streamer for SEC EDGAR filings via EFTS API.

    This class extends EFTSQuery to add document streaming capabilities.
    It queries the EFTS (EDGAR Full-Text Search) API and downloads the
    actual submission documents, processing them with a user-provided
    callback function.

    The streamer manages concurrent downloads with rate limiting and
    provides progress tracking via tqdm progress bars.

    Attributes:
        document_callback: Async callback function invoked for each downloaded document.
        document_queue: Queue holding documents pending download.
        download_in_progress: Event indicating active document downloads.
        query_paused: Event used to pause EFTS queries during downloads.
        document_pbar: Progress bar for document downloads.
        document_workers: List of async worker tasks for downloads.
        documents_processed: Counter of successfully processed documents.
        total_documents: Total number of documents queued for download.
        accession_numbers: Optional set of accession numbers to include.
        skip_accession_numbers: Optional set of accession numbers to skip.
        skipped_documents: Counter of documents skipped by filters.

    Example:
        >>> async def my_callback(hit, content, cik, accno, url):
        ...     print(f"Downloaded {accno}")
        >>> streamer = Streamer(document_callback=my_callback)
        >>> results = await streamer.stream(cik="1318605", submission_type="10-K")
    """

    def __init__(
        self,
        requests_per_second: float = 5.0,
        document_callback: Optional[Callable] = None,
        accession_numbers: Optional[List[str]] = None,
        skip_accession_numbers: Optional[List[str]] = None,
        quiet: bool = False
    ) -> None:
        """
        Initialize the Streamer.

        Args:
            requests_per_second: Rate limit for SEC requests. Defaults to 5.0.
            document_callback: Async callback function that receives
                (hit, content, cik, accno, url) for each downloaded document.
            accession_numbers: Optional list of accession numbers to include.
                If provided, only these accession numbers will be downloaded.
            skip_accession_numbers: Optional list of accession numbers to skip.
            quiet: If True, suppress progress output. Defaults to False.
        """
        super().__init__(requests_per_second=requests_per_second, quiet=quiet)
        self.document_callback = document_callback
        self.document_queue: asyncio.Queue = asyncio.Queue()
        self.download_in_progress: asyncio.Event = asyncio.Event()
        self.query_paused: asyncio.Event = asyncio.Event()
        self.document_pbar: Optional[tqdm] = None
        self.document_workers: List[asyncio.Task] = []
        self.documents_processed: int = 0
        self.total_documents: int = 0
        self.accession_numbers = accession_numbers
        self.skip_accession_numbers = skip_accession_numbers
        self.skipped_documents: int = 0
        
    async def _fetch_worker(self) -> None:
        """
        Override the parent class worker to implement pause/resume functionality.

        This worker processes EFTS query requests from the fetch queue while
        respecting pause signals during document downloads. When query_paused
        is set, the worker waits until downloads complete before continuing.

        The worker runs indefinitely until cancelled, processing URLs from
        the fetch queue and invoking callbacks with the results.

        Raises:
            asyncio.CancelledError: When the worker is cancelled during shutdown.
        """
        while True:
            try:
                # Check if we should pause for document downloads
                if self.query_paused.is_set():
                    # Wait until downloads are done and we're resumed
                    await self.query_paused.wait()
                    
                params, from_val, size_val, callback = await self.fetch_queue.get()
                
                url = f"{self.base_url}?{urlencode(params, doseq=True)}&from={from_val}&size={size_val}"
                
                try:
                    data = await self._fetch_json(url)
                    if 'hits' in data:
                        hits = data['hits']['hits']
                        if self.pbar:
                            self.pbar.update(len(hits))
                        if callback:
                            await callback(hits)
                    self.fetch_queue.task_done()
                except Exception as e:
                    if not self.quiet:
                        print(f"\nError fetching {url}: {str(e)}")
                    self.fetch_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                if not self.quiet:
                    print(f"\nWorker error: {str(e)}")
                self.fetch_queue.task_done()

    def _construct_submission_url(self, hit: dict) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Construct the URL for retrieving the actual submission document.

        Extracts the CIK and accession number from an EFTS hit and constructs
        the full SEC EDGAR URL for the submission file. Also applies any
        configured accession number filters.

        Args:
            hit: An EFTS search hit dictionary containing _id and _source fields.

        Returns:
            A tuple of (url, cik, accession_number) if successful, or
            (None, None, None) if the hit should be skipped or an error occurs.
        """
        try:
            # Extract CIK from the hit
            cik = hit['_source']['ciks'][0]
            
            # Extract accession number from _id (format: accno:file.txt)
            accno_w_dash = hit['_id'].split(':')[0]
            accno_no_dash = accno_w_dash.replace('-', '')
            
            # Check if we should filter by accession numbers
            if self.accession_numbers is not None and accno_w_dash not in self.accession_numbers:
                return None, None, None
            
            if self.skip_accession_numbers is not None and accno_no_dash in self.skip_accession_numbers:
                return None, None, None
            
            # Construct the URL
            url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accno_no_dash}/{accno_w_dash}.txt"
            url = fix_filing_url(url)
            
            return url, cik, accno_w_dash
        except (KeyError, IndexError) as e:
            if not self.quiet:
                print(f"Error constructing URL for hit: {hit}. Error: {str(e)}")
            return None, None, None

    async def _document_download_worker(self) -> None:
        """
        Async worker to download actual SEC filing documents.

        This worker processes items from the document_queue, downloading
        each filing and passing it to the document_callback. It respects
        the configured rate limiter and updates progress tracking.

        The worker runs indefinitely until cancelled, processing download
        requests from the queue.

        Raises:
            asyncio.CancelledError: When the worker is cancelled during shutdown.
        """
        while True:
            try:
                hit, doc_url, cik, accno = await self.document_queue.get()
                
                try:
                    # Use the same rate limiter as the EFTS queries
                    async with self.limiter:
                        async with self.session.get(doc_url) as response:
                            response.raise_for_status()
                            content = await response.read()
                            
                            # Update rate monitor
                            await self.rate_monitor.add_request(len(content))
                            
                            # Call document callback with content in memory
                            if self.document_callback:
                                await self.document_callback(hit, content, cik, accno, doc_url)
                            
                            # Update progress bar
                            if self.document_pbar:
                                self.document_pbar.update(1)
                                self.documents_processed += 1
                            
                    self.document_queue.task_done()
                except Exception as e:
                    if not self.quiet:
                        print(f"\nError streaming document {doc_url}: {str(e)}")
                    self.document_queue.task_done()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                if not self.quiet:
                    print(f"\nDocument worker error: {str(e)}")
                self.document_queue.task_done()

    async def document_download_callback(self, hits: List[dict]) -> None:
        """
        Callback to process EFTS query results and stream submissions.

        This method is invoked by the EFTS query system for each batch of
        search results. It pauses the query processing, queues documents
        for download, waits for all downloads to complete, then resumes
        query processing.

        Args:
            hits: List of EFTS search hit dictionaries to process.
        """
        # Pause the EFTS query processing
        self.query_paused.set()
        
        # Signal that document download is in progress
        self.download_in_progress.set()
        
        # Create progress bar for documents if not exists
        if not self.document_pbar and not self.quiet:
            self.document_pbar = tqdm(total=0, desc="Streaming submissions")
        
        # Queue up the documents for download
        for hit in hits:
            doc_url, cik, accno = self._construct_submission_url(hit)
            if doc_url:
                # Update document progress bar total
                if self.document_pbar:
                    self.document_pbar.total += 1
                self.total_documents += 1
                
                # Add to download queue
                await self.document_queue.put((hit, doc_url, cik, accno))
            elif accno is None and self.accession_numbers is not None:
                # Document was skipped due to accession number filter
                self.skipped_documents += 1
        
        # Wait for all documents to be downloaded
        await self.document_queue.join()
        
        # Resume EFTS query processing
        self.query_paused.clear()
        
        # Signal that document download is complete
        self.download_in_progress.clear()

    async def stream(
        self,
        cik: Optional[Union[str, List[str]]] = None,
        submission_type: Optional[Union[str, List[str]]] = None,
        filing_date: Optional[Union[str, tuple, List]] = None,
        location: Optional[str] = None,
        name: Optional[str] = None
    ) -> List[dict]:
        """
        Stream EFTS results and download documents.

        This is the main entry point for streaming SEC filings. It queries
        the EFTS API with the provided filters, downloads matching submissions,
        and processes them with the configured document_callback.

        Args:
            cik: Central Index Key(s) for the company. Can be a single CIK
                string or a list of CIKs.
            submission_type: Filing form type(s) to filter by (e.g., "10-K",
                "10-Q"). Can be a single type or a list.
            filing_date: Date or date range to filter by. Can be a single
                date string, a tuple of (start, end), or a list of dates.
            location: Location code to filter by (e.g., "CA" for California).
            name: Company name to search for (alternative to providing CIK).

        Returns:
            List of all EFTS hits processed.

        Example:
            >>> streamer = Streamer(document_callback=my_callback)
            >>> results = await streamer.stream(
            ...     cik="1318605",
            ...     submission_type="10-K",
            ...     filing_date=("2020-01-01", "2023-12-31")
            ... )
        """
        # Create document worker tasks
        self.document_workers = [
            asyncio.create_task(self._document_download_worker()) 
            for _ in range(5)  # Same number as query workers
        ]
        
        # Reset counters
        self.documents_processed = 0
        self.total_documents = 0
        self.skipped_documents = 0
        
        # Run the main query with our document download callback
        results = await self.query(cik, submission_type, filing_date, location, self.document_download_callback, name)
        
        # Make sure all document downloads are complete
        if self.download_in_progress.is_set():
            if not self.quiet:
                print("Waiting for remaining document downloads to complete...")
            await self.document_queue.join()
        
        # Clean up document workers
        for worker in self.document_workers:
            worker.cancel()
        
        await asyncio.gather(*self.document_workers, return_exceptions=True)
        
        # Close document progress bar and don't show a new one
        if self.document_pbar:
            self.document_pbar.close()
            self.document_pbar = None  # Set to None to prevent reuse
        
        if not self.quiet:
            print(f"\n--- Streaming complete: {len(results)} EFTS results processed ---")
            if self.accession_numbers is not None:
                print(f"--- {self.documents_processed} documents downloaded, {self.skipped_documents} skipped due to accession number filter ---")
        
        return results

def stream(
    cik: Optional[Union[str, List[str]]] = None,
    submission_type: Optional[Union[str, List[str]]] = None,
    filing_date: Optional[Union[str, tuple, List]] = None,
    location: Optional[str] = None,
    requests_per_second: float = 5.0,
    document_callback: Optional[Callable] = None,
    filtered_accession_numbers: Optional[List[str]] = None,
    skip_accession_numbers: List[str] = [],
    quiet: bool = False,
    name: Optional[str] = None
) -> List[dict]:
    """
    Stream SEC EFTS results and download documents into memory.

    This is a convenience function that wraps the Streamer class for
    synchronous use. It creates an async event loop internally to run
    the streaming operation.

    Args:
        cik: CIK number(s) to query for. Can be a single string or list.
        submission_type: Filing type(s) to query for (e.g., "10-K", "10-Q").
        filing_date: Date or date range to query for. Can be a single date
            string, a tuple of (start, end), or a list of dates.
        location: Location code to filter by (e.g., "CA" for California).
        requests_per_second: Rate limit for SEC requests. Defaults to 5.0.
        document_callback: Async callback function that receives
            (hit, content, cik, accno, url) for each downloaded document.
        filtered_accession_numbers: Optional list of accession numbers to
            include. If provided, only these accession numbers are downloaded.
        skip_accession_numbers: Optional list of accession numbers to skip.
        quiet: If True, suppress progress output. Defaults to False.
        name: Company name to search for (alternative to providing CIK).

    Returns:
        List of all EFTS hits processed.

    Raises:
        ValueError: If filtered_accession_numbers is an empty list.

    Example:
        Search by company name::

            results = stream(name="Tesla", submission_type="10-K")

        Search by CIK::

            results = stream(cik="1318605", submission_type="10-K")

        Search with location filter::

            results = stream(name="Tesla", location="CA", submission_type="10-K")

        With custom callback::

            async def save_filing(hit, content, cik, accno, url):
                with open(f"{accno}.txt", "wb") as f:
                    f.write(content)

            results = stream(
                cik="1318605",
                submission_type="10-K",
                document_callback=save_filing
            )
    """
    
    # Check if acc no is empty list
    if filtered_accession_numbers == []:
        raise ValueError("Applied filter resulted in empty accession numbers list")
    
    async def run_stream():
        """Run the Streamer in an async context and return results."""
        streamer = Streamer(
            requests_per_second=requests_per_second, 
            document_callback=document_callback,
            accession_numbers=filtered_accession_numbers,
            skip_accession_numbers=skip_accession_numbers,
            quiet=quiet
        )
        return await streamer.stream(cik, submission_type, filing_date, location, name)
    
    return asyncio.run(run_stream())
