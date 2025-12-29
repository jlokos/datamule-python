"""Create compressed tar archives for submission documents."""

from __future__ import annotations

import io
import json
import tarfile
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Union

import zstandard as zstd
from secsgml.utils import calculate_documents_locations_in_tar


def compress_content(
    content: Union[bytes, str],
    compression_type: Optional[str],
    level: Optional[int],
    threshold: Optional[int],
) -> bytes:
    """Compress raw content when configured to use zstd."""
    if compression_type == 'zstd':
        # Handle string content
        if isinstance(content, str):
            content_bytes = content.encode('utf-8')
        else:
            content_bytes = content

        # If content smaller than threshold, return uncompressed
        if threshold is not None and len(content_bytes) < threshold:
            return content_bytes

        # Compress with specified level
        compressor = zstd.ZstdCompressor(level=level)
        return compressor.compress(content_bytes)

    # Return uncompressed if not zstd
    return content


def compress_content_list(
    document_tuple_list: Sequence[Tuple[Union[bytes, str], str]],
    compression_type: Optional[str],
    level: Optional[int],
    threshold: Optional[int],
) -> List[Tuple[bytes, str]]:
    """Compress document content tuples when compression is enabled."""
    if compression_type is None:
        return document_tuple_list
    
    if level is None:
        level = 3

    compressed_list = []
    for content, accession in document_tuple_list:
        compressed_content = compress_content(content, compression_type, level, threshold)
        compressed_list.append((compressed_content, accession))
    
    return compressed_list


def tar_content_list(
    metadata: Dict[str, Any],
    document_tuple_list_compressed: Sequence[Tuple[bytes, str]],
) -> io.BytesIO:
    """Create a tar buffer from metadata and compressed content tuples."""
    # Update metadata with compressed sizes
    for i, (content, accession) in enumerate(document_tuple_list_compressed):  
        metadata['documents'][i]['secsgml_size_bytes'] = len(content)
    
    metadata = calculate_documents_locations_in_tar(metadata)

    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode='w') as tar:  
        # Add metadata first
        metadata_json = json.dumps(metadata).encode('utf-8')
        tarinfo = tarfile.TarInfo(f'metadata.json')
        tarinfo.size = len(metadata_json)
        tar.addfile(tarinfo, io.BytesIO(metadata_json))
        
        # Add each content
        for i, (content, accession) in enumerate(document_tuple_list_compressed): 
            doc = metadata['documents'][i]
            filename = doc.get('filename', doc['sequence'] + '.txt')
            
            tarinfo = tarfile.TarInfo(name=filename)
            tarinfo.size = len(content)
            tar.addfile(tarinfo, io.BytesIO(content)) 
    
    tar_buffer.seek(0)  # Reset buffer position
    return tar_buffer


def tar_submission(
    metadata: Dict[str, Any],
    documents_obj_list: Sequence[Any],
    compression_type: Optional[str] = None,
    level: Optional[int] = None,
    threshold: Optional[int] = None,
) -> io.BytesIO:
    """Takes a list of documents, compresses them (if above threshold), then tars them."""
    document_tuple_list = [(doc.content, doc.accession) for doc in documents_obj_list]
    document_tuple_list_compressed = compress_content_list(
        document_tuple_list,
        compression_type=compression_type, 
        level=level,
        threshold=threshold
    )

    return tar_content_list(metadata, document_tuple_list_compressed)
