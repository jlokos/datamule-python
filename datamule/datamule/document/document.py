"""Parse and analyze SEC filing documents.

This module defines the `Document` class for parsing filing content into a
structured representation, extracting text, tags, and tables, and exporting
the results in common formats.

Example:
    >>> from datamule.document import Document
    >>> doc = Document(
    ...     type="10-K",
    ...     content=b"...",
    ...     extension=".txt",
    ...     accession="0000320193-23-000077",
    ...     filing_date="2023-10-31",
    ... )
    >>> doc.text  # doctest: +SKIP
"""

from __future__ import annotations

import csv
import json
import re
import tempfile
import webbrowser
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

from doc2dict import html2dict, pdf2dict, txt2dict, unnest_dict, visualize_dict, xml2dict
from doc2dict import flatten_dict, get_title
from secsgml.utils import bytes_to_str

from ..mapping_dicts.html_mapping_dicts import *
from ..mapping_dicts.xml_mapping_dicts import dict_345
from ..tables.tables import Tables
from ..tags.utils import (
    analyze_lm_sentiment_fragment,
    get_all_tickers,
    get_cusip_using_regex,
    get_figi_using_regex,
    get_full_names,
    get_full_names_dictionary_lookup,
    get_isin_using_regex,
)
from ..utils.pdf import has_extractable_text

class DataWithTags(dict):
    """Dictionary wrapper that exposes tag and similarity analysis."""

    def __init__(self, data: Dict[str, Any], document: "Document") -> None:
        """Initialize with parsed data and the source document."""
        super().__init__(data)
        self._document = document
        self._tags: Optional[Tags] = None
    
    @property
    def tags(self) -> "Tags":
        """Return tag extraction results for this document's data."""
        if self._tags is None:
            self._tags = Tags(self._document, mode='data')  # New fragment-based behavior
        return self._tags
    
    @property
    def similarity(self) -> "Similarity":
        """Return similarity/sentiment results for this document's data."""
        if not hasattr(self, '_similarity'):
            self._similarity = Similarity(self._document, mode='data')
        return self._similarity
    
class TextWithTags(str):
    """String wrapper that exposes tag and similarity analysis."""

    def __new__(cls, content: str, document: "Document") -> "TextWithTags":
        """Create a new text wrapper bound to a document."""
        instance = str.__new__(cls, content)
        instance._document = document
        instance._tags = None
        return instance
    
    @property
    def tags(self) -> "Tags":
        """Return tag extraction results for this document's text."""
        if self._tags is None:
            self._tags = Tags(self._document, mode='text')  # Original behavior
        return self._tags
    
    @property
    def similarity(self) -> "Similarity":
        """Return similarity/sentiment results for this document's text."""
        if not hasattr(self, '_similarity'):
            self._similarity = Similarity(self._document, mode='text')
        return self._similarity
        

class Tickers:
    """Lazy ticker extraction for a document's text."""

    def __init__(self, document: "Document") -> None:
        """Initialize with the source document."""
        self.document = document
        self._tickers_data: Optional[Dict[str, List[str]]] = None
    
    def _get_tickers_data(self) -> Dict[str, List[str]]:
        """Return ticker data once and cache it."""
        if self._tickers_data is None:
           self._tickers_data = get_all_tickers(self.document.text)
        return self._tickers_data
    
    def __getattr__(self, exchange_name: str) -> List[str]:
        """Return tickers for a specific exchange key."""
        data = self._get_tickers_data()
        
        if exchange_name in data:
            return data[exchange_name]
        
        return []
    
    def __bool__(self) -> bool:
        """Return True if any tickers were found."""
        data = self._get_tickers_data()
        return bool(data.get('all', []))
    
    def __repr__(self) -> str:
        """Show the full ticker data when printed or accessed directly."""
        data = self._get_tickers_data()
        return str(data)
    
    def __str__(self) -> str:
        """Show the full ticker data when printed."""
        data = self._get_tickers_data()
        return str(data)
    
