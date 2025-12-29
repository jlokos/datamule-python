"""Download and package SEC filings from the DataMule SGML bucket."""

from __future__ import annotations

import asyncio
import io
import json
import logging
import os
import shutil
import ssl
import tarfile
import time
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from os import cpu_count
from queue import Queue
from threading import Lock, Thread
from typing import Any, Iterable, List, Optional, Sequence

import aiohttp
import zstandard as zstd
from secsgml import parse_sgml_content_into_memory
from secsgml.utils import bytes_to_str
from tqdm import tqdm

from ..providers.providers import SEC_FILINGS_SGML_BUCKET_ENDPOINT
from ..utils.format_accession import format_accession
from .datamule_lookup import datamule_lookup

# TODO could be cleaned up

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=logging.getLogger().handlers,
)
logger = logging.getLogger(__name__)


class Downloader:
    """Download submissions and store them in batch tar archives."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize a downloader with an optional API key."""
        self.BASE_URL = SEC_FILINGS_SGML_BUCKET_ENDPOINT
        self.CHUNK_SIZE = 2 * 1024 * 1024
        self.MAX_CONCURRENT_DOWNLOADS = 10
        self.MAX_DECOMPRESSION_WORKERS = cpu_count()
        self.MAX_TAR_WORKERS = cpu_count()
        if api_key is not None:
            self._api_key = api_key
        self.loop = asyncio.new_event_loop()
        self.loop_thread = Thread(target=self._run_event_loop, daemon=True)
        self.loop_thread.start()
        self.async_queue = Queue()
        
    def _run_event_loop(self) -> None:
        """Run the internal event loop on a background thread."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    
    def _run_coroutine(self, coro: Any) -> Any:
        """Run a coroutine on the internal event loop and return its result."""
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result()

    @property
    def api_key(self) -> Optional[str]:
        """Return the API key from memory or environment."""
        return getattr(self, '_api_key', None) or os.getenv('DATAMULE_API_KEY')

    @api_key.setter
    def api_key(self, value: str) -> None:
        """Set the API key for authenticated downloads."""
        if not value:
            raise ValueError("API key cannot be empty")
        self._api_key = value

    def _log_error(self, output_dir: str, filename: str, error_msg: str) -> None:
        """Append an error entry to output_dir/errors.json."""
        error_file = os.path.join(output_dir, 'errors.json')
        try:
            if os.path.exists(error_file):
                with open(error_file, 'r') as f:
                    errors = json.load(f)
            else:
                errors = {}
            
            errors[filename] = str(error_msg)
            
            with open(error_file, 'w') as f:
                json.dump(errors, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to log error to {error_file}: {str(e)}")

    class TarManager:
        """Manage batch tar output files and their sizes."""

        def __init__(
            self,
            output_dir: str,
            num_tar_files: int,
            max_batch_size: int = 1024 * 1024 * 1024,
        ) -> None:
            """Initialize tar files and locks for concurrent writes."""
            self.output_dir = output_dir
            self.num_tar_files = num_tar_files
            self.max_batch_size = max_batch_size
            self.tar_files = {}
            self.tar_locks = {}
            self.file_counters = {}
            self.tar_sizes = {}
            self.tar_sequences = {}
            
            for i in range(num_tar_files):
                tar_path = os.path.join(output_dir, f'batch_{i:03d}_001.tar')
                self.tar_files[i] = tarfile.open(tar_path, 'a')
                self.tar_locks[i] = Lock()
                self.file_counters[i] = 0
                self.tar_sizes[i] = 0
                self.tar_sequences[i] = 1
        
        def get_tar_index(self, filename: str) -> int:
            """Return the tar shard index for a filename."""
            return hash(filename) % self.num_tar_files
        
        def write_submission(
            self,
            filename: str,
            metadata: Any,
            documents: Sequence[bytes],
            standardize_metadata: bool,
        ) -> bool:
            """Write a submission's metadata and documents into a tar."""
            tar_index = self.get_tar_index(filename)
            accession_num = filename.split('.')[0]
            
            metadata_str = bytes_to_str(metadata, lower=False)
            metadata_json = json.dumps(metadata_str).encode('utf-8')
            submission_size = len(metadata_json) + sum(len(doc) for doc in documents)
            
            with self.tar_locks[tar_index]:
                if self.tar_sizes[tar_index] > 0 and self.tar_sizes[tar_index] + submission_size > self.max_batch_size:
                    tar = self.tar_files[tar_index]
                    tar.close()

                    self.tar_sequences[tar_index] += 1
                    new_tar_path = os.path.join(self.output_dir, f'batch_{tar_index:03d}_{self.tar_sequences[tar_index]:03d}.tar')
                    self.tar_files[tar_index] = tarfile.open(new_tar_path, 'a')
                    self.file_counters[tar_index] = 0
                    self.tar_sizes[tar_index] = 0
                
                tar = self.tar_files[tar_index]
                
                try:
                    tarinfo = tarfile.TarInfo(name=f'{accession_num}/metadata.json')
                    tarinfo.size = len(metadata_json)
                    tar.addfile(tarinfo, io.BytesIO(metadata_json))
                    
                    for file_num, content in enumerate(documents):
                        doc_name = self._get_document_name(metadata, file_num, standardize_metadata)
                        tarinfo = tarfile.TarInfo(name=f'{accession_num}/{doc_name}')
                        tarinfo.size = len(content)
                        tar.addfile(tarinfo, io.BytesIO(content))
                    
                    self.file_counters[tar_index] += 1
                    self.tar_sizes[tar_index] += submission_size
                    return True
                    
                except Exception as e:
                    logger.error(f"Error writing {filename} to tar {tar_index}: {str(e)}")
                    return False
        
        def _get_document_name(
            self,
            metadata: Any,
            file_num: int,
            standardize_metadata: bool,
        ) -> str:
            """Resolve a document filename from metadata."""
            if standardize_metadata:
                documents_key = b'documents'
                filename_key = b'filename'
                sequence_key = b'sequence'
            else:
                documents_key = b'DOCUMENTS'
                filename_key = b'FILENAME'
                sequence_key = b'SEQUENCE'
            
            doc_metadata = metadata[documents_key][file_num]
            filename = doc_metadata.get(filename_key)
            if filename:
                return filename.decode('utf-8')
            else:
                sequence = doc_metadata.get(sequence_key, b'document')
                return sequence.decode('utf-8') + '.txt'
        
        def close_all(self) -> None:
            """Close all tar file handles."""
            for i, tar in self.tar_files.items():
                try:
                    tar.close()
                except Exception as e:
                    logger.error(f"Error closing tar {i}: {str(e)}")

    def decompress_and_parse_and_write(
        self,
        compressed_chunks: Sequence[bytes],
        filename: str,
        keep_document_types: Sequence[str],
        keep_filtered_metadata: bool,
        standardize_metadata: bool,
        tar_manager: "Downloader.TarManager",
        output_dir: str,
    ) -> bool:
        """Decompress zstd content, parse SGML, and write to tar."""
        dctx = zstd.ZstdDecompressor()
        try:
            input_buffer = io.BytesIO(b''.join(compressed_chunks))
            decompressed_content = io.BytesIO()
            
            with dctx.stream_reader(input_buffer) as reader:
                shutil.copyfileobj(reader, decompressed_content)
                
            content = decompressed_content.getvalue()
            
            metadata, documents = parse_sgml_content_into_memory(
                bytes_content=content,
                filter_document_types=keep_document_types,
                keep_filtered_metadata=keep_filtered_metadata,
                standardize_metadata=standardize_metadata
            )
            
            success = tar_manager.write_submission(filename, metadata, documents, standardize_metadata)
            return success
                
        except Exception as e:
            self._log_error(output_dir, filename, f"Decompression/parsing error: {str(e)}")
            return False
        finally:
            try:
                input_buffer.close()
                decompressed_content.close()
            except:
                pass

    def parse_and_write_regular_file(
        self,
        chunks: Sequence[bytes],
        filename: str,
        keep_document_types: Sequence[str],
        keep_filtered_metadata: bool,
        standardize_metadata: bool,
        tar_manager: "Downloader.TarManager",
        output_dir: str,
    ) -> bool:
        """Parse raw SGML content and write to tar."""
        try:
            content = b''.join(chunks)
            
            metadata, documents = parse_sgml_content_into_memory(
                bytes_content=content,
                filter_document_types=keep_document_types,
                keep_filtered_metadata=keep_filtered_metadata,
                standardize_metadata=standardize_metadata
            )
            
            success = tar_manager.write_submission(filename, metadata, documents, standardize_metadata)
            return success
                
        except Exception as e:
            self._log_error(output_dir, filename, f"Parsing error: {str(e)}")
            return False

    async def download_and_process(
        self,
        session: aiohttp.ClientSession,
        url: str,
        semaphore: asyncio.Semaphore,
        decompression_pool: ThreadPoolExecutor,
        keep_document_types: Sequence[str],
        keep_filtered_metadata: bool,
        standardize_metadata: bool,
        tar_manager: "Downloader.TarManager",
        output_dir: str,
        pbar: tqdm,
    ) -> None:
        """Download a single submission and write it to batch tar."""
        async with semaphore:
            chunks = []
            filename = url.split('/')[-1]

            api_key = self.api_key
            if not api_key:
                raise ValueError("No API key found. Please set DATAMULE_API_KEY environment variable or provide api_key in constructor")

            try:
                headers = {
                    'Connection': 'keep-alive',
                    'Accept-Encoding': 'gzip, deflate, br',
                    #'Authorization': f'Bearer {api_key}'
                }
                
                async with session.get(url, headers=headers) as response:
                    content_type = response.headers.get('Content-Type', '')
                    
                    if response.status == 200:
                        async for chunk in response.content.iter_chunked(self.CHUNK_SIZE):
                            chunks.append(chunk)

                        loop = asyncio.get_running_loop()
                        if content_type == 'application/zstd':
                            logger.debug(f"Processing {filename} as compressed (zstd)")
                            success = await loop.run_in_executor(
                                decompression_pool,
                                partial(self.decompress_and_parse_and_write, chunks, filename, keep_document_types, keep_filtered_metadata, standardize_metadata, tar_manager, output_dir)
                            )
                        else:
                            logger.debug(f"Processing {filename} as uncompressed")
                            success = await loop.run_in_executor(
                                decompression_pool,
                                partial(self.parse_and_write_regular_file, chunks, filename, keep_document_types, keep_filtered_metadata, standardize_metadata, tar_manager, output_dir)
                            )

                        if not success:
                            self._log_error(output_dir, filename, "Failed to process file")
                            
                    elif response.status == 401:
                        self._log_error(output_dir, filename, "Authentication failed: Invalid API key")
                        raise ValueError("Invalid API key")
                    else:
                        self._log_error(output_dir, filename, f"Download failed: Status {response.status}")
                        
                    pbar.update(1)
                        
            except Exception as e:
                self._log_error(output_dir, filename, str(e))
                pbar.update(1)

    async def process_batch(
        self,
        urls: Sequence[str],
        output_dir: str,
        keep_document_types: Sequence[str] = (),
        keep_filtered_metadata: bool = False,
        standardize_metadata: bool = True,
        max_batch_size: int = 1024 * 1024 * 1024,
    ) -> None:
        """Download and process a batch of submission URLs."""
        os.makedirs(output_dir, exist_ok=True)
        
        num_tar_files = min(self.MAX_TAR_WORKERS, len(urls))
        
        tar_manager = self.TarManager(output_dir, num_tar_files, max_batch_size)
        
        try:
            with tqdm(total=len(urls), desc="Downloading files") as pbar:
                semaphore = asyncio.Semaphore(self.MAX_CONCURRENT_DOWNLOADS)
                decompression_pool = ThreadPoolExecutor(max_workers=self.MAX_DECOMPRESSION_WORKERS)

                connector = aiohttp.TCPConnector(
                    limit=self.MAX_CONCURRENT_DOWNLOADS,
                    force_close=False,
                    ssl=ssl.create_default_context(),
                    ttl_dns_cache=300,
                    keepalive_timeout=60
                )

                async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=600)) as session:
                    tasks = [
                        self.download_and_process(
                            session, url, semaphore, decompression_pool, 
                            keep_document_types, keep_filtered_metadata, standardize_metadata, 
                            tar_manager, output_dir, pbar
                        ) 
                        for url in urls
                    ]
                    await asyncio.gather(*tasks, return_exceptions=True)

                decompression_pool.shutdown()
                
        finally:
            tar_manager.close_all()

    def download(
        self,
        accession_numbers: Sequence[str],
        output_dir: str = "downloads",
        keep_document_types: Sequence[str] = (),
        keep_filtered_metadata: bool = False,
        standardize_metadata: bool = True,
        max_batch_size: int = 1024 * 1024 * 1024,
    ) -> None:
        """
        Download SEC filings for the given accession numbers.
        
        Args:
            accession_numbers: List of accession numbers to download
            output_dir: Directory to save downloaded files
            keep_document_types: List of document types to keep (empty = keep all)
            keep_filtered_metadata: Whether to keep metadata for filtered documents
            standardize_metadata: Whether to standardize metadata keys to lowercase
            max_batch_size: Maximum size of each batch tar file in bytes
        """
        if self.api_key is None:
            raise ValueError("No API key found. Please set DATAMULE_API_KEY environment variable or provide api_key in constructor")

        logger.debug(f"Generating URLs for {len(accession_numbers)} filings...")
        
        urls = []
        for accession in accession_numbers:
            url = f"{self.BASE_URL}{format_accession(accession,'no-dash')}.sgml"
            urls.append(url)
        
        # Deduplicate URLs
        urls = list(set(urls))
        
        if not urls:
            logger.warning("No submissions found matching the criteria")
            return

        start_time = time.time()
        
        asyncio.run(self.process_batch(
            urls, output_dir, 
            keep_document_types=keep_document_types, 
            keep_filtered_metadata=keep_filtered_metadata, 
            standardize_metadata=standardize_metadata, 
            max_batch_size=max_batch_size
        ))
        
        elapsed_time = time.time() - start_time
        logger.debug(f"Processing completed in {elapsed_time:.2f} seconds")
        logger.debug(f"Processing speed: {len(urls)/elapsed_time:.2f} files/second")
    
    def __del__(self):
        if hasattr(self, 'loop') and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)

def download(
    cik: Optional[str] = None,
    ticker: Optional[str] = None,
    submission_type: Optional[str] = None,
    filing_date: Optional[str] = None,
    report_date: Optional[str] = None,
    detected_time: Optional[str] = None,
    contains_xbrl: Optional[bool] = None,
    document_type: Optional[str] = None,
    filename: Optional[str] = None,
    sequence: Optional[str] = None,
    api_key: Optional[str] = None,
    output_dir: str = "downloads",
    filtered_accession_numbers: Optional[Sequence[str]] = None,
    skip_accession_numbers: Optional[Sequence[str]] = None,
    keep_document_types: Sequence[str] = (),
    keep_filtered_metadata: bool = False,
    standardize_metadata: bool = True,
    max_batch_size: int = 1024 * 1024 * 1024,
    accession_numbers: Optional[Sequence[str]] = None,
    quiet: bool = False,
    **kwargs: Any,
) -> None:
    """
    Download SEC filings from DataMule.
    
    If accession_numbers is provided, downloads those directly.
    Otherwise, queries datamule_lookup with the provided filters to get accession numbers.
    """
    
    downloader = Downloader(api_key=api_key)

    # Get accession numbers if not provided
    if accession_numbers is None:
        accession_numbers = datamule_lookup(
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
            filtered_accession_numbers=filtered_accession_numbers,
            skip_accession_numbers=skip_accession_numbers,
            quiet=quiet, 
            api_key=api_key,
            provider='datamule-sgml',
            **kwargs
        )

        
        if not accession_numbers:
            logger.warning("No submissions found matching the criteria")
            return
    
    # Download the filings
    downloader.download(
        accession_numbers=accession_numbers,
        output_dir=output_dir,
        keep_document_types=keep_document_types,
        keep_filtered_metadata=keep_filtered_metadata,
        standardize_metadata=standardize_metadata,
        max_batch_size=max_batch_size
    )
