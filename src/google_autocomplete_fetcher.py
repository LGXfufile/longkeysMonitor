#!/usr/bin/env python3
"""
Google Autocomplete Suggestion Fetcher
Fetches Google autocomplete suggestions for "ai generate" + a-z
"""

import requests
import json
import time
import string
from urllib.parse import quote

def get_google_suggestions(query):
    """Fetch Google autocomplete suggestions for a query"""
    try:
        # Google autocomplete API endpoint
        url = f"http://suggestqueries.google.com/complete/search"
        params = {
            'client': 'firefox',
            'q': query,
            'hl': 'en'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            if len(data) > 1 and isinstance(data[1], list):
                return data[1]
        return []
    
    except Exception as e:
        print(f"Error fetching suggestions for '{query}': {e}")
        return []

def collect_all_suggestions():
    """Collect all suggestions for 'ai generate' + a-z"""
    base_query = "ai generate"
    all_suggestions = {}
    
    print(f"Fetching suggestions for base query: '{base_query}'")
    base_suggestions = get_google_suggestions(base_query)
    all_suggestions[base_query] = base_suggestions
    print(f"Found {len(base_suggestions)} suggestions for base query")
    
    # Iterate through a-z
    for letter in string.ascii_lowercase:
        query = f"{base_query} {letter}"
        print(f"Fetching suggestions for: '{query}'")
        
        suggestions = get_google_suggestions(query)
        all_suggestions[query] = suggestions
        
        print(f"Found {len(suggestions)} suggestions")
        for suggestion in suggestions[:5]:  # Show first 5
            print(f"  - {suggestion}")
        
        # Be respectful to Google's servers
        time.sleep(1)
    
    return all_suggestions

def save_results(suggestions, filename="google_autocomplete_results.json"):
    """Save results to a JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(suggestions, f, indent=2, ensure_ascii=False)
    print(f"Results saved to {filename}")

def display_summary(suggestions):
    """Display a summary of all collected suggestions"""
    print("\n" + "="*60)
    print("SUMMARY OF ALL COLLECTED SUGGESTIONS")
    print("="*60)
    
    total_suggestions = 0
    unique_suggestions = set()
    
    for query, suggestion_list in suggestions.items():
        print(f"\n{query}: ({len(suggestion_list)} suggestions)")
        for suggestion in suggestion_list:
            print(f"  - {suggestion}")
            unique_suggestions.add(suggestion)
        total_suggestions += len(suggestion_list)
    
    print(f"\nTotal queries processed: {len(suggestions)}")
    print(f"Total suggestions found: {total_suggestions}")
    print(f"Unique suggestions: {len(unique_suggestions)}")

if __name__ == "__main__":
    print("Google Autocomplete Suggestion Fetcher")
    print("Collecting suggestions for 'ai generate' + a-z...")
    print("-" * 50)
    
    # Collect all suggestions
    all_suggestions = collect_all_suggestions()
    
    # Save results
    save_results(all_suggestions)
    
    # Display summary
    display_summary(all_suggestions)
    
    print(f"\nDone! Check 'google_autocomplete_results.json' for complete results.")