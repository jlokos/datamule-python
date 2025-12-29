"""Convenience wrappers around helper utilities."""

from __future__ import annotations

from typing import List, Sequence, Union

from ..helper import _process_cik_and_metadata_filters


def get_ciks_from_tickers(tickers: Union[str, Sequence[str]]) -> List[int]:
    """Return CIKs for one or more ticker symbols."""
    return _process_cik_and_metadata_filters(ticker=tickers)
