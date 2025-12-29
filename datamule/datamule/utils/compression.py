"""Compression helpers for zstandard content."""

from __future__ import annotations

import io
import shutil
from typing import Iterable, Optional, Sequence, Union

import zstandard as zstd


def create_compressor(level: int = 6) -> zstd.ZstdCompressor:
    """Create a Zstandard compressor at the given level."""
    return zstd.ZstdCompressor(level=level)


def compress_content(
    content: Union[str, bytes],
    compressor: zstd.ZstdCompressor,
    encoding: str = 'utf-8',
) -> bytes:
    """Compress text or bytes content with a zstd compressor."""
    if isinstance(content, str):
        content_bytes = content.encode(encoding)
    else:
        content_bytes = content
    
    compressed = compressor.compress(content_bytes)
    return compressed


def decompress_content(compressed_data: Union[bytes, Sequence[bytes]]) -> bytes:
    """Decompress zstd data from bytes or a list of chunks."""
    dctx = zstd.ZstdDecompressor()
    
    # Handle both single bytes object and list of chunks
    if isinstance(compressed_data, list):
        input_buffer = io.BytesIO(b''.join(compressed_data))
    else:
        input_buffer = io.BytesIO(compressed_data)
    
    decompressed_content = io.BytesIO()
    
    try:
        with dctx.stream_reader(input_buffer) as reader:
            shutil.copyfileobj(reader, decompressed_content)
        
        return decompressed_content.getvalue()
    finally:
        input_buffer.close()
        decompressed_content.close()
