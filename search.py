#!/usr/bin/env python3
"""
Search module for British Days application.
Handles internet searches for British slang terms from multiple sources.
"""
import random
import json
import requests
from datetime import datetime
import re
import time


class SlangSearcher:
    """Searches for British slang terms from various sources."""
    
    def __init__(self, config_path='config.json', db_manager=None):
        """Initialize the searcher."""
        self.config = self._load_config(config_path)
        self.search_config = self.config.get('search_api', {})
        self.db = db_manager
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BritishDaysBot/1.0 (Educational Language Learning App)'
        })
        
        # British slang categories for Wikipedia
        self.british_slang_categories = [
            'British slang',
            'Cockney rhyming slang',
            'British English',
            'English slang',
            'British colloquialisms'
        ]
        
        # Track current search state
        self.current_source_index = 0
        self.wikipedia_search_offset = 0
        self.wiktionary_letter_index = 0
    
    def _load_config(self, config_path):
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'search_api': {
                    'type': 'api',
                    'sources': ['wikipedia', 'wiktionary', 'mock'],
                    'fallback_terms': ['mate', 'brilliant', 'chuffed']
                }
            }
    
    def search_new_slang(self):
        """
        Search for a new British slang term.
        Returns a dictionary with term, definition, example, category, polish, and pronunciation.
        """
        search_type = self.search_config.get('type', 'mock')
        sources = self.search_config.get('sources', ['mock'])
        
        if search_type == 'mock':
            return self._mock_search()
        
        # Try each source in rotation
        for _ in range(len(sources) * 2):  # Try each source at least twice
            source = sources[self.current_source_index % len(sources)]
            self.current_source_index += 1
            
            try:
                if source == 'wikipedia':
                    result = self._search_wikipedia()
                elif source == 'wiktionary':
                    result = self._search_wiktionary()
                else:
                    result = self._mock_search()
                
                if result:
                    return result
            except Exception as e:
                print(f"Error searching {source}: {e}")
                continue
        
        # Fallback to mock if all APIs fail
        return self._mock_search()
    
    def _search_wikipedia(self):
        """Search Wikipedia for British slang terms."""
        endpoint = self.search_config.get('wikipedia_endpoint', 'https://en.wikipedia.org/w/api.php')
        
        # Search for articles in British slang categories
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'categorymembers',
            'cmtitle': 'Category:British slang',
            'cmlimit': 50,
            'cmtype': 'page',
            'cmcontinue': self.wikipedia_search_offset
        }
        
        try:
            timeout = self.search_config.get('timeout', 10)
            response = self.session.get(endpoint, params=params, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            
            members = data.get('query', {}).get('categorymembers', [])
            
            if not members:
                # Reset offset and try again
                self.wikipedia_search_offset = 0
                params['cmcontinue'] = 0
                response = self.session.get(endpoint, params=params, timeout=timeout)
                data = response.json()
                members = data.get('query', {}).get('categorymembers', [])
            
            if members:
                # Get a random article from the results
                article = random.choice(members)
                page_title = article['title']
                
                # Check if already searched this page
                if self.db and self.db.is_location_searched('wikipedia', page_title):
                    # Try next one
                    self.wikipedia_search_offset += 1
                    return None
                
                # Get article content
                content_params = {
                    'action': 'query',
                    'format': 'json',
                    'titles': page_title,
                    'prop': 'extracts|categories',
                    'exintro': True,
                    'explaintext': True
                }
                
                content_response = self.session.get(endpoint, params=content_params, timeout=timeout)
                content_data = content_response.json()
                
                pages = content_data.get('query', {}).get('pages', {})
                if pages:
                    page_id = list(pages.keys())[0]
                    page_content = pages[page_id]
                    
                    term = page_title
                    extract = page_content.get('extract', '')
                    
                    # Parse the extract to get definition and example
                    definition, example = self._parse_wikipedia_extract(extract)
                    
                    if definition:
                        # Mark location as searched
                        if self.db:
                            self.db.mark_location_searched('wikipedia', page_title, 1)
                        
                        result = {
                            'term': term,
                            'definition': definition,
                            'example': example,
                            'category': 'slang',
                            'polish': '',  # Would need translation API
                            'pronunciation': '',
                            'source': 'wikipedia',
                            'source_url': f'https://en.wikipedia.org/wiki/{page_title.replace(" ", "_")}',
                            'search_date': datetime.now().isoformat()
                        }
                        
                        # Cache the result - explicitly pass expected parameters
                        if self.db:
                            self.db.add_to_cache(
                                term=result['term'],
                                definition=result['definition'],
                                example=result['example'],
                                category=result['category'],
                                polish=result['polish'],
                                pronunciation=result['pronunciation'],
                                source_type=result['source'],
                                source_url=result['source_url']
                            )
                        
                        return result
                
                self.wikipedia_search_offset += 1
                
        except Exception as e:
            print(f"Wikipedia search error: {e}")
        
        return None
    
    def _parse_wikipedia_extract(self, extract):
        """Parse Wikipedia extract to get definition and example."""
        if not extract:
            return None, None
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', extract)
        
        if len(sentences) < 1:
            return None, None
        
        # First sentence is usually the definition
        definition = sentences[0].strip()
        
        # Try to find an example in the text
        example = ''
        for sentence in sentences[1:]:
            if any(keyword in sentence.lower() for keyword in ['example', 'used', 'saying', 'means']):
                example = sentence.strip()
                break
        
        # Limit lengths
        if len(definition) > 500:
            definition = definition[:497] + '...'
        
        return definition, example
    
    def _search_wiktionary(self):
        """Search Wiktionary for British slang terms."""
        endpoint = self.search_config.get('wiktionary_endpoint', 'https://en.wiktionary.org/w/api.php')
        
        # Common British slang starting letters
        letters = ['b', 'c', 'd', 'g', 'k', 'm', 'p', 's', 'w']
        letter = letters[self.wiktionary_letter_index % len(letters)]
        
        # Search for British English terms
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srsearch': f'{letter} incategory:"British English"',
            'srlimit': 20,
            'srnamespace': 0
        }
        
        try:
            timeout = self.search_config.get('timeout', 10)
            response = self.session.get(endpoint, params=params, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            
            search_results = data.get('query', {}).get('search', [])
            
            if search_results:
                # Pick a random result
                result_item = random.choice(search_results)
                term = result_item['title']
                
                # Check if already searched
                if self.db and self.db.is_location_searched('wiktionary', term):
                    self.wiktionary_letter_index += 1
                    return None
                
                # Get the full page content
                parse_params = {
                    'action': 'parse',
                    'format': 'json',
                    'page': term,
                    'prop': 'text',
                    'section': 0
                }
                
                parse_response = self.session.get(endpoint, params=parse_params, timeout=timeout)
                parse_data = parse_response.json()
                
                html_content = parse_data.get('parse', {}).get('text', {}).get('*', '')
                
                # Extract definition from HTML (simplified)
                definition, example = self._parse_wiktionary_html(html_content)
                
                if definition:
                    # Mark as searched
                    if self.db:
                        self.db.mark_location_searched('wiktionary', term, 1)
                    
                    result = {
                        'term': term,
                        'definition': definition,
                        'example': example,
                        'category': 'slang',
                        'polish': '',
                        'pronunciation': '',
                        'source': 'wiktionary',
                        'source_url': f'https://en.wiktionary.org/wiki/{term}',
                        'search_date': datetime.now().isoformat()
                    }
                    
                    # Cache the result - explicitly pass expected parameters
                    if self.db:
                        self.db.add_to_cache(
                            term=result['term'],
                            definition=result['definition'],
                            example=result['example'],
                            category=result['category'],
                            polish=result['polish'],
                            pronunciation=result['pronunciation'],
                            source_type=result['source'],
                            source_url=result['source_url']
                        )
                    
                    return result
            
            self.wiktionary_letter_index += 1
            
        except Exception as e:
            print(f"Wiktionary search error: {e}")
        
        return None
    
    def _parse_wiktionary_html(self, html):
        """Parse Wiktionary HTML to extract definition and example."""
        # This is a simplified parser - a real implementation would use BeautifulSoup
        if not html:
            return None, None
        
        # Remove HTML tags (simple approach)
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Look for definition pattern
        sentences = re.split(r'[.!?]+', text)
        
        definition = None
        example = None
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < 300 and not definition:
                definition = sentence
            elif any(marker in sentence.lower() for marker in ['example', 'quot', '"', "'"]) and not example:
                example = sentence[:200]
        
        return definition, example
    
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


# For standalone testing
if __name__ == '__main__':
    searcher = SlangSearcher()
    
    print("Searching for British slang...\n")
    
    for i in range(5):
        result = searcher.search_new_slang()
        print(f"{i+1}. {result['term'].upper()}")
        print(f"   Definition: {result['definition']}")
        print(f"   Polish: {result.get('polish', 'N/A')}")
        print(f"   Pronunciation: {result.get('pronunciation', 'N/A')}")
        print(f"   Example: {result.get('example', 'N/A')}")
        print(f"   Category: {result['category']}")
        print(f"   Source: {result.get('source', 'unknown')}")
        print()
