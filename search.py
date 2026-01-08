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
        Returns a dictionary with term, definition, example, category, polish, and pronunciation.
        """
        search_type = self.search_config.get('type', 'mock')
        
        if search_type == 'mock':
            return self._mock_search()
        else:
            return self._api_search()
    
    def _mock_search(self):
        """
        Mock search that returns random British slang from a predefined list.
        Includes Polish translations and pronunciation guides.
        """
        slang_database = [
            {
                'term': 'brilliant',
                'definition': 'Excellent, wonderful, or great',
                'example': 'That\'s absolutely brilliant!',
                'category': 'praise',
                'polish': 'Wspaniały, świetny, doskonały',
                'pronunciation': 'BRIL-yənt'
            },
            {
                'term': 'chuffed',
                'definition': 'Very pleased or happy',
                'example': 'I\'m dead chuffed with my new car!',
                'category': 'emotion',
                'polish': 'Bardzo zadowolony, uszczęśliwiony',
                'pronunciation': 'CHUFED'
            },
            {
                'term': 'gutted',
                'definition': 'Extremely disappointed or upset',
                'example': 'I was gutted when they cancelled the concert.',
                'category': 'emotion',
                'polish': 'Bardzo rozczarowany, zdruzgotany',
                'pronunciation': 'GUT-id'
            },
            {
                'term': 'knackered',
                'definition': 'Very tired or exhausted',
                'example': 'I\'m absolutely knackered after that workout.',
                'category': 'state',
                'polish': 'Wykończony, zmęczony, wycieńczony',
                'pronunciation': 'NAK-əd'
            },
            {
                'term': 'peckish',
                'definition': 'Slightly hungry',
                'example': 'I\'m feeling a bit peckish, fancy a snack?',
                'category': 'state',
                'polish': 'Lekko głodny, mający ochotę na przekąskę',
                'pronunciation': 'PEK-ish'
            },
            {
                'term': 'cheeky',
                'definition': 'Playfully rude or impudent',
                'example': 'Don\'t be so cheeky!',
                'category': 'behavior',
                'polish': 'Bezczelny (w zabawny sposób), zuchwały',
                'pronunciation': 'CHEE-kee'
            },
            {
                'term': 'dodgy',
                'definition': 'Suspicious, unreliable, or of poor quality',
                'example': 'That pub looks a bit dodgy.',
                'category': 'description',
                'polish': 'Podejrzany, wątpliwy, kiepski',
                'pronunciation': 'DOJ-ee'
            },
            {
                'term': 'fancy',
                'definition': 'To want or desire something; to like someone romantically',
                'example': 'Do you fancy a cuppa?',
                'category': 'desire',
                'polish': 'Mieć ochotę na coś, podobać się',
                'pronunciation': 'FAN-see'
            },
            {
                'term': 'kip',
                'definition': 'Sleep or a nap',
                'example': 'I need to have a kip.',
                'category': 'action',
                'polish': 'Drzemka, sen, przespać się',
                'pronunciation': 'KIP'
            },
            {
                'term': 'mate',
                'definition': 'Friend or buddy',
                'example': 'Alright, mate?',
                'category': 'greeting',
                'polish': 'Kumpel, kolega, ziomek',
                'pronunciation': 'MATE'
            },
            {
                'term': 'quid',
                'definition': 'British pound (£1)',
                'example': 'That costs twenty quid.',
                'category': 'money',
                'polish': 'Funt brytyjski (potocznie)',
                'pronunciation': 'KWID'
            },
            {
                'term': 'bloke',
                'definition': 'A man or guy',
                'example': 'He\'s a decent bloke.',
                'category': 'person',
                'polish': 'Facet, gość, koleś',
                'pronunciation': 'BLOKE'
            },
            {
                'term': 'cheers',
                'definition': 'Thank you or goodbye',
                'example': 'Cheers for the help!',
                'category': 'greeting',
                'polish': 'Dzięki, na zdrowie, do zobaczenia',
                'pronunciation': 'CHEERZ'
            },
            {
                'term': 'proper',
                'definition': 'Very or really; genuine',
                'example': 'That was proper good!',
                'category': 'intensifier',
                'polish': 'Naprawdę, bardzo, porządny',
                'pronunciation': 'PROP-ər'
            },
            {
                'term': 'mental',
                'definition': 'Crazy or insane',
                'example': 'The party was absolutely mental!',
                'category': 'description',
                'polish': 'Szalony, zwariowany, obłąkany',
                'pronunciation': 'MEN-təl'
            },
            {
                'term': 'brolly',
                'definition': 'Umbrella',
                'example': 'Better bring a brolly, it looks like rain.',
                'category': 'object',
                'polish': 'Parasol, parasolka',
                'pronunciation': 'BROL-ee'
            },
            {
                'term': 'bog',
                'definition': 'Toilet or bathroom',
                'example': 'Where\'s the bog?',
                'category': 'place',
                'polish': 'Kibel, toaleta (potocznie)',
                'pronunciation': 'BOG'
            },
            {
                'term': 'naff',
                'definition': 'Uncool, unfashionable, or of poor quality',
                'example': 'That shirt is a bit naff.',
                'category': 'description',
                'polish': 'Niemodny, kiepski, tandetny',
                'pronunciation': 'NAF'
            },
            {
                'term': 'gobsmacked',
                'definition': 'Utterly astonished or amazed',
                'example': 'I was absolutely gobsmacked!',
                'category': 'emotion',
                'polish': 'Zszokowany, oszołomiony, zdumiony',
                'pronunciation': 'GOB-smakt'
            },
            {
                'term': 'skint',
                'definition': 'Having no money; broke',
                'example': 'I\'m completely skint this month.',
                'category': 'state',
                'polish': 'Spłukany, bez grosza',
                'pronunciation': 'SKINT'
            },
            {
                'term': 'bog-standard',
                'definition': 'Ordinary, basic, nothing special',
                'example': 'It\'s just a bog-standard car.',
                'category': 'description',
                'polish': 'Zwyczajny, podstawowy, standardowy',
                'pronunciation': 'BOG-STAN-dərd'
            },
            {
                'term': 'botched',
                'definition': 'Done badly or clumsily',
                'example': 'They completely botched the repair.',
                'category': 'action',
                'polish': 'Spartaczony, zepsuty, źle wykonany',
                'pronunciation': 'BOTCHT'
            },
            {
                'term': 'chinwag',
                'definition': 'A chat or conversation',
                'example': 'Let\'s have a chinwag over tea.',
                'category': 'action',
                'polish': 'Pogawędka, pogaduszki',
                'pronunciation': 'CHIN-wag'
            },
            {
                'term': 'faff',
                'definition': 'To waste time on trivial things',
                'example': 'Stop faffing about and get ready!',
                'category': 'action',
                'polish': 'Marnować czas, obijać się',
                'pronunciation': 'FAF'
            },
            {
                'term': 'miffed',
                'definition': 'Slightly annoyed or offended',
                'example': 'She was a bit miffed about the comment.',
                'category': 'emotion',
                'polish': 'Urażony, lekko zdenerwowany',
                'pronunciation': 'MIFT'
            },
            {
                'term': 'cuppa',
                'definition': 'A cup of tea',
                'example': 'Fancy a cuppa?',
                'category': 'food',
                'polish': 'Filiżanka herbaty',
                'pronunciation': 'KUP-ə'
            },
            {
                'term': 'barmy',
                'definition': 'Crazy, foolish',
                'example': 'You must be barmy!',
                'category': 'description',
                'polish': 'Zwariowany, stuknięty',
                'pronunciation': 'BAR-mee'
            },
            {
                'term': 'codswallop',
                'definition': 'Nonsense, rubbish',
                'example': 'That\'s complete codswallop!',
                'category': 'description',
                'polish': 'Bzdury, bujda, nonsens',
                'pronunciation': 'KODZ-wol-əp'
            },
            {
                'term': 'daft',
                'definition': 'Silly, stupid',
                'example': 'Don\'t be daft!',
                'category': 'description',
                'polish': 'Głupi, niemądry, durny',
                'pronunciation': 'DAFT'
            },
            {
                'term': 'jammy',
                'definition': 'Lucky',
                'example': 'You jammy git!',
                'category': 'description',
                'polish': 'Szczęściarz, mający fart',
                'pronunciation': 'JAM-ee'
            },
            {
                'term': 'nosh',
                'definition': 'Food',
                'example': 'Let\'s grab some nosh.',
                'category': 'food',
                'polish': 'Żarcie, jedzenie',
                'pronunciation': 'NOSH'
            },
            {
                'term': 'scrummy',
                'definition': 'Delicious',
                'example': 'That cake was scrummy!',
                'category': 'food',
                'polish': 'Pyszny, smaczny',
                'pronunciation': 'SKRUM-ee'
            },
            {
                'term': 'knickers',
                'definition': 'Women\'s underwear',
                'example': 'Don\'t get your knickers in a twist!',
                'category': 'clothing',
                'polish': 'Majtki damskie',
                'pronunciation': 'NIK-ərz'
            },
            {
                'term': 'trollied',
                'definition': 'Very drunk',
                'example': 'He was completely trollied!',
                'category': 'state',
                'polish': 'Zalany, pijany w trupa',
                'pronunciation': 'TROL-eed'
            },
            {
                'term': 'wazzock',
                'definition': 'A stupid or annoying person',
                'example': 'You absolute wazzock!',
                'category': 'insult',
                'polish': 'Idiota, dureń, pajac',
                'pronunciation': 'WAZ-ək'
            },
            {
                'term': 'wonky',
                'definition': 'Unsteady, not straight',
                'example': 'That table is a bit wonky.',
                'category': 'description',
                'polish': 'Krzywy, chwiejny, nierówny',
                'pronunciation': 'WON-kee'
            }
        ]
        
        # Select a random term
        selected = random.choice(slang_database)
        
        return {
            'term': selected['term'],
            'definition': selected['definition'],
            'example': selected['example'],
            'category': selected['category'],
            'polish': selected['polish'],
            'pronunciation': selected['pronunciation'],
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
        print(f"   Polish: {result['polish']}")
        print(f"   Pronunciation: {result['pronunciation']}")
        print(f"   Example: {result['example']}")
        print(f"   Category: {result['category']}")
        print()
