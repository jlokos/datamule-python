"""High-level sheet-like access to DataMule datasets."""

from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from company_fundamentals import construct_fundamentals
from company_fundamentals.utils import get_fundamental_mappings

from ..datamule.datamule_mysql_rds import query_mysql_rds
from ..helper import _process_cik_and_metadata_filters


class Sheet:
    """Fetch and export DataMule tables to disk."""

    def __init__(self, path: str, api_key: Optional[str] = None) -> None:
        """Initialize a Sheet with an output path and optional API key."""
        self.path = Path(path)
        self._api_key = api_key
    
    @property
    def api_key(self) -> Optional[str]:
        """Return the API key from memory or environment."""
        return getattr(self, '_api_key', None) or os.getenv('DATAMULE_API_KEY')

    @api_key.setter
    def api_key(self, value: str) -> None:
        """Set the API key for authenticated requests."""
        if not value:
            raise ValueError("API key cannot be empty")
        self._api_key = value
    
    def get_table(self, database: str, **kwargs: Any) -> Any:
        """Return table data from the DataMule API.

        If database is "fundamentals", this constructs a fundamentals view from
        XBRL records using the selected mappings.
        """
        if 'cik' in kwargs or 'ticker' in kwargs:
            # Get ticker and remove it from kwargs if present
            ticker = kwargs.pop('ticker', None)
            
            # Get cik from kwargs, or None if it doesn't exist
            cik = kwargs.get('cik')
            
            # Process cik and add/update it in kwargs
            kwargs['cik'] = _process_cik_and_metadata_filters(cik, ticker)

        if database == 'fundamentals':
            fundamentals = kwargs.pop('fundamentals', None)
            if fundamentals is None:
                raise ValueError("fundamentals parameter required for fundamentals table")
            
            categories = kwargs.pop('categories',None)
            
            mappings = get_fundamental_mappings(fundamentals=fundamentals)
            #print(mappings)
            taxonomies = [item[0] for item in mappings]
            names = [item[1] for item in mappings]
            xbrl = query_mysql_rds(database='simple-xbrl',taxonomy=taxonomies,name=names,api_key=self.api_key,**kwargs)
            #print(xbrl)

            return construct_fundamentals(xbrl, 'taxonomy', 'name', 'period_start_date', 'period_end_date', categories=categories,fundamentals=fundamentals)
            
        else:
            return query_mysql_rds(database=database,**kwargs)

    # def download_xbrl(
    #     self, 
    #     cik=None, 
    #     ticker=None, 
    #     **kwargs
    # ):
    #     # If no CIK or ticker specified, get all companies with tickers
    #     if cik is None and ticker is None:
    #         cik = [row['cik'] for row in load_package_dataset('company_tickers')]
            
    #     # Normalize cik to list format
    #     if isinstance(cik, (str, int)):
    #         cik = [cik]
            
    #     # Process CIK and metadata filters
    #     cik_list = _process_cik_and_metadata_filters(cik, ticker, **kwargs)
        
    #     # Download facts for all CIKs in parallel
    #     download_company_facts(cik=cik_list, output_dir=self.path)

    def write_table(
        self,
        database: str,
        table: Optional[str] = None,
        filename: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Fetch a table and write it to a CSV file."""
        # Get the data using existing get_table method
        data = self.get_table(database=database, table=table, **kwargs)
        
        # If filename not provided, create a default one
        if filename is None:
            if table:
                filename = f"{database}_{table}.csv"
            else:
                filename = f"{database}.csv"
        
        # Ensure filename has an extension
        if not filename.endswith('.csv'):
            filename = f"{filename}.csv"
        
        # Use existing _download_to_csv method to write the file
        self._download_to_csv(data, filename, verbose=True)
        


    def _download_to_csv(
        self,
        data: List[Dict[str, Any]],
        filepath: str,
        verbose: bool = False,
    ) -> List[Dict[str, Any]]:
        """Write a list of dict rows to a CSV file."""
        # If no data returned, nothing to save
        if not data:
            if verbose:
                print("No data returned from API. No file was created.")
            return data
        
        # Resolve filepath - if it's not absolute, make it relative to self.path
        filepath_obj = Path(filepath)
        if not filepath_obj.is_absolute():
            filepath_obj = self.path / filepath_obj
        
        # Create directory if it doesn't exist
        os.makedirs(filepath_obj.parent, exist_ok=True)
        
        # Get fieldnames from the first record
        fieldnames = data[0].keys()
        
        # Write to CSV
        with open(filepath_obj, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
            
        if verbose:
            print(f"Saved {len(data)} records to {filepath_obj}")
            
    
