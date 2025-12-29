"""Dictionary management for SEC filing data analysis.

This module provides functionality to download and load various reference dictionaries
used for tagging and analyzing SEC filings. Dictionaries include name lists, financial
identifiers (CUSIPs, ISINs, FIGIs), and sentiment word lists.

Available dictionaries:
    - ssa_baby_first_names: SSA baby first names for person identification
    - npx_figis: Financial Instrument Global Identifiers from NPX filings
    - npx_isins: International Securities Identification Numbers from NPX filings
    - sc13dg_cusips: CUSIPs from Schedule 13D/G filings
    - 13fhr_information_table_cusips: CUSIPs from 13F-HR information tables
    - 8k_2024_persons: Person names extracted from 2024 8-K filings
    - loughran_mcdonald: Loughran-McDonald financial sentiment word lists
"""

from pathlib import Path
from typing import Dict, List, Optional, Set, Union
import urllib.request
import json
import csv


urls: Dict[str, str] = {
    "ssa_baby_first_names": "https://raw.githubusercontent.com/john-friedman/datamule-data/master/data/dictionaries/ssa_baby_first_names.txt",
    "npx_figis" : "https://raw.githubusercontent.com/john-friedman/datamule-data/master/data/dictionaries/npx_figis.txt",
    "npx_isins" : "https://raw.githubusercontent.com/john-friedman/datamule-data/master/data/dictionaries/npx_isins.txt",
    "sc13dg_cusips" : "https://raw.githubusercontent.com/john-friedman/datamule-data/master/data/dictionaries/sc13dg_cusips.txt",
    "8k_2024_persons" : "https://raw.githubusercontent.com/john-friedman/datamule-data/master/data/dictionaries/8k_2024_persons.json",
    "13fhr_information_table_cusips" : "https://raw.githubusercontent.com/john-friedman/datamule-data/refs/heads/master/data/dictionaries/13fhr_information_table_cusips.txt",
    "loughran_mcdonald" : "https://drive.usercontent.google.com/u/0/uc?id=1cfg_w3USlRFS97wo7XQmYnuzhpmzboAY&export=download"
}


def download_dictionary(name: str, overwrite: bool = False) -> None:
    """Download a dictionary file from the remote data repository.

    Downloads the specified dictionary to the local ~/.datamule/dictionaries
    directory. If the file already exists and overwrite is False, the download
    is skipped.

    Args:
        name: The name of the dictionary to download. Must be one of the keys
            in the `urls` dictionary (e.g., 'ssa_baby_first_names', 'npx_figis').
        overwrite: If True, download the file even if it already exists locally.
            Defaults to False.

    Raises:
        KeyError: If the dictionary name is not found in the `urls` dictionary.
        urllib.error.URLError: If the download fails due to network issues.

    Example:
        >>> download_dictionary('ssa_baby_first_names')
        Downloading ssa_baby_first_names dictionary to ~/.datamule/dictionaries/ssa_baby_first_names.txt
    """
    url = urls[name]
    
    # Create dictionaries directory in datamule folder
    dict_dir = Path.home() / ".datamule" / "dictionaries"
    dict_dir.mkdir(parents=True, exist_ok=True)

    # check if file exists first
    if not overwrite:
        if name == "loughran_mcdonald":
            filename = "loughran_mcdonald.csv"
        else:
            filename = url.split('/')[-1]
        file_path = dict_dir / filename
        if file_path.exists():
            return 
    
    # Extract filename from URL
    if name == "loughran_mcdonald":
        filename = "loughran_mcdonald.csv"
    else:
        filename = url.split('/')[-1]
    file_path = dict_dir / filename
    
    print(f"Downloading {name} dictionary to {file_path}")
    urllib.request.urlretrieve(url, file_path)
    return
    
def load_dictionary(name: str) -> Union[Set[str], List[str], Dict[str, Set[str]]]:
    """Load a dictionary from the local cache, downloading if necessary.

    Retrieves the specified dictionary, downloading it first if not already
    present in the local cache. The return type depends on the dictionary:

    - Most dictionaries return a set of strings (names, identifiers, etc.)
    - '8k_2024_persons' returns a list of person data
    - 'loughran_mcdonald' returns a dict mapping sentiment categories to word sets

    Args:
        name: The name of the dictionary to load. Must be one of:
            'ssa_baby_first_names', 'npx_figis', 'npx_isins', 'sc13dg_cusips',
            '13fhr_information_table_cusips', '8k_2024_persons', 'loughran_mcdonald'.

    Returns:
        The loaded dictionary data. Type varies by dictionary:
            - Set[str]: For identifier dictionaries (CUSIPs, ISINs, FIGIs, names)
            - List[str]: For '8k_2024_persons'
            - Dict[str, Set[str]]: For 'loughran_mcdonald' (category -> word set)

    Raises:
        ValueError: If the dictionary name is not recognized.
        KeyError: If the dictionary name is not found in the `urls` dictionary.

    Example:
        >>> names = load_dictionary('ssa_baby_first_names')
        >>> 'JOHN' in names
        True
        >>> lm = load_dictionary('loughran_mcdonald')
        >>> 'negative' in lm
        True
    """
    # Get or download the dictionary file
    dict_dir = Path.home() / ".datamule" / "dictionaries"
    
    if name == "loughran_mcdonald":
        filename = "loughran_mcdonald.csv"
    else:
        filename = urls[name].split('/')[-1]
    file_path = dict_dir / filename
    
    # Download if doesn't exist
    if not file_path.exists():
        download_dictionary(name)
    
    # Load the dictionary based on name
    if name == "ssa_baby_first_names":
        names_set = set()
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                names_set.add(line.strip())
        return names_set
    elif name == "npx_figis":
        figi_set = set()
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                figi_set.add(line.strip())
        return figi_set
    elif name == "npx_isins":
        isin_set = set()
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                isin_set.add(line.strip())
        return isin_set
    elif name == "sc13dg_cusips":
        cusip_set = set()
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                cusip_set.add(line.strip())
        return cusip_set
    elif name == "13fhr_information_table_cusips":
        cusip_set = set()
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                cusip_set.add(line.strip())
        return cusip_set
    elif name == "8k_2024_persons":
        with open(file_path, 'r', encoding='utf-8') as f:
            persons_list = json.load(f)
        return persons_list
    elif name == "loughran_mcdonald":
        # Load the Loughran-McDonald dictionary using base Python CSV
        lm_dict = {}
        categories = ['Negative', 'Positive', 'Uncertainty', 'Litigious', 
                    'Strong_Modal', 'Weak_Modal', 'Constraining']
        
        # Initialize category sets
        for category in categories:
            lm_dict[category.lower()] = set()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                word = row['Word'].lower()
                for category in categories:
                    value = row.get(category)
                    # Check if value exists and is not 0 (words added in specific years)
                    if value and str(value).strip() != '0':
                        lm_dict[category.lower()].add(word)
        
        return lm_dict
    else:
        raise ValueError("dictionary not found")
    
download_dictionary('loughran_mcdonald')