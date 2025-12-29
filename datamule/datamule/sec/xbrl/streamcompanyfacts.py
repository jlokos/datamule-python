"""
Stream company facts from SEC XBRL API.

This module provides functionality to fetch XBRL company facts data from the SEC's
public API. It supports both single and batch CIK requests with built-in rate
limiting, progress tracking, and error handling.

The SEC's company facts API provides structured XBRL data for SEC filers,
including financial metrics, filing dates, and other standardized data points.
"""

import asyncio
from typing import Any, Callable, Dict, List, Optional, Union

import aiohttp
import json
from tqdm import tqdm
from ..utils import PreciseRateLimiter, RateMonitor, headers

async def fetch_company_facts(
    session: aiohttp.ClientSession,
    cik: Union[str, int],
    rate_limiter: PreciseRateLimiter,
    rate_monitor: RateMonitor,
    pbar: tqdm
) -> Dict[str, Any]:
    """
    Fetch company facts for a single CIK from the SEC XBRL API.

    This is an internal async function that handles the HTTP request to the SEC's
    company facts endpoint. It includes automatic retry logic for rate limiting
    (HTTP 429) responses and tracks request/bandwidth metrics.

    Args:
        session: The aiohttp client session to use for the request.
        cik: The Central Index Key (CIK) of the company. Can be provided as
            a string or integer; will be zero-padded to 10 digits.
        rate_limiter: A PreciseRateLimiter instance to control request frequency.
        rate_monitor: A RateMonitor instance to track request and bandwidth metrics.
        pbar: A tqdm progress bar instance for displaying progress.

    Returns:
        A dictionary containing the company facts data from the SEC API.
        If an error occurs, returns a dictionary with 'error' and 'cik' keys.
    """
    # Format CIK with leading zeros to 10 digits
    formatted_cik = f"CIK{str(cik).zfill(10)}"
    url = f"https://data.sec.gov/api/xbrl/companyfacts/{formatted_cik}.json"
    
    try:
        # Acquire rate limit token
        await rate_limiter.acquire()
        
        async with session.get(url, headers=headers) as response:
            content_length = int(response.headers.get('Content-Length', 0))
            await rate_monitor.add_request(content_length)
            
            # Log current rates
            req_rate, mb_rate = rate_monitor.get_current_rates()
            pbar.set_postfix({"req/s": req_rate, "MB/s": mb_rate})
            
            # Handle rate limiting
            if response.status == 429:
                retry_after = int(response.headers.get('Retry-After', 601))
                pbar.set_description(f"Rate limited, retry after {retry_after}s")
                await asyncio.sleep(retry_after)
                pbar.set_description(f"Fetching CIK {cik}")
                return await fetch_company_facts(session, cik, rate_limiter, rate_monitor, pbar)
            
            # Handle other errors
            if response.status != 200:
                pbar.update(1)
                return {"error": f"HTTP {response.status}", "cik": cik}
            
            data = await response.json()
            pbar.update(1)
            return data
    
    except Exception as e:
        pbar.update(1)
        return {"error": str(e), "cik": cik}

async def stream_companyfacts(
    cik: Optional[Union[str, int, List[Union[str, int]]]] = None,
    requests_per_second: int = 5,
    callback: Optional[Callable[[Dict[str, Any]], None]] = None
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Asynchronously stream company facts for one or more CIKs from the SEC XBRL API.

    This async function fetches XBRL company facts data from the SEC's public API.
    It supports fetching data for a single CIK or multiple CIKs concurrently with
    built-in rate limiting to comply with SEC rate limits.

    Args:
        cik: The Central Index Key(s) to fetch data for. Can be a single CIK
            (as string or integer) or a list of CIKs. If None, returns an error.
        requests_per_second: Maximum number of requests per second to the SEC API.
            Defaults to 5 to stay within SEC rate limits.
        callback: Optional callback function that is called with each successfully
            fetched company facts dictionary. Not called for error responses.

    Returns:
        If a single CIK is provided, returns a dictionary with the company facts.
        If multiple CIKs are provided, returns a list of dictionaries.
        Error responses include 'error' and 'cik' keys.

    Example:
        >>> import asyncio
        >>> result = asyncio.run(stream_companyfacts(cik="320193"))  # Apple
        >>> print(result.get("entityName"))
        'Apple Inc.'
    """
    if cik is None:
        return {"error": "No CIK provided. Please specify a CIK."}
    
    # Handle both single CIK and list of CIKs
    if not isinstance(cik, list):
        cik_list = [cik]
    else:
        cik_list = cik
    
    # Initialize rate limiter and monitor
    rate_limiter = PreciseRateLimiter(rate=requests_per_second)
    rate_monitor = RateMonitor(window_size=10.0)
    
    # Create progress bar
    pbar = tqdm(total=len(cik_list), desc="Fetching company facts")
    
    results = []
    async with aiohttp.ClientSession() as session:
        # Create tasks for all CIKs
        tasks = [
            fetch_company_facts(session, cik_item, rate_limiter, rate_monitor, pbar)
            for cik_item in cik_list
        ]
        
        # Process tasks as they complete
        for completed_task in asyncio.as_completed(tasks):
            data = await completed_task
            
            # Call callback if provided
            if callback and not (data and 'error' in data):
                callback(data)
            
            results.append(data)
    
    pbar.close()
    
    # If single CIK was passed, return just that result
    if len(cik_list) == 1:
        return results[0]
    
    # Otherwise return all results
    return results

def stream_company_facts(
    cik: Optional[Union[str, int, List[Union[str, int]]]] = None,
    requests_per_second: int = 5,
    callback: Optional[Callable[[Dict[str, Any]], None]] = None
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Synchronously stream company facts for one or more CIKs from the SEC XBRL API.

    This is a synchronous wrapper around the async `stream_companyfacts` function.
    It fetches XBRL company facts data from the SEC's public API with built-in
    rate limiting and progress tracking.

    Args:
        cik: The Central Index Key(s) to fetch data for. Can be a single CIK
            (as string or integer) or a list of CIKs. If None, returns an error.
        requests_per_second: Maximum number of requests per second to the SEC API.
            Defaults to 5 to stay within SEC rate limits.
        callback: Optional callback function that is called with each successfully
            fetched company facts dictionary. Not called for error responses.

    Returns:
        If a single CIK is provided, returns a dictionary with the company facts.
        If multiple CIKs are provided, returns a list of dictionaries.
        Error responses include 'error' and 'cik' keys.

    Example:
        >>> result = stream_company_facts(cik="320193")  # Apple
        >>> print(result.get("entityName"))
        'Apple Inc.'

        >>> # Fetch multiple companies
        >>> results = stream_company_facts(cik=["320193", "789019"])  # Apple, Microsoft
    """
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(
        stream_companyfacts(cik=cik, requests_per_second=requests_per_second, callback=callback)
    )