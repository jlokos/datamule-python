"""Search helpers for SEC submissions."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Union

from .helper import _process_cik_and_metadata_filters
from .sec.submissions.textsearch import query

class Index:
    """Convenience wrapper for text-based submission searches."""

    def __init__(self) -> None:
        """Create an Index instance."""
        pass
        
    def search_submissions(
        self,
        text_query: Optional[str] = None,
        filing_date: Optional[Union[str, Sequence[str]]] = None,
        submission_type: Optional[str] = None,
        cik: Optional[Union[str, int, Sequence[Union[str, int]]]] = None,
        ticker: Optional[Union[str, Sequence[str]]] = None,
        requests_per_second: float = 5.0,
        quiet: bool = True,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Search SEC filings for the given text query.
        
        Args:
            text_query (str): Text to search for in SEC filings.
            filing_date (str or sequence, optional): Filing date or date range filter.
            submission_type (str, optional): Type of SEC submission to search.
            cik (str, int, or list, optional): CIK(s) to filter by.
            ticker (str or list, optional): Ticker(s) to filter by.
            requests_per_second (float, optional): Rate limit for SEC API requests.
            quiet (bool, optional): Whether to suppress output.
            **kwargs: Additional filters to apply.
            
        Returns:
            dict: Search results from the query function.
        """
        # Process CIK and ticker filters if provided
        if cik is not None or ticker is not None:
            cik_list = _process_cik_and_metadata_filters(cik, ticker, **kwargs)
            # Add CIK filter to the query if we have results
            if cik_list:
                # Implementation note: Update as needed - this assumes your query function
                # can accept a cik parameter, otherwise you may need additional logic here
                kwargs['cik'] = cik_list
            
        # Execute the search query
        results = query(
            f'{text_query}',
            filing_date=filing_date,
            requests_per_second=requests_per_second,
            quiet=quiet,
            submission_type=submission_type,
            **kwargs
        )
        

            
        return results
    
