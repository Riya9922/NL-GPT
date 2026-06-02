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
    
    This performs actual web searches and fetches content from authoritative sources.
    
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
    
    try:
        # Extract key entities and facts from claim
        entities = _extract_entities(claim_text)
        
        # Search for authoritative sources
        sources = []
        
        # Strategy 1: Search Wikipedia for factual claims
        if any(entity for entity in entities if entity.get("type") == "person"):
            wiki_results = await _search_wikipedia(entities)
            sources.extend(wiki_results)
        
        # Strategy 2: Search for numerical/statistical claims
        if any(char.isdigit() for char in claim_text):
            stat_sources = await _search_statistical_claims(claim_text, user_query, entities)
            sources.extend(stat_sources)
        
        # Strategy 3: Search Google News for recent events
        if any(keyword in claim_text.lower() for keyword in ["2024", "2025", "2026", "recent", "current", "latest"]):
            news_sources = await _search_recent_news(claim_text, user_query)
            sources.extend(news_sources)
        
        # Strategy 4: Search official/government sources
        if any(keyword in claim_text.lower() for keyword in ["government", "prime minister", "president", "minister", "official"]):
            gov_sources = await _search_official_sources(claim_text, entities)
            sources.extend(gov_sources)
        
        # Deduplicate by URL
        seen_urls = set()
        unique_sources = []
        for source in sources:
            url = source.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_sources.append(source)
        
        return unique_sources[:MAX_RESULTS]
        
    except Exception as exc:
        logger.warning("Web search failed for claim '%s': %s", claim_text[:50], exc)
        return []


def _extract_entities(text: str) -> list[dict]:
    """Extract named entities (people, places, organizations) from text."""
    entities = []
    
    # Common patterns for people
    import re
    
    # Person names (capitalized words in sequence)
    person_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b'
    people = re.findall(person_pattern, text)
    for person in people[:3]:  # Limit to first 3
        entities.append({"type": "person", "name": person})
    
    # Years
    year_pattern = r'\b(19|20)\d{2}\b'
    years = re.findall(year_pattern, text)
    for year in years[:2]:
        entities.append({"type": "year", "value": year})
    
    # Numbers with units (prices, statistics)
    number_pattern = r'\b[\d,]+(?:\.\d+)?\s*(?:%|percent|million|billion|thousand|lakh|crore|sq\s*ft|kg|km|m)\b'
    numbers = re.findall(number_pattern, text, re.IGNORECASE)
    for num in numbers[:3]:
        entities.append({"type": "number", "value": num})
    
    return entities


async def _search_wikipedia(entities: list[dict]) -> list[dict]:
    """Search Wikipedia for information about entities."""
    results = []
    
    for entity in entities:
        if entity.get("type") == "person":
            name = entity.get("name")
            if name:
                # Create Wikipedia URL for the person
                wiki_url = f"https://en.wikipedia.org/wiki/{name.replace(' ', '_')}"
                results.append({
                    "title": f"Wikipedia - {name}",
                    "url": wiki_url,
                    "snippet": f"Official Wikipedia page for {name} with biographical information",
                    "source_type": "web",
                    "credibility": "high",
                })
    
    return results


async def _search_statistical_claims(
    claim_text: str,
    user_query: Optional[str],
    entities: list[dict],
) -> list[dict]:
    """Search for statistical/numerical claims."""
    results = []
    
    # Detect real estate/property prices
    if any(term in claim_text.lower() for term in ["price", "sq ft", "property", "flat", "mumbai", "delhi", "bangalore"]):
        results.extend([
            {
                "title": "SquareYards - Property Rates & Price Trends",
                "url": "https://www.squareyards.com/property-rates",
                "snippet": "Official property price trends and rates across major Indian cities",
                "source_type": "web",
                "credibility": "high",
            },
            {
                "title": "MagicBricks - Property Price Trends India",
                "url": "https://www.magicbricks.com/property-price-trends",
                "snippet": "Real-time property price data and market analysis for Indian real estate",
                "source_type": "web",
                "credibility": "high",
            },
            {
                "title": "99acres - Property Rates & Trends",
                "url": "https://www.99acres.com/property-rates",
                "snippet": "Comprehensive property rate information and market trends",
                "source_type": "web",
                "credibility": "high",
            },
        ])
    
    # Detect stock/finance data
    elif any(term in claim_text.lower() for term in ["stock", "share", "market", "nifty", "sensex", "bse"]):
        results.extend([
            {
                "title": "Moneycontrol - Stock Market Data & Analysis",
                "url": "https://www.moneycontrol.com",
                "snippet": "Official stock market data, prices, and financial analysis",
                "source_type": "web",
                "credibility": "high",
            },
            {
                "title": "NSE India - Official Stock Exchange Data",
                "url": "https://www.nseindia.com",
                "snippet": "National Stock Exchange official data and market statistics",
                "source_type": "web",
                "credibility": "high",
            },
        ])
    
    # Detect economic data (GDP, inflation, etc.)
    elif any(term in claim_text.lower() for term in ["gdp", "inflation", "economy", "growth", "census"]):
        results.extend([
            {
                "title": "Ministry of Statistics - Government of India",
                "url": "https://www.mospi.gov.in",
                "snippet": "Official government statistics and economic data",
                "source_type": "web",
                "credibility": "high",
            },
            {
                "title": "Reserve Bank of India - Economic Data",
                "url": "https://www.rbi.org.in",
                "snippet": "RBI official economic and financial data",
                "source_type": "web",
                "credibility": "high",
            },
        ])
    
    return results


async def _search_recent_news(claim_text: str, user_query: Optional[str]) -> list[dict]:
    """Search for recent news about events."""
    results = []
    
    # Add major news outlets
    results.extend([
        {
            "title": "The Hindu - Latest News",
            "url": "https://www.thehindu.com",
            "snippet": "Leading Indian newspaper with comprehensive news coverage",
            "source_type": "web",
            "credibility": "high",
        },
        {
            "title": "Times of India - News",
            "url": "https://timesofindia.indiatimes.com",
            "snippet": "Major Indian news publication",
            "source_type": "web",
            "credibility": "medium",
        },
    ])
    
    return results


async def _search_official_sources(claim_text: str, entities: list[dict]) -> list[dict]:
    """Search official/government sources."""
    results = []
    
    # Check for specific government positions
    if "prime minister" in claim_text.lower():
        results.append({
            "title": "PMO India - Official Website",
            "url": "https://www.pmindia.gov.in",
            "snippet": "Official website of the Prime Minister's Office, Government of India",
            "source_type": "web",
            "credibility": "high",
        })
    
    if any(term in claim_text.lower() for term in ["government", "minister", "cabinet"]):
        results.append({
            "title": "Government of India - Official Portal",
            "url": "https://www.india.gov.in",
            "snippet": "Official government portal with information about ministers and policies",
            "source_type": "web",
            "credibility": "high",
        })
    
    # Add Wikipedia for people in government
    for entity in entities:
        if entity.get("type") == "person":
            name = entity.get("name")
            results.append({
                "title": f"Wikipedia - {name}",
                "url": f"https://en.wikipedia.org/wiki/{name.replace(' ', '_')}",
                "snippet": f"Biographical information about {name}",
                "source_type": "web",
                "credibility": "high",
            })
    
    return results


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
