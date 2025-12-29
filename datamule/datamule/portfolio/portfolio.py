"""Portfolio manager for loading, filtering, and downloading submissions."""

from __future__ import annotations

import os
import shutil
import tarfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock
from typing import Any, Callable, Iterable, Iterator, List, Optional, Sequence, Union

from tqdm import tqdm

from ..config import Config
from ..datamule.downloader import download as seclibrary_download
from ..datamule.sec_connector import SecConnector
from ..datamule.tar_downloader import download_tar
from ..helper import _process_cik_and_metadata_filters
from ..sec.submissions.downloader import download as sec_download
from ..sec.submissions.monitor import Monitor
from ..sec.submissions.textsearch import filter_text
from ..sec.xbrl.filter_xbrl import filter_xbrl
from ..submission.submission import Submission
from .portfolio_compression_utils_legacy import CompressionManager



class Portfolio:
    """Manage a local submission portfolio with filtering and downloads."""

    def __init__(self, path: str) -> None:
        """Initialize the portfolio at a filesystem path."""
        self.path = Path(path)
        self.api_key = None
        self.submissions = []
        self.submissions_loaded = False
        self.MAX_WORKERS = os.cpu_count() - 1 
        
        # Batch tar support
        self.batch_tar_handles = {}  # {batch_tar_path: tarfile_handle}
        self.batch_tar_locks = {}    # {batch_tar_path: threading.Lock}

        self.monitor = Monitor()
        
        
        if self.path.exists():
            self._load_submissions()
        else:
            self.path.mkdir(parents=True, exist_ok=True)

    def set_api_key(self, api_key: str) -> None:
        """Set the API key used for downloads."""
        self.api_key = api_key
    
    def _load_submissions(self) -> None:
        """Load submissions from disk into memory."""
        print(f"Loading submissions")
        
        # Separate regular and batch items
        regular_items = [f for f in self.path.iterdir() if (f.is_dir() or f.suffix=='.tar') and 'batch' not in f.name]
        batch_tars = [f for f in self.path.iterdir() if f.is_file() and 'batch' in f.name and f.suffix == '.tar']
        
        
        # Load regular submissions (existing logic)
        def load_submission(folder: Path) -> Submission:
            """Load a submission from a directory path."""
            return Submission(folder)
        
        regular_submissions = []
        if regular_items:
            with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
                regular_submissions = list(tqdm(
                    executor.map(load_submission, regular_items),
                    total=len(regular_items),
                    desc="Loading regular submissions"
                ))
        
        # Load batch submissions with parallel processing + progress
        batch_submissions = []
        if batch_tars:
            with tqdm(desc="Loading batch submissions", unit="submissions") as pbar:
                with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
                    # Submit all batch tar jobs
                    futures = [
                        executor.submit(self._load_batch_submissions_worker, batch_tar, pbar) 
                        for batch_tar in batch_tars
                    ]
                    
                    # Collect results as they complete
                    for future in as_completed(futures):
                        batch_submissions.extend(future.result())
        
        # Combine and filter None values  
        self.submissions = [s for s in (regular_submissions + batch_submissions) if s is not None]
        print(f"Successfully loaded {len(self.submissions)} submissions")

        self.submissions_loaded = True

    def _load_batch_submissions_worker(self, batch_tar_path: Path, pbar: tqdm) -> List[Submission]:
        """Worker function to load submissions from one batch tar with progress updates."""
        # Open tar handle and store it
        tar_handle = tarfile.open(batch_tar_path, 'r')
        self.batch_tar_handles[batch_tar_path] = tar_handle
        self.batch_tar_locks[batch_tar_path] = Lock()
        
        # Find all accession directories
        accession_prefixes = set()
        for member in tar_handle.getmembers():
            if '/' in member.name and member.name.endswith('metadata.json'):
                accession_prefix = member.name.split('/')[0]
                accession_prefixes.add(accession_prefix)
        
        # Create submissions for each accession
        submissions = []
        for accession_prefix in accession_prefixes:
            try:
                submission = Submission(
                    batch_tar_path=batch_tar_path,
                    accession=accession_prefix,
                    portfolio_ref=self
                )
                submissions.append(submission)
            except Exception as e:
                print(f"Path: {batch_tar_path}. Exception: {e}")
                pass
                #print(f"Path: {batch_tar_path}. Exception: {e}")
            pbar.update(1)  # Update progress for each successful submission
        
        return submissions
            

    def decompress(self) -> None:
        """Decompress batch tar files into individual submission directories."""
        CompressionManager().decompress_portfolio(self, self.MAX_WORKERS)

    def _close_batch_handles(self) -> None:
        """Close all open batch tar handles to free resources."""
        for handle in self.batch_tar_handles.values():
            handle.close()
        self.batch_tar_handles.clear()
        self.batch_tar_locks.clear()

    def __del__(self):
        """Cleanup batch tar handles on destruction."""
        self._close_batch_handles()

    def process_submissions(self, callback: Callable[[Submission], Any]) -> List[Any]:
        """Process all submissions using a thread pool."""
        if not self.submissions_loaded:
            self._load_submissions()
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            results = list(tqdm(
                executor.map(callback, self.submissions),
                total=len(self.submissions),
                desc="Processing submissions"
            ))
            return results

    def process_documents(self, callback: Callable[[Any], Any]) -> List[Any]:
        """Process all documents using a thread pool."""
        if not self.submissions_loaded:
            self._load_submissions()

        documents = [doc for sub in self.submissions for doc in sub]
        
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            results = list(tqdm(
                executor.map(callback, documents),
                total=len(documents),
                desc="Processing documents"
            ))
            return results
    
    def filter_text(
        self,
        text_query: str,
        cik: Optional[Sequence[str]] = None,
        ticker: Optional[Sequence[str]] = None,
        submission_type: Optional[str] = None,
        filing_date: Optional[Sequence[str]] = None,
        **kwargs: Any,
    ) -> None:
        """Filter submissions by text query and metadata filters."""
        # Process CIK and metadata filters
        cik = _process_cik_and_metadata_filters(cik, ticker, **kwargs)
        
        # Call the filter_text function with processed parameters
        new_accession_numbers = filter_text(
            text_query=text_query,
            cik=cik,
            submission_type=submission_type,
            filing_date=filing_date
        )
        
        # If we already have accession numbers, take the intersection
        if hasattr(self, 'accession_numbers') and self.accession_numbers:
            self.accession_numbers = list(set(self.accession_numbers).intersection(new_accession_numbers))
        else:
            # First query, just set the accession numbers
            self.accession_numbers = new_accession_numbers

    def filter_xbrl(
        self,
        taxonomy: str,
        concept: str,
        unit: str,
        period: str,
        logic: str,
        value: Any,
    ) -> None:
        """Filter submissions by XBRL values."""
        new_accession_numbers = filter_xbrl(
            taxonomy=taxonomy,
            concept=concept,
            unit=unit,
            period=period,
            logic=logic,
            value=value
        )
        
        # If we already have accession numbers, take the intersection
        if hasattr(self, 'accession_numbers') and self.accession_numbers:
            self.accession_numbers = list(set(self.accession_numbers).intersection(new_accession_numbers))
        else:
            # First query, just set the accession numbers
            self.accession_numbers = new_accession_numbers

    def download_submissions(
        self,
        cik: Optional[Sequence[str]] = None,
        ticker: Optional[Sequence[str]] = None,
        submission_type: Optional[str] = None,
        filing_date: Optional[Sequence[str]] = None,
        provider: Optional[str] = None,
        document_type: Sequence[str] = (),
        requests_per_second: int = 5,
        keep_filtered_metadata: bool = False,
        standardize_metadata: bool = True,
        skip_existing: bool = True,
        accession_numbers: Optional[Sequence[str]] = None,
        report_date: Optional[Sequence[str]] = None,
        detected_time: Optional[Sequence[str]] = None,
        contains_xbrl: Optional[bool] = None,
        sequence: Optional[str] = None,
        quiet: bool = False,
        filename: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Download submissions into the portfolio directory."""

        if provider is None:
            config = Config()
            provider = config.get_default_source()

        filtered_accession_numbers = self.accession_numbers if hasattr(self, 'accession_numbers') else None

        skip_accession_numbers = []
        if skip_existing:
            skip_accession_numbers = [sub.accession for sub in self]

        # map legacy provider
        if provider == 'datamule':
            provider = 'datamule-sgml'
            
        if provider == 'datamule-sgml':
            seclibrary_download(
                cik=cik,
                ticker=ticker,
                submission_type=submission_type,
                filing_date=filing_date,
                report_date=report_date,
                detected_time=detected_time,
                contains_xbrl=contains_xbrl,
                document_type=document_type,
                filename=filename,
                sequence=sequence,
                accession_numbers=accession_numbers,
                filtered_accession_numbers=filtered_accession_numbers,
                skip_accession_numbers=skip_accession_numbers,
                output_dir=self.path,
                api_key=self.api_key,
                keep_document_types=document_type,
                keep_filtered_metadata=keep_filtered_metadata,
                standardize_metadata=standardize_metadata,
                quiet=quiet,
                **kwargs
            )
            
        elif provider == 'datamule-tar':
            download_tar(
                cik=cik,
                ticker=ticker,
                submission_type=submission_type,
                filing_date=filing_date,
                report_date=report_date,
                detected_time=detected_time,
                contains_xbrl=contains_xbrl,
                document_type=document_type,
                filename=filename,
                sequence=sequence,
                accession_numbers=accession_numbers,
                filtered_accession_numbers=filtered_accession_numbers,
                skip_accession_numbers=skip_accession_numbers,
                output_dir=self.path,
                api_key=self.api_key,
                keep_document_types=document_type,
                quiet=quiet,
                **kwargs
            )
            
        else:
            # will later add accession_numbers arg in the free update.
            sec_download(
                output_dir=self.path,
                cik=cik,
                submission_type=submission_type,
                filing_date=filing_date,
                requests_per_second=requests_per_second, 
                filtered_accession_numbers=filtered_accession_numbers,
                keep_document_types=document_type,
                keep_filtered_metadata=keep_filtered_metadata,
                standardize_metadata=standardize_metadata,
                skip_accession_numbers=skip_accession_numbers,
                ticker = ticker,
                **kwargs
            )

        self.submissions_loaded = False
        
    def monitor_submissions(
        self,
        data_callback: Optional[Callable[[Any], None]] = None,
        interval_callback: Optional[Callable[[], None]] = None,
        polling_interval: int = 1000,
        quiet: bool = True,
        start_date: Optional[str] = None,
        validation_interval: int = 600000,
    ) -> None:
        """Monitor for new submissions and invoke callbacks."""

        self.monitor.monitor_submissions(
            data_callback=data_callback,
            interval_callback=interval_callback,
            polling_interval=polling_interval,
            quiet=quiet,
            start_date=start_date,
            validation_interval=validation_interval
        )

    def stream_submissions(
        self,
        data_callback: Optional[Callable[[Any], None]] = None,
        quiet: bool = False,
    ) -> None:
        """Stream live submission data via the SEC connector."""

        connector = SecConnector(api_key=self.api_key,quiet=quiet)
        connector.connect(data_callback=data_callback)

        
    def __iter__(self) -> Iterator[Submission]:
        if not self.submissions_loaded:
            self._load_submissions()
        return iter(self.submissions)
    
    def document_type(self, document_types: Union[Sequence[str], str]) -> Iterator[Any]:
        """Yield documents matching the given type(s)."""
        if not self.submissions_loaded:
            self._load_submissions()
        if isinstance(document_types, str):
            document_types = [document_types]
            
        for submission in self.submissions:
            yield from submission.document_type(document_types)

    def delete(self) -> None:
        """Delete the portfolio contents and reset state."""
        self._close_batch_handles()
        shutil.rmtree(self.path)

        # reinit
        self.__dict__.update(Portfolio(self.path).__dict__)