class TextAnalysisBase:
    """Base class for tag and similarity analysis helpers."""

    def __init__(self, document: "Document", mode: str = 'text') -> None:
        """Initialize analysis with a document and mode."""
        from ..tags.config import _active_dictionaries, _loaded_dictionaries
        self.document = document
        self.mode = mode  # 'text' or 'data'
        self.dictionaries: Dict[str, Any] = {}
        self.processors: Dict[str, Any] = {}
        self._text_sources: Optional[List[Dict[str, Any]]] = None
        
        # Load global dictionaries with their data and processors
        active_dicts = _active_dictionaries
        for dict_name in active_dicts:
            dict_info = _loaded_dictionaries[dict_name]
            self.dictionaries[dict_name] = dict_info['data']
            if dict_info['processor'] is not None:
                self.processors[dict_name] = dict_info['processor']
    
    def _get_text_sources(self) -> List[Dict[str, Any]]:
        """Return text sources based on mode (single text or fragments)."""
        if self._text_sources is None:
            if self.mode == 'text':
                # Original behavior - single text source
                self._text_sources = [{'id': None, 'text': str(self.document.text)}]
            else:  # mode == 'data'
                self._text_sources = [{'id':data_tuple[0],'text':data_tuple[2]} for data_tuple in self.document.data_tuples if data_tuple[1] in ['text','title','textsmall']]
        return self._text_sources
    
    def _format_results(
        self,
        results: Iterable[Tuple[Any, int, int]],
        fragment_id: Optional[Any],
    ) -> List[Tuple[Any, ...]]:
        """Format results based on mode."""
        if self.mode == 'text':
            # Original format: (match, start, end)
            return results
        else:
            # New format: (match, fragment_id, start, end)
            return [(match, fragment_id, start, end) for match, start, end in results]

class Tags(TextAnalysisBase):
    """Extract identifiers and names from a document."""

    def __init__(self, document: "Document", mode: str = 'text') -> None:
        """Initialize tag extraction for a document."""
        super().__init__(document, mode)
        self._tickers: Optional[Tickers] = None
    
    @property
    def cusips(self) -> List[Tuple[Any, ...]]:
        """Return extracted CUSIP identifiers."""
        if not hasattr(self, '_cusips'):
            self._cusips = []
            sources = self._get_text_sources()
            
            for source in sources:
                if 'sc13dg_cusips' in self.dictionaries:
                    keywords = self.dictionaries['sc13dg_cusips']
                    results = get_cusip_using_regex(source['text'], keywords)
                elif "13fhr_information_table_cusips" in self.dictionaries:
                    keywords = self.dictionaries['13fhr_information_table_cusips']
                    results = get_cusip_using_regex(source['text'], keywords)
                else:
                    results = get_cusip_using_regex(source['text'])
                
                # Format results based on mode
                formatted_results = self._format_results(results, source['id'])
                self._cusips.extend(formatted_results)
                    
        return self._cusips
    
    @property
    def isins(self) -> List[Tuple[Any, ...]]:
        """Return extracted ISIN identifiers."""
        if not hasattr(self, '_isins'):
            self._isins = []
            sources = self._get_text_sources()
            
            for source in sources:
                if 'npx_isins' in self.dictionaries:
                    keywords = self.dictionaries['npx_isins']
                    results = get_isin_using_regex(source['text'], keywords)
                else:
                    results = get_isin_using_regex(source['text'])
                
                formatted_results = self._format_results(results, source['id'])
                self._isins.extend(formatted_results)
                    
        return self._isins

    @property
    def figis(self) -> List[Tuple[Any, ...]]:
        """Return extracted FIGI identifiers."""
        if not hasattr(self, '_figis'):
            self._figis = []
            sources = self._get_text_sources()
            
            for source in sources:
                if 'npx_figis' in self.dictionaries:
                    keywords = self.dictionaries['npx_figis']
                    results = get_figi_using_regex(source['text'], keywords)
                else:
                    results = get_figi_using_regex(source['text'])
                
                formatted_results = self._format_results(results, source['id'])
                self._figis.extend(formatted_results)
                    
        return self._figis
    
    @property
    def tickers(self) -> Tickers:
        """Return a ticker accessor for the document."""
        # Tickers work differently - they need the full document context
        # Keep original behavior for now
        if self._tickers is None:
            self._tickers = Tickers(self.document)
        return self._tickers
    
    @property
    def persons(self) -> List[Tuple[Any, ...]]:
        """Return extracted person name matches."""
        if not hasattr(self, '_persons'):
            self._persons = []
            sources = self._get_text_sources()
            for source in sources:
                if '8k_2024_persons' in self.processors:
                    results = get_full_names_dictionary_lookup(source['text'], self.processors['8k_2024_persons'])
                elif 'ssa_baby_first_names' in self.dictionaries:
                    results = get_full_names(source['text'], self.dictionaries['ssa_baby_first_names'])
                else:
                    results = get_full_names(source['text'])
                
                formatted_results = self._format_results(results, source['id'])
                self._persons.extend(formatted_results)
                    
        return self._persons

