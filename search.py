#!/usr/bin/env python3
"""
Search module for British Days application.
Handles internet searches for British slang terms.
"""
import random
import json
import requests
from datetime import datetime


class SlangSearcher:
    """Searches for British slang terms from various sources."""
    
    def __init__(self, config_path='config.json'):
        """Initialize the searcher."""
        self.config = self._load_config(config_path)
        self.search_config = self.config.get('search_api', {})
    
    def _load_config(self, config_path):
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'search_api': {
                    'type': 'mock',
                    'fallback_terms': ['mate', 'brilliant', 'chuffed']
                }
            }
    
    def search_new_slang(self):
        """
        Search for a new British slang term.
        Returns a dictionary with term, definition, example, and category.
        """
        search_type = self.search_config.get('type', 'mock')
        
        if search_type == 'mock':
            return self._mock_search()
        else:
            return self._api_search()
    
    def _mock_search(self):
        """
        Mock search that returns random British slang from a predefined list.
        Used when no API is configured or as a fallback.
        """
        slang_database = [
            {
                'term': 'brilliant',
                'definition': 'Excellent, wonderful, or great',
                'example': 'That\'s absolutely brilliant!',
                'category': 'praise'
            },
            {
                'term': 'chuffed',
                'definition': 'Very pleased or happy',
                'example': 'I\'m dead chuffed with my new car!',
                'category': 'emotion'
            },
            {
                'term': 'gutted',
                'definition': 'Extremely disappointed or upset',
                'example': 'I was gutted when they cancelled the concert.',
                'category': 'emotion'
            },
            {
                'term': 'knackered',
                'definition': 'Very tired or exhausted',
                'example': 'I\'m absolutely knackered after that workout.',
                'category': 'state'
            },
            {
                'term': 'peckish',
                'definition': 'Slightly hungry',
                'example': 'I\'m feeling a bit peckish, fancy a snack?',
                'category': 'state'
            },
            {
                'term': 'cheeky',
                'definition': 'Playfully rude or impudent',
                'example': 'Don\'t be so cheeky!',
                'category': 'behavior'
            },
            {
                'term': 'dodgy',
                'definition': 'Suspicious, unreliable, or of poor quality',
                'example': 'That pub looks a bit dodgy.',
                'category': 'description'
            },
            {
                'term': 'fancy',
                'definition': 'To want or desire something; to like someone romantically',
                'example': 'Do you fancy a cuppa?',
                'category': 'desire'
            },
            {
                'term': 'kip',
                'definition': 'Sleep or a nap',
                'example': 'I need to have a kip.',
                'category': 'action'
            },
            {
                'term': 'mate',
                'definition': 'Friend or buddy',
                'example': 'Alright, mate?',
                'category': 'greeting'
            },
            {
                'term': 'quid',
                'definition': 'British pound (£1)',
                'example': 'That costs twenty quid.',
                'category': 'money'
            },
            {
                'term': 'bloke',
                'definition': 'A man or guy',
                'example': 'He\'s a decent bloke.',
                'category': 'person'
            },
            {
                'term': 'cheers',
                'definition': 'Thank you or goodbye',
                'example': 'Cheers for the help!',
                'category': 'greeting'
            },
            {
                'term': 'proper',
                'definition': 'Very or really; genuine',
                'example': 'That was proper good!',
                'category': 'intensifier'
            },
            {
                'term': 'mental',
                'definition': 'Crazy or insane',
                'example': 'The party was absolutely mental!',
                'category': 'description'
            },
            {
                'term': 'brolly',
                'definition': 'Umbrella',
                'example': 'Better bring a brolly, it looks like rain.',
                'category': 'object'
            },
            {
                'term': 'bog',
                'definition': 'Toilet or bathroom',
                'example': 'Where\'s the bog?',
                'category': 'place'
            },
            {
                'term': 'naff',
                'definition': 'Uncool, unfashionable, or of poor quality',
                'example': 'That shirt is a bit naff.',
                'category': 'description'
            },
            {
                'term': 'gobsmacked',
                'definition': 'Utterly astonished or amazed',
                'example': 'I was absolutely gobsmacked!',
                'category': 'emotion'
            },
            {
                'term': 'skint',
                'definition': 'Having no money; broke',
                'example': 'I\'m completely skint this month.',
                'category': 'state'
            },
            {
                'term': 'bog-standard',
                'definition': 'Ordinary, basic, nothing special',
                'example': 'It\'s just a bog-standard car.',
                'category': 'description'
            },
            {
                'term': 'botched',
                'definition': 'Done badly or clumsily',
                'example': 'They completely botched the repair.',
                'category': 'action'
            },
            {
                'term': 'chinwag',
                'definition': 'A chat or conversation',
                'example': 'Let\'s have a chinwag over tea.',
                'category': 'action'
            },
            {
                'term': 'faff',
                'definition': 'To waste time on trivial things',
                'example': 'Stop faffing about and get ready!',
                'category': 'action'
            },
            {
                'term': 'miffed',
                'definition': 'Slightly annoyed or offended',
                'example': 'She was a bit miffed about the comment.',
                'category': 'emotion'
            }
        ]
        
        # Select a random term
        selected = random.choice(slang_database)
        
        return {
            'term': selected['term'],
            'definition': selected['definition'],
            'example': selected['example'],
            'category': selected['category'],
            'source': 'mock_database',
            'search_date': datetime.now().isoformat()
        }
    
    def _api_search(self):
        """
        Search using an API (placeholder for future implementation).
        Falls back to mock search if API fails.
        """
        try:
            # Placeholder for API integration
            # This could be integrated with Urban Dictionary API, 
            # British Slang API, or similar services
            
            # For now, fallback to mock
            return self._mock_search()
        except Exception as e:
            print(f"API search failed: {e}")
            return self._mock_search()


# For standalone testing
if __name__ == '__main__':
    searcher = SlangSearcher()
    
    print("Searching for British slang...\n")
    
    for i in range(5):
        result = searcher.search_new_slang()
        print(f"{i+1}. {result['term'].upper()}")
        print(f"   Definition: {result['definition']}")
        print(f"   Example: {result['example']}")
        print(f"   Category: {result['category']}")
        print()
