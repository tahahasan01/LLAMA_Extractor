from typing import Any, Dict, List
import re


def normalize_string(text: str) -> str:
    """
    Normalize a string for comparison
    
    Args:
        text: Input text
    
    Returns:
        Normalized text
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters
    text = re.sub(r'[^a-z0-9\s]', '', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text


def extract_year_from_date(date_string: str) -> int:
    """
    Extract year from date string
    
    Args:
        date_string: Date string (e.g., "2020-01-15")
    
    Returns:
        Year as integer or None
    """
    if not date_string or len(date_string) < 4:
        return None
    
    try:
        return int(date_string[:4])
    except (ValueError, TypeError):
        return None


def truncate_text(text: str, max_length: int = 200) -> str:
    """
    Truncate text to max length
    
    Args:
        text: Input text
        max_length: Maximum length
    
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."


def format_runtime(minutes: int) -> str:
    """
    Format runtime in minutes to human-readable string
    
    Args:
        minutes: Runtime in minutes
    
    Returns:
        Formatted string (e.g., "2h 15m")
    """
    if not minutes or minutes <= 0:
        return "Unknown"
    
    hours = minutes // 60
    mins = minutes % 60
    
    if hours > 0:
        if mins > 0:
            return f"{hours}h {mins}m"
        return f"{hours}h"
    
    return f"{mins}m"


def validate_rating(rating: float) -> bool:
    """
    Validate rating value
    
    Args:
        rating: Rating value
    
    Returns:
        True if valid, False otherwise
    """
    try:
        rating = float(rating)
        return 1.0 <= rating <= 5.0
    except (ValueError, TypeError):
        return False


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division fails
    
    Returns:
        Result of division or default
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (ValueError, TypeError, ZeroDivisionError):
        return default


def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """
    Merge two dictionaries (dict2 overrides dict1)
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary
    
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    result.update(dict2)
    return result


def deduplicate_list(items: List[Any], key: str = None) -> List[Any]:
    """
    Remove duplicates from list
    
    Args:
        items: List of items
        key: Key to use for deduplication (for dicts/objects)
    
    Returns:
        List with duplicates removed
    """
    if not items:
        return []
    
    if key and isinstance(items[0], dict):
        # Deduplicate based on key in dictionary
        seen = set()
        result = []
        for item in items:
            if item.get(key) not in seen:
                seen.add(item.get(key))
                result.append(item)
        return result
    
    # Simple deduplication
    return list(dict.fromkeys(items))


def calculate_similarity_score(text1: str, text2: str) -> float:
    """
    Calculate simple similarity score between two texts
    
    Args:
        text1: First text
        text2: Second text
    
    Returns:
        Similarity score (0-1)
    """
    if not text1 or not text2:
        return 0.0
    
    # Normalize texts
    norm1 = normalize_string(text1)
    norm2 = normalize_string(text2)
    
    # Split into words
    words1 = set(norm1.split())
    words2 = set(norm2.split())
    
    if not words1 or not words2:
        return 0.0
    
    # Calculate Jaccard similarity
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    return intersection / union if union > 0 else 0.0


def paginate(items: List[Any], page: int = 1, per_page: int = 10) -> Dict:
    """
    Paginate a list of items
    
    Args:
        items: List of items
        page: Page number (1-indexed)
        per_page: Items per page
    
    Returns:
        Dictionary with paginated data
    """
    total = len(items)
    total_pages = (total + per_page - 1) // per_page
    
    # Validate page number
    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages
    
    # Calculate slice indices
    start = (page - 1) * per_page
    end = start + per_page
    
    return {
        'items': items[start:end],
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages
    }


def format_movie_list(movies: List[Dict]) -> str:
    """
    Format movie list as readable text
    
    Args:
        movies: List of movie dictionaries
    
    Returns:
        Formatted text
    """
    if not movies:
        return "No movies found."
    
    lines = []
    for i, movie in enumerate(movies, 1):
        title = movie.get('title', 'Unknown')
        year = extract_year_from_date(movie.get('release_date', ''))
        rating = movie.get('vote_average', 0)
        
        line = f"{i}. {title}"
        if year:
            line += f" ({year})"
        if rating > 0:
            line += f" - ⭐ {rating:.1f}"
        
        lines.append(line)
    
    return '\n'.join(lines)


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract keywords from text (simple implementation)
    
    Args:
        text: Input text
        max_keywords: Maximum number of keywords
    
    Returns:
        List of keywords
    """
    if not text:
        return []
    
    # Normalize and split
    normalized = normalize_string(text)
    words = normalized.split()
    
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
        'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was',
        'are', 'were', 'be', 'been', 'being', 'have', 'has', 'had'
    }
    
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    
    # Get word frequency
    word_freq = {}
    for word in keywords:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency
    sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    
    return [word for word, _ in sorted_keywords[:max_keywords]]
