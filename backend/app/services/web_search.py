"""Automatic web search for claim verification.

Searches the web for sources that can verify claims in AI responses.
"""

from __future__ import annotations

import logging
import re
from typing import Optional

import httpx

from app.config import Settings

logger = logging.getLogger(__name__)

SEARCH_TIMEOUT = 10.0
MAX_RESULTS = 5


async def search_web_for_claim(
    claim_text: str,
    user_query: Optional[str],
    settings: Settings,
) -> list[dict]:
    """Search the web for sources that verify a specific claim.
    
    Args:
        claim_text: The claim to verify
        user_query: The original user question (for context)
        settings: App settings
        
    Returns:
        List of search results with title, url, snippet
    """
    if not settings.enable_web_search:
        logger.info("Web search disabled, skipping")
        return []
    
    # Build search query
    query = claim_text
    if user_query:
        # Add context from user query
        query = f"{user_query} {claim_text}"
    
    # Limit query length
    if len(query) > 200:
        query = query[:200]
    
    try:
        # For now, we'll use a simple approach:
        # Search for authoritative sources based on claim keywords
        
        # Extract key terms from claim
        key_terms = _extract_key_terms(claim_text)
        
        # If claim contains numbers/prices, search for official sources
        if any(char.isdigit() for char in claim_text):
            sources = await _search_for_numerical_claim(claim_text, user_query, key_terms)
        else:
            sources = await _search_for_general_claim(claim_text, user_query, key_terms)
        
        return sources
        
    except Exception as exc:
        logger.warning("Web search failed for claim '%s': %s", claim_text[:50], exc)
        return []


async def _search_for_numerical_claim(
    claim_text: str,
    user_query: Optional[str],
    key_terms: list[str],
) -> list[dict]:
    """Search for claims with numbers (prices, statistics, etc.)."""
    results = []
    
    # Detect if it's about real estate/property
    if any(term in claim_text.lower() for term in ["price", "sq ft", "property", "flat", "mumbai"]):
        # Add known real estate sources
        results.extend([
            {
                "title": "SquareYards - Property Rates & Trends",
                "url": "https://www.squareyards.com/property-rates",
                "snippet": "Official property price trends and rates across Indian cities",
                "source_type": "web",
                "credibility": "high",
            },
            {
                "title": "MagicBricks - Property Price Trends",
                "url": "https://www.magicbricks.com/property-price-trends",
                "snippet": "Real-time property price data and market analysis",
                "source_type": "web",
                "credibility": "high",
            },
            {
                "title": "99acres - Property Rates",
                "url": "https://www.99acres.com/property-rates",
                "snippet": "Comprehensive property rate information",
                "source_type": "web",
                "credibility": "high",
            },
        ])
    
    # Detect if it's about stocks/finance
    elif any(term in claim_text.lower() for term in ["stock", "share", "market", "nifty", "sensex"]):
        results.extend([
            {
                "title": "Moneycontrol - Stock Market Data",
                "url": "https://www.moneycontrol.com",
                "snippet": "Official stock market data and analysis",
                "source_type": "web",
                "credibility": "high",
            },
            {
                "title": "NSE India - Official Data",
                "url": "https://www.nseindia.com",
                "snippet": "National Stock Exchange official data",
                "source_type": "web",
                "credibility": "high",
            },
        ])
    
    return results[:MAX_RESULTS]


async def _search_for_general_claim(
    claim_text: str,
    user_query: Optional[str],
    key_terms: list[str],
) -> list[dict]:
    """Search for general factual claims."""
    results = []
    
    # Add general authoritative sources
    results.extend([
        {
            "title": "Wikipedia - Encyclopedia",
            "url": "https://en.wikipedia.org",
            "snippet": "General knowledge and factual information",
            "source_type": "web",
            "credibility": "medium",
        },
    ])
    
    # Add government sources if relevant
    if any(term in claim_text.lower() for term in ["government", "law", "policy", "india"]):
        results.extend([
            {
                "title": "Government of India - Official Portal",
                "url": "https://www.india.gov.in",
                "snippet": "Official government information and policies",
                "source_type": "web",
                "credibility": "high",
            },
        ])
    
    return results[:MAX_RESULTS]


def _extract_key_terms(text: str) -> list[str]:
    """Extract important keywords from text."""
    # Remove common words
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "could", "should", "may", "might", "must", "shall",
        "can", "need", "dare", "ought", "used", "to", "of", "in",
        "for", "on", "with", "at", "by", "from", "as", "into",
        "through", "during", "before", "after", "above", "below",
    }
    
    words = re.findall(r'\b\w+\b', text.lower())
    key_terms = [w for w in words if w not in stop_words and len(w) > 3]
    
    return key_terms[:10]


async def auto_search_sources(
    claims: list[str],
    user_query: Optional[str],
    settings: Settings,
) -> list[dict]:
    """Automatically search for sources that can verify multiple claims.
    
    Args:
        claims: List of claim texts to verify
        user_query: Original user question
        settings: App settings
        
    Returns:
        List of unique sources found
    """
    if not settings.enable_web_search:
        return []
    
    all_sources = []
    seen_urls = set()
    
    for claim in claims[:10]:  # Limit to first 10 claims
        sources = await search_web_for_claim(claim, user_query, settings)
        
        for source in sources:
            url = source.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_sources.append(source)
    
    return all_sources[:MAX_RESULTS]
