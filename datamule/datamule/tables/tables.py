"""Parse and map structured tables from SEC filings."""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from doc2dict.utils.format_dict import _format_table

from .tables_13fhr import config_13fhr
from .tables_25nse import config_25nse
from .tables_informationtable import config_information_table
from .tables_npx import config_npx
from .tables_ownership import config_ownership
from .tables_proxyvotingrecord import config_proxyvotingrecord
from .tables_sbsef import config_sbsef
from .tables_sdr import config_sdr
from .utils import flatten_dict, safe_get
# will add filing date param later? or extension
all_tables_dict = {
    '3' : config_ownership,
    '3/A' : config_ownership,
    '4' : config_ownership,
    '4/A' : config_ownership,
    '5' : config_ownership,
    '5/A' : config_ownership,
    '13F-HR' : config_13fhr,
    '13F-HR/A' : config_13fhr,
    '13F-NT' : config_13fhr,
    '13F-NT/A' : config_13fhr,
    'INFORMATION TABLE' : config_information_table,
    '25-NSE' : config_25nse,
    '25-NSE/A' : config_25nse,
    'N-PX' : config_npx,
    'N-PX/A' : config_npx,
    'SBSEF' : config_sbsef,
    'SBSEF/A' : config_sbsef,
    'SBSEF-V' : config_sbsef,
    'SBSEF-W' : config_sbsef,
    'SDR' : config_sdr,
    'SDR/A' : config_sdr,
    'SDR-W' : config_sdr,
    'SDR-A' : config_sdr,
    'PROXY VOTING RECORD' : config_proxyvotingrecord,
}

# process_ex102_abs will need to be done later
# process d
# 144

def seperate_data(tables_dict: Dict[str, Dict[str, Any]], data: Dict[str, Any]) -> List[Tuple[str, Any]]:
    """Extract each table section based on configured paths."""
    data_list = []
    
    for table_name, config in tables_dict.items():
        path = config['path']
        
        # Extract data at the specific path
        table_data = safe_get(data, path.split('.'))
        if not table_data:
            continue
            
        # Find sub-paths to exclude (only for paths that have sub-tables)
        sub_paths = [other_path for other_path in [c['path'] for c in tables_dict.values()] 
                    if other_path.startswith(path + '.')]
        
        # Only apply exclusions if this path has sub-paths AND the data is a dict
        if sub_paths and isinstance(table_data, dict):
            exclude_keys = {sp.split('.')[len(path.split('.'))] for sp in sub_paths}
            table_data = {k: v for k, v in table_data.items() if k not in exclude_keys}
        
        data_list.append((table_name, table_data))
    
    return data_list

def apply_mapping(
    flattened_data: Any,
    mapping_dict: Dict[str, str],
    accession: str,
    must_exist_in_mapping: bool = False,
) -> List[Dict[str, Any]]:
    """Apply mapping to flattened data and add accession"""
    
    # Handle case where flattened_data is a list of dictionaries
    if isinstance(flattened_data, list):
        results = []
        for data_dict in flattened_data:
            results.extend(apply_mapping(data_dict, mapping_dict, accession,must_exist_in_mapping))
        return results
    
    # Original logic for single dictionary
    ordered_row = {'accession': accession}
    
    # Apply mapping for all other keys
    for old_key, new_key in mapping_dict.items():
        if old_key in flattened_data:
            ordered_row[new_key] = flattened_data.pop(old_key)
        else:
            ordered_row[new_key] = None
    
    # Add any remaining keys that weren't in the mapping
    if not must_exist_in_mapping:
        for key, value in flattened_data.items():
            ordered_row[key] = value
    
    return [ordered_row]

# TODO, move from dict {} to [[]]
class Table:
    """Represents a single parsed table."""

    def __init__(
        self,
        data: List[Dict[str, Any]],
        name: str,
        accession: str,
        description: Optional[str] = None,
    ) -> None:
        """Initialize a table with rows, name, and accession."""
        self.data = data
        if data != []:
            try:
                self.columns = data[0].keys() # handle xml tables
            except:
                self.columns = data[0] # handle html tables
        self.name = name
        self.accession = accession
        self.description = description

    # TODO MADE IN A HURRY #
    def __str__(self) -> str:
        """Return a formatted string representation of the table."""
        formatted_table = _format_table(self.data)
        if isinstance(formatted_table, list):
            table_str = '\n'.join(formatted_table)
        else:
            table_str = str(formatted_table)
        return f"Table '{self.name}' ({self.accession}) - {len(self.data) if isinstance(self.data, list) else 'N/A'} rows\ndescription: {self.description if self.description else ''}\n{table_str}"


class Tables():
    """Collection of tables parsed from a document."""

    def __init__(self, document_type: str, accession: str) -> None:
        """Initialize with the document type and accession."""
        self.document_type = document_type
        self.accession = accession
        self.tables: List[Table] = []

    def parse_tables(self, data: Dict[str, Any], must_exist_in_mapping: bool = True) -> None:
        """Parse and map tables from structured data."""
        self.data = data

        try:
            tables_dict = all_tables_dict[self.document_type]
        except:
            raise ValueError(f"Table not found: {self.document_type}.")
        
        # now get the dicts from the data
        data_dicts = seperate_data(tables_dict,self.data)

        # now flatten
        data_dicts = [(x,flatten_dict(y)) for x,y in data_dicts]
        
        for table_name, flattened_data in data_dicts:
            mapping_dict = tables_dict[table_name]['mapping']
            mapped_data = apply_mapping(flattened_data, mapping_dict, self.accession,must_exist_in_mapping)
            self.tables.append(Table(mapped_data, table_name, self.accession))
        
    def add_table(self, data: List[Dict[str, Any]], name: str, description: Optional[str] = None) -> None:
        """Add a table to the collection."""
        self.tables.append(Table(data=data,name=name,accession=self.accession,description=description))

    def get_tables(
        self,
        description_regex: Optional[str] = None,
        name: Optional[str] = None,
        contains_regex: Optional[Sequence[str]] = None,
    ) -> List[Table]:
        """Return tables matching name, description, or content patterns."""
        matching_tables = []
        
        for table in self.tables:
            # Check name match (exact match)
            if name is not None:
                if table.name == name:
                    matching_tables.append(table)
                    continue
            
            # Check description regex match
            if description_regex is not None and table.description is not None:
                if re.search(description_regex, table.description):
                    # If contains_regex is also specified, need to check that too
                    if contains_regex is not None:
                        if self._check_contains_regex(table, contains_regex):
                            matching_tables.append(table)
                    else:
                        matching_tables.append(table)
                    continue
            
            # Check contains_regex match (only if description_regex didn't already handle it)
            if contains_regex is not None and description_regex is None and name is None:
                if self._check_contains_regex(table, contains_regex):
                    matching_tables.append(table)
        
        return matching_tables

    def _check_contains_regex(self, table: Table, contains_regex: Sequence[str]) -> bool:
        """Return True when all regex patterns are found in table cells."""
        # Convert all patterns to compiled regex objects
        compiled_patterns = [re.compile(pattern) for pattern in contains_regex]
        
        # Track which patterns have been matched
        patterns_matched = [False] * len(compiled_patterns)
        
        # Iterate through all cells in table.data
        for row in table.data:
            for cell in row:
                # Convert cell to string for regex matching
                cell_str = str(cell)
                
                # Check each pattern that hasn't been matched yet
                for i, pattern in enumerate(compiled_patterns):
                    if not patterns_matched[i]:
                        if pattern.search(cell_str):
                            patterns_matched[i] = True
                
                # Early exit if all patterns have been matched
                if all(patterns_matched):
                    return True
        
        # Return True only if all patterns were matched
        return all(patterns_matched)