class Similarity(TextAnalysisBase):
    """Sentiment/similarity analyses derived from document text."""
    @property
    def loughran_mcdonald(self) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Return Loughran-McDonald sentiment analysis results."""
        if not hasattr(self, '_loughran_mcdonald'):
            self._loughran_mcdonald = []
            sources = self._get_text_sources()
            
            if 'loughran_mcdonald' in self.processors:
                lm_processors = self.processors['loughran_mcdonald']
                
                for source in sources:
                    results = analyze_lm_sentiment_fragment(source['text'], lm_processors)
                    
                    if self.mode == 'text':
                        # Single result for whole document
                        self._loughran_mcdonald = results
                        break
                    else:
                        # Per-fragment results with fragment_id
                        fragment_result = {
                            'fragment_id': source['id'],
                            **results
                        }
                        self._loughran_mcdonald.append(fragment_result)
            else:
                # No processors available
                self._loughran_mcdonald = [] if self.mode == 'data' else {}
                    
        return self._loughran_mcdonald


class Document:
    """Represents a single filing document and its parsed artifacts.

    Attributes:
        type (str): SEC document type (e.g., "10-K", "EX-99.1").
        accession (str): Accession number for the parent submission.
        filing_date (str): Filing date in YYYY-MM-DD format.
        extension (str): File extension for the raw content.
        path (Optional[Path]): Optional source path for the document.
    """

    def __init__(
        self,
        type: str,
        content: Union[bytes, str],
        extension: str,
        accession: str,
        filing_date: str,
        path: Optional[Union[Path, str]] = None,
    ) -> None:
        """Initialize a document with raw content and identifiers."""
        self.type = type
        extension = extension.lower()
        self.accession = accession
        self.filing_date = filing_date

        if self.type == 'submission_metadata':
            # this converts to lower
            self.content = bytes_to_str(content)
        else:
            self.content = content

        if path is not None:
            self.path = path

        self.extension = extension

        # this will be filled by parsed
        self._data: Optional[Union[Dict[str, Any], DataWithTags]] = None
        self._data_tuples: Optional[List[Tuple[Any, Any, Any, Any]]] = None
        self._tables: Optional[Tables] = None
        self._text: Optional[TextWithTags] = None
        self._markdown: Optional[str] = None

        # booleans
        self._data_bool = self.extension in ('.htm', '.html','.txt')

        # may slow things down?
        if self.extension == '.pdf':
            if has_extractable_text(pdf_bytes=self.content):
                self._data_bool = True

        self._data_tuples_bool = self._data_bool
        self._text_bool = self._data_bool
        self._markdown_bool = self._data_bool
        self._visualize_bool = self._data_bool
        self._tables_bool = self.extension in ('.xml')
        


    def contains_string(self, pattern: Union[str, bytes]) -> bool:
        """Return True when the raw content contains a regex pattern."""
        if self.extension in ['.htm', '.html', '.txt','.xml']:
            return bool(re.search(pattern, self.content))
        return False
    
    def parse(self) -> None:
        """Parse raw content into structured data when supported."""
        # check if we have already parsed the content
        if self._data:
            return
        
        mapping_dict = None
        if self._data_bool:
            
            if self.type in ['1-K', '1-K/A']:
                mapping_dict = dict_1kpartii_html
            elif self.type in ['1-SA', '1-SA/A']:
                mapping_dict = dict_1sa_html
            elif self.type in ['1-U', '1-U/A']:
                mapping_dict = dict_1u_html
            elif self.type in ['10-12B', '10-12B/A']:
                mapping_dict = dict_1012b_html
            elif self.type in ['10-D', '10-D/A']:
                mapping_dict = dict_10d_html
            elif self.type in ['10-K', '10-K/A']:
                mapping_dict = dict_10k_html
            elif self.type in ['10-Q', '10-Q/A']:
                mapping_dict = dict_10q_html
            elif self.type in ['20-F', '20-F/A']:
                mapping_dict = dict_20f_html
            elif self.type in ['8-A12B', '8-A12B/A']:
                mapping_dict = dict_8a12b_html
            elif self.type in ['8-A12G', '8-A12G/A']:
                mapping_dict = dict_8a12g_html
            elif self.type in ['8-K', '8-K/A']:
                mapping_dict = dict_8k_html
            elif self.type in ['8-K12B', '8-K12B/A']:
                mapping_dict = dict_8k12b_html
            elif self.type in ['8-K12G3', '8-K12G3/A']:
                mapping_dict = dict_8k12g3_html
            elif self.type in ['8-K15D5', '8-K15D5/A']:
                mapping_dict = dict_8k15d5_html
            elif self.type in ['ABS-15G', 'ABS-15G/A']:
                mapping_dict = dict_abs15g_html
            elif self.type in ['ABS-EE', 'ABS-EE/A']:
                mapping_dict = dict_absee_html
            elif self.type in ['APP NTC', 'APP NTC/A']:
                mapping_dict = dict_appntc_html
            elif self.type in ['CB', 'CB/A']:
                mapping_dict = dict_cb_html
            elif self.type in ['DSTRBRPT', 'DSTRBRPT/A']:
                mapping_dict = dict_dstrbrpt_html
            elif self.type in ['N-18F1', 'N-18F1/A']:
                mapping_dict = dict_n18f1_html
            elif self.type in ['N-CSRS', 'N-CSRS/A']:
                mapping_dict = dict_ncsrs_html
            elif self.type in ['NT-10K', 'NT-10K/A']:
                mapping_dict = dict_nt10k_html
            elif self.type in ['NT-10Q', 'NT-10Q/A']:
                mapping_dict = dict_nt10q_html
            elif self.type in ['NT 20-F', 'NT 20-F/A']:
                mapping_dict = dict_nt20f_html
            elif self.type in ['NT-NCEN', 'NT-NCEN/A']:
                mapping_dict = dict_ntncen_html
            elif self.type in ['NT-NCSR', 'NT-NCSR/A']:
                mapping_dict = dict_ntncsr_html
            elif self.type in ['NTFNCEN', 'NTFNCEN/A']:
                mapping_dict = dict_ntfcen_html
            elif self.type in ['NTFNCSR', 'NTFNCSR/A']:
                mapping_dict = dict_ntfncsr_html
            elif self.type in ['EX-99.CERT', 'EX-99.CERT/A']:
                mapping_dict = dict_ex99cert_html
            elif self.type in ['SC 13E3', 'SC 13E3/A']:
                mapping_dict = dict_sc13e3_html
            elif self.type in ['SC 14D9', 'SC 14D9/A']:
                mapping_dict = dict_sc14d9_html
            elif self.type in ['SP 15D2', 'SP 15D2/A']:
                mapping_dict = dict_sp15d2_html
            elif self.type in ['SD', 'SD/A']:
                mapping_dict = dict_sd_html
            elif self.type in ['S-1', 'S-1/A']:
                mapping_dict = dict_s1_html
            elif self.type in ['T-3', 'T-3/A']:
                mapping_dict = dict_t3_html
            elif self.type in ['NT 10-K', 'NT 10-K/A', 'NT 10-Q', 'NT 10-Q/A', 'NT 20-F', 'NT 20-F/A']:
                mapping_dict = dict_nt10k_html
            elif self.type in ['SC 13G', 'SC 13G/A']:
                mapping_dict = dict_13g
            elif self.type in ['SC 13D', 'SC 13D/A']:
                mapping_dict = dict_13d
            
            if self.extension in ['.htm','.html']:
                dct = html2dict(content=self.content, mapping_dict=mapping_dict)
            elif self.extension in ['.txt']:
                dct = txt2dict(content=self.content, mapping_dict=mapping_dict)
            elif self.extension == '.pdf':
                dct = pdf2dict(content=self.content, mapping_dict=mapping_dict)
            else:
                dct = {}
            
            self._data = dct
        elif self.extension == '.xml':
            if self.type in ['3', '4', '5', '3/A', '4/A', '5/A']:
                mapping_dict = dict_345
            self._data = xml2dict(content=self.content, mapping_dict=mapping_dict)

        else:
            pass

    @property
    def data(self) -> Optional[Union[Dict[str, Any], DataWithTags]]:
        """Return parsed data (with tags for text-based documents)."""
        if self._data_bool:
            if self._data is None:
                self.parse()

            if self._data is None:
                self._data = {}
            
            if not isinstance(self._data, DataWithTags):
                self._data = DataWithTags(self._data, self)
        elif self.extension == '.xml':
            if self._data is None:
                self.parse()

            if self._data is None:
                self._data = {}
            
        return self._data
    
    @property
    def data_tuples(self) -> Optional[List[Tuple[Any, Any, Any, Any]]]:
        """Return flattened data tuples for text extraction."""
        if self._data_bool:
            if self._data_tuples is None:
                self._data_tuples = unnest_dict(self.data)
        return self._data_tuples
    
    @property
    def text(self) -> Optional[TextWithTags]:
        """Return flattened text with tag helpers when supported."""
        if self._text_bool:
            if self._text is None:
                text = flatten_dict(tuples_list=self.data_tuples,format='text')
                self._text = TextWithTags(text, self)
        return self._text
    
    @property
    def markdown(self) -> Optional[str]:
        """Return flattened markdown text when supported."""
        if self._markdown_bool:
            if self._markdown is None:
                self._markdown = flatten_dict(tuples_list=self.data_tuples,format='markdown')

        return self._markdown

    
    def write_json(self, output_filename: Union[str, Path]) -> None:
        """Write parsed data to a JSON file."""
        if not self.data:
            self.parse()
            
        with open(output_filename, 'w',encoding='utf-8') as f:
            json.dump(self.data, f, indent=2)

    def parse_tables(self, must_exist_in_mapping: bool = True) -> None:
        """Parse tables from the document and cache them."""
        if self.extension == '.xml':
            tables = Tables(document_type = self.type, accession=self.accession)
            tables.parse_tables(data=self.data,must_exist_in_mapping=must_exist_in_mapping)
            self._tables = tables

        elif self._data_bool:
            tables = Tables(document_type = self.type, accession=self.accession)
            data_tuples = self.data_tuples
            
            for i, (id, type, content, level) in enumerate(data_tuples):
                if type == "table" and i > 0:
                    description = None
                    
                    # Look at previous element
                    prev_id, prev_type, prev_content, prev_level = data_tuples[i-1]
                    
                    # Case 1: Same level + text content
                    if prev_level == level and prev_type in ["text", "textsmall"]:
                        description = prev_content
                    
                    # Case 2: Higher level (lower number) + title
                    elif prev_level < level and prev_type == "title":
                        description = prev_content
                    
                    # Case 3: No matching description - add table without description
                    # (description remains None)
                    
                    tables.add_table(data=content, description=description, name="extracted_table")

            self._tables = tables

        else:
            self._tables = []

    @property
    def tables(self) -> List[Any]:
        """Return extracted tables for the document."""
        if self._tables is None:
            self.parse_tables()
        return self._tables.tables
    

    def write(self, file: Union[str, Path]) -> None:
        """Write raw content to a file."""
        with open(file, 'wb') as f:
            f.write(self.content)


    def write_csv(self, output_folder: Union[str, Path]) -> None:
        """Write extracted tables to CSV files in a folder."""
        output_folder = Path(output_folder)
        output_folder.mkdir(exist_ok=True)
            
        tables = self.tables

        if not tables:
            return
        
        for table in tables:
            fieldnames = table.columns
            output_filename = output_folder / f"{table.name}.csv"

            # Check if the file already exists
            if output_filename.exists():
        
                with open(output_filename, 'a', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile,fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
                    writer.writerows(table.data)
            else:
                with open(output_filename, 'w', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
                    writer.writeheader()
                    writer.writerows(table.data)

    def reset_nlp(self) -> None:
        """Reset NLP analysis by recreating wrapper objects."""
        # Reset data wrapper
        if hasattr(self, '_data') and self._data is not None:
            raw_data = dict(self._data)  # Extract the underlying dict
            self._data = DataWithTags(raw_data, self)
        
        # Reset text wrapper
        if hasattr(self, '_text') and self._text is not None:
            raw_text = str(self._text)  # Extract the underlying string
            self._text = TextWithTags(raw_text, self)
        
    def _document_to_section_text(
        self,
        document_data: Any,
        parent_key: str = '',
    ) -> List[Dict[str, str]]:
        """Flatten nested document data into section/text pairs."""
        items = []
        
        if isinstance(document_data, dict):
            for key, value in document_data.items():
                # Build the section name
                section = f"{parent_key}_{key}" if parent_key else key
                
                # If the value is a dict, recurse
                if isinstance(value, dict):
                    items.extend(self._document_to_section_text(value, section))
                # If it's a list, handle each item
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            items.extend(self._document_to_section_text(item, f"{section}_{i+1}"))
                        else:
                            items.append({
                                'section': f"{section}_{i+1}",
                                'text': str(item)
                            })
                # Base case - add the item
                else:
                    items.append({
                        'section': section,
                        'text': str(value)
                    })
        
        return items
    
    def visualize(self) -> None:
        """Visualize parsed data when available."""
        if not self.data:
            self.parse()

        if not self.data:
            pass
        else:
            visualize_dict(self.data)

    # alpha feature
    def open(self) -> None:
        """Open the document in a browser or viewer (experimental)."""
        if self.extension in ['.htm', '.html','.txt','.jpg','.png', '.pdf']:
            # Create a temporary file with the content and open it

            with tempfile.NamedTemporaryFile(mode='wb', suffix=self.extension, delete=False) as f:
                f.write(self.content)
                temp_path = f.name
            webbrowser.open('file://' + temp_path)
        else:
            print(f"Cannot open files with extension {self.extension}")

    def get_section(
        self,
        title: Optional[str] = None,
        title_regex: Optional[str] = None,
        title_class: Optional[str] = None,
        format: str = 'dict',
    ) -> List[Any]:
        """Return sections matching a title or regex."""
        if self._data_bool:
            if not self.data:
                self.parse()

            result = get_title(self.data,title=title,title_regex=title_regex,title_class=title_class)
            if format == 'dict':
                return [item[1] for item in result]
            else:
                return [flatten_dict(item[1],format) for item in result]


    def get_tables(
        self,
        description_regex: Optional[str] = None,
        name: Optional[str] = None,
        contains_regex: Optional[str] = None,
    ) -> List[Any]:
        """Return tables matching description/name/content filters."""
        # make sure tables is initialized
        self.tables
        return self._tables.get_tables(description_regex=description_regex, name=name, contains_regex=contains_regex)
