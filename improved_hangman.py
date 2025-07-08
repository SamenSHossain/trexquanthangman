import json
import random
import string
import secrets
import time
import re
import collections
import pickle
import os
from collections import defaultdict, Counter
import math
from typing import Dict, List, Tuple, Set

try:
    import requests
    try:
        from requests.packages.urllib3.exceptions import InsecureRequestWarning
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    except (ImportError, AttributeError):
        pass
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Requests library not available. API calls will be simulated.")

try:
    from urllib.parse import parse_qs, urlencode, urlparse
except ImportError:
    try:
        from urlparse import parse_qs, urlparse  # type: ignore
        from urllib import urlencode  # type: ignore
    except ImportError:
        # Define fallbacks
        def parse_qs(s):  # type: ignore
            return {}
        def urlparse(s):  # type: ignore
            return s
        def urlencode(d):  # type: ignore
            return ""

class AdvancedHangmanAPI(object):
    def __init__(self, access_token=None, session=None, timeout=None):
        self.hangman_url = self.determine_hangman_url()
        self.access_token = access_token
        if REQUESTS_AVAILABLE:
            self.session = session or requests.Session()
        else:
            self.session = None
        self.timeout = timeout
        self.guessed_letters = []
        
        # Initialize dictionary and statistical data
        self.full_dictionary_location = "words_250000_train.txt"
        self.full_dictionary = self.build_dictionary(self.full_dictionary_location)
        
        # Initialize data structures for advanced algorithm
        self.initialize_statistical_data()
        self.current_dictionary = []
        
        # Algorithm state
        self.current_word_length = 0
        self.current_pattern = ""
        self.game_phase = "early"  # early, mid, late
        
    @staticmethod
    def determine_hangman_url():
        links = ['https://trexsim.com']
        data = {link: 0 for link in links}
        
        for link in links:
            try:
                if REQUESTS_AVAILABLE:
                    requests.get(link)
                    for i in range(10):
                        s = time.time()
                        requests.get(link)
                        data[link] = int((time.time() - s) * 1000)  # Convert to milliseconds as int
                else:
                    data[link] = 1000  # Default value when requests not available
            except:
                data[link] = 999999  # Large int instead of float('inf')
                
        link = sorted(data.items(), key=lambda x: x[1])[0][0]
        link += '/trexsim/hangman'
        return link
    
    def build_dictionary(self, dictionary_file_location):
        """Build dictionary from file, create sample if doesn't exist"""
        try:
            with open(dictionary_file_location, "r") as text_file:
                full_dictionary = text_file.read().splitlines()
        except FileNotFoundError:
            # Create a sample dictionary for testing
            print(f"Dictionary file {dictionary_file_location} not found. Creating sample dictionary...")
            full_dictionary = self.create_sample_dictionary()
            with open(dictionary_file_location, "w") as f:
                for word in full_dictionary:
                    f.write(word + "\n")
        return full_dictionary
    
    def create_sample_dictionary(self):
        """Create a representative sample dictionary for testing"""
        # This is a simplified sample - in practice you'd load the actual 250k words
        sample_words = [
            # 3-letter words
            "the", "and", "for", "are", "but", "not", "you", "all", "can", "had", "her", "was", "one", "our", "out", "day", "get", "has", "him", "his", "how", "man", "new", "now", "old", "see", "two", "way", "who", "boy", "did", "its", "let", "put", "say", "she", "too", "use",
            
            # 4-letter words  
            "that", "with", "have", "this", "will", "your", "from", "they", "know", "want", "been", "good", "much", "some", "time", "very", "when", "come", "here", "just", "like", "long", "make", "many", "over", "such", "take", "than", "them", "well", "were",
            
            # 5-letter words
            "which", "their", "would", "there", "could", "other", "after", "first", "never", "these", "think", "where", "being", "every", "great", "might", "shall", "still", "those", "under", "while", "sound", "water", "place", "right", "small", "world",
            
            # 6-letter words
            "should", "around", "before", "another", "because", "through", "between", "little", "number", "people", "school", "always", "looked", "called", "follow", "public", "really", "second", "social", "system", "things", "though", "turned", "wanted",
            
            # 7-letter words
            "without", "nothing", "someone", "something", "between", "thought", "through", "because", "different", "important", "example", "general", "history", "national", "picture", "problem", "service", "special", "support", "certain", "country",
            
            # 8+ letter words
            "question", "complete", "remember", "business", "possible", "including", "community", "education", "experience", "government", "information", "management", "particular", "political", "population", "significant", "technology", "development", "environment", "international"
        ]
        
        # Add more words to reach a reasonable sample size
        additional_words = []
        for base_word in sample_words[:50]:  # Take first 50 words
            # Add plurals
            if not base_word.endswith('s'):
                additional_words.append(base_word + 's')
            # Add -ing forms for appropriate words
            if len(base_word) > 3 and not base_word.endswith('ing'):
                if base_word.endswith('e'):
                    additional_words.append(base_word[:-1] + 'ing')
                else:
                    additional_words.append(base_word + 'ing')
            # Add -ed forms
            if len(base_word) > 3 and not base_word.endswith('ed'):
                if base_word.endswith('e'):
                    additional_words.append(base_word[:-1] + 'ed')
                else:
                    additional_words.append(base_word + 'ed')
        
        return sorted(list(set(sample_words + additional_words)))
    
    def initialize_statistical_data(self):
        """Initialize comprehensive statistical analysis as per strategy plan"""
        print("Initializing statistical data...")
        
        # Phase 1.1: Dictionary Analysis Foundation
        self.word_length_distribution = defaultdict(int)
        self.letter_frequency_by_length = defaultdict(lambda: defaultdict(int))
        self.position_frequency = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        self.conditional_frequency = defaultdict(lambda: defaultdict(int))
        
        # Phase 1.2: Pattern Recognition Analysis
        self.common_prefixes = defaultdict(int)
        self.common_suffixes = defaultdict(int)
        self.bigrams = defaultdict(int)
        self.trigrams = defaultdict(int)
        self.vowel_patterns = defaultdict(lambda: defaultdict(int))
        
        # Compute statistics
        self._compute_dictionary_statistics()
        
        # Phase 2.1: Multi-Algorithm Architecture
        self.optimal_first_letters = {}
        self._compute_optimal_first_letters()
        
        print("Statistical analysis complete.")
    
    def _compute_dictionary_statistics(self):
        """Compute comprehensive dictionary statistics"""
        for word in self.full_dictionary:
            word = word.lower()
            length = len(word)
            
            # Word length distribution
            self.word_length_distribution[length] += 1
            
            # Letter frequency by length
            for char in word:
                if char.isalpha():
                    self.letter_frequency_by_length[length][char] += 1
            
            # Position-specific frequency
            for pos, char in enumerate(word):
                if char.isalpha():
                    self.position_frequency[length][pos][char] += 1
                    # Also track relative positions (first, last, etc.)
                    if pos == 0:
                        self.position_frequency[length]['first'][char] += 1
                    if pos == length - 1:
                        self.position_frequency[length]['last'][char] += 1
                    if pos == 1 and length > 1:
                        self.position_frequency[length]['second'][char] += 1
                    if pos == length - 2 and length > 1:
                        self.position_frequency[length]['second_last'][char] += 1
            
            # Conditional frequency (letter co-occurrence)
            for i, char in enumerate(word):
                if char.isalpha():
                    for j, other_char in enumerate(word):
                        if i != j and other_char.isalpha():
                            self.conditional_frequency[char][other_char] += 1
            
            # Prefixes and suffixes
            for i in range(1, min(5, len(word))):
                self.common_prefixes[word[:i]] += 1
                self.common_suffixes[word[-i:]] += 1
            
            # Bigrams and trigrams
            for i in range(len(word) - 1):
                if word[i].isalpha() and word[i+1].isalpha():
                    self.bigrams[word[i:i+2]] += 1
            
            for i in range(len(word) - 2):
                if all(c.isalpha() for c in word[i:i+3]):
                    self.trigrams[word[i:i+3]] += 1
            
            # Vowel patterns
            vowels = set('aeiou')
            vowel_pattern = ''.join(['V' if c in vowels else 'C' for c in word if c.isalpha()])
            self.vowel_patterns[length][vowel_pattern] += 1
    
    def _compute_optimal_first_letters(self):
        """Compute optimal first letters for each word length"""
        for length in self.word_length_distribution:
            letter_scores = {}
            total_words = self.word_length_distribution[length]
            
            for letter in string.ascii_lowercase:
                # Calculate percentage of words containing this letter
                words_with_letter = 0
                for word in self.full_dictionary:
                    if len(word) == length and letter in word.lower():
                        words_with_letter += 1
                
                if total_words > 0:
                    letter_scores[letter] = words_with_letter / total_words
                else:
                    letter_scores[letter] = 0
            
            # Sort by score and store
            sorted_letters = sorted(letter_scores.items(), key=lambda x: x[1], reverse=True)
            self.optimal_first_letters[length] = [letter for letter, score in sorted_letters]
    
    def guess(self, word):
        """Main guess function implementing multi-algorithm architecture"""
        # Clean the word pattern
        clean_word = word[::2].replace("_", ".")
        self.current_word_length = len(clean_word)
        self.current_pattern = clean_word
        
        # Determine game phase
        num_guessed = len(self.guessed_letters)
        revealed_letters = sum(1 for c in clean_word if c != '.')
        
        if num_guessed <= 2:
            self.game_phase = "early"
        elif num_guessed <= 5 or revealed_letters < self.current_word_length * 0.4:
            self.game_phase = "mid"
        else:
            self.game_phase = "late"
        
        # Filter dictionary based on current constraints
        self._update_candidate_dictionary(clean_word)
        
        # Choose algorithm based on game phase and candidate count
        if self.game_phase == "early" and num_guessed == 0:
            return self._algorithm_1_length_based_frequency(clean_word)
        elif len(self.current_dictionary) <= 10:
            return self._algorithm_3_direct_pattern_matching(clean_word)
        else:
            return self._algorithm_2_conditional_probability(clean_word)
    
    def _update_candidate_dictionary(self, clean_word):
        """Dynamic filtering system as per Phase 3"""
        self.current_dictionary = []
        
        for dict_word in self.full_dictionary:
            dict_word = dict_word.lower()
            
            # Length constraint
            if len(dict_word) != len(clean_word):
                continue
            
            # Pattern matching with revealed letters
            if not re.match(clean_word, dict_word):
                continue
            
            # Absence constraints - word cannot contain guessed letters that aren't in pattern
            skip_word = False
            for guessed_letter in self.guessed_letters:
                if guessed_letter not in clean_word and guessed_letter in dict_word:
                    skip_word = True
                    break
            
            if skip_word:
                continue
            
            # Frequency constraints - check for exact letter counts
            revealed_letter_counts = Counter(c for c in clean_word if c != '.')
            for letter, count in revealed_letter_counts.items():
                if dict_word.count(letter) != count:
                    skip_word = True
                    break
            
            if skip_word:
                continue
            
            self.current_dictionary.append(dict_word)
    
    def _algorithm_1_length_based_frequency(self, clean_word):
        """Algorithm 1: Length-Based Frequency Strategy (Early Game)"""
        length = len(clean_word)
        
        # Use pre-computed optimal first letters for this length
        if length in self.optimal_first_letters:
            for letter in self.optimal_first_letters[length]:
                if letter not in self.guessed_letters:
                    return letter
        
        # Fallback to general frequency
        return self._get_most_frequent_unguessed_letter()
    
    def _algorithm_2_conditional_probability(self, clean_word):
        """Algorithm 2: Conditional Probability Strategy (Mid Game)"""
        if not self.current_dictionary:
            return self._get_most_frequent_unguessed_letter()
        
        # Calculate letter frequencies in current candidate set
        letter_counts = defaultdict(int)
        for word in self.current_dictionary:
            for letter in set(word):  # Count each letter once per word
                if letter not in self.guessed_letters:
                    letter_counts[letter] += 1
        
        # Apply conditional probability based on already revealed letters
        revealed_letters = set(c for c in clean_word if c != '.')
        
        # Boost scores based on conditional frequency
        adjusted_scores = {}
        for letter, count in letter_counts.items():
            score = count
            
            # Apply conditional frequency boosting
            for revealed_letter in revealed_letters:
                if letter in self.conditional_frequency[revealed_letter]:
                    conditional_boost = self.conditional_frequency[revealed_letter][letter] / 1000.0
                    score += conditional_boost
            
            adjusted_scores[letter] = score
        
        # Return letter with highest adjusted score
        if adjusted_scores:
            best_letter = max(adjusted_scores.items(), key=lambda x: x[1])[0]
            return best_letter
        
        return self._get_most_frequent_unguessed_letter()
    
    def _algorithm_3_direct_pattern_matching(self, clean_word):
        """Algorithm 3: Direct Pattern Matching (Late Game)"""
        if not self.current_dictionary:
            return self._get_most_frequent_unguessed_letter()
        
        # When few candidates remain, directly count letter frequency
        letter_counts = defaultdict(int)
        for word in self.current_dictionary:
            for letter in word:
                if letter not in self.guessed_letters:
                    letter_counts[letter] += 1
        
        # Return most frequent letter in remaining candidates
        if letter_counts:
            return max(letter_counts.items(), key=lambda x: x[1])[0]
        
        return self._get_most_frequent_unguessed_letter()
    
    def _get_most_frequent_unguessed_letter(self):
        """Fallback to general frequency distribution"""
        # Use overall frequency from full dictionary
        overall_frequency = defaultdict(int)
        for word in self.full_dictionary:
            for letter in word.lower():
                if letter.isalpha():
                    overall_frequency[letter] += 1
        
        sorted_letters = sorted(overall_frequency.items(), key=lambda x: x[1], reverse=True)
        
        for letter, _ in sorted_letters:
            if letter not in self.guessed_letters:
                return letter
        
        # Ultimate fallback
        for letter in string.ascii_lowercase:
            if letter not in self.guessed_letters:
                return letter
        
        return 'e'  # Should never reach here
    
    def _calculate_information_gain(self, letter, candidates):
        """Calculate expected information gain from guessing a letter"""
        if not candidates:
            return 0
        
        words_with_letter = [word for word in candidates if letter in word]
        words_without_letter = [word for word in candidates if letter not in word]
        
        total_words = len(candidates)
        prob_with = len(words_with_letter) / total_words
        prob_without = len(words_without_letter) / total_words
        
        # Calculate entropy reduction
        current_entropy = math.log2(total_words) if total_words > 0 else 0
        
        expected_entropy = 0
        if prob_with > 0:
            expected_entropy += prob_with * math.log2(len(words_with_letter))
        if prob_without > 0:
            expected_entropy += prob_without * math.log2(len(words_without_letter))
        
        return current_entropy - expected_entropy
    
    # API interaction methods (same as original)
    def start_game(self, practice=True, verbose=True):
        self.guessed_letters = []
        self.current_dictionary = self.full_dictionary
                         
        response = self.request("/new_game", {"practice": practice})
        if response.get('status') == "approved":
            game_id = response.get('game_id')
            word = response.get('word')
            tries_remains = response.get('tries_remains')
            if verbose:
                print("Successfully start a new game! Game ID: {0}. # of tries remaining: {1}. Word: {2}.".format(game_id, tries_remains, word))
            
            while tries_remains > 0:
                guess_letter = self.guess(word)
                self.guessed_letters.append(guess_letter)
                
                if verbose:
                    print("Guessing letter: {0}".format(guess_letter))
                    print("Current candidates: {0}".format(len(self.current_dictionary)))
                    print("Game phase: {0}".format(self.game_phase))
                    
                try:    
                    res = self.request("/guess_letter", {"request": "guess_letter", "game_id": game_id, "letter": guess_letter})
                except HangmanAPIError:
                    print('HangmanAPIError exception caught on request.')
                    continue
                except Exception as e:
                    print('Other exception caught on request.')
                    raise e
               
                if verbose:
                    print("Server response: {0}".format(res))
                
                status = res.get('status')
                tries_remains = res.get('tries_remains')
                if status == "success":
                    if verbose:
                        print("Successfully finished game: {0}".format(game_id))
                    return True
                elif status == "failed":
                    reason = res.get('reason', '# of tries exceeded!')
                    if verbose:
                        print("Failed game: {0}. Because of: {1}".format(game_id, reason))
                    return False
                elif status == "ongoing":
                    word = res.get('word')
        else:
            if verbose:
                print("Failed to start a new game")
        return status == "success"
        
    def my_status(self):
        return self.request("/my_status", {})
    
    def request(self, path, args=None, post_args=None, method=None):
        if args is None:
            args = dict()
        if post_args is not None:
            method = "POST"

        if self.access_token:
            if post_args and "access_token" not in post_args:
                post_args["access_token"] = self.access_token
            elif "access_token" not in args:
                args["access_token"] = self.access_token

        time.sleep(0.2)

        num_retry, time_sleep = 50, 2
        for it in range(num_retry):
            try:
                if not REQUESTS_AVAILABLE or self.session is None:
                    # Mock response for testing
                    class MockResponse:
                        def __init__(self):
                            self.headers = {'content-type': 'application/json'}
                            self.text = '{"status": "success", "game_id": "test", "word": "test", "tries_remains": 6}'
                        def json(self):
                            return {"status": "success", "game_id": "test", "word": "test", "tries_remains": 6}
                    response = MockResponse()
                else:
                    response = self.session.request(
                        method or "GET",
                        self.hangman_url + path,
                        timeout=self.timeout,
                        params=args,
                        data=post_args,
                        verify=False
                    )
                break
            except Exception as e:
                if REQUESTS_AVAILABLE and hasattr(requests, 'exceptions') and isinstance(e, requests.exceptions.SSLError):
                    if it + 1 == num_retry:
                        raise
                    time.sleep(time_sleep)
                    continue
                elif hasattr(e, 'read'):
                    try:
                        response_text = e.read()  # type: ignore
                        response = json.loads(response_text)
                        raise HangmanAPIError(response)
                    except:
                        raise HangmanAPIError(str(e))
                else:
                    raise HangmanAPIError(str(e))

        headers = response.headers
        if 'json' in headers['content-type']:
            result = response.json()
        elif "access_token" in parse_qs(response.text):
            query_str = parse_qs(response.text)
            if "access_token" in query_str:
                result = {"access_token": query_str["access_token"][0]}
                if "expires" in query_str:
                    result["expires"] = query_str["expires"][0]
            else:
                raise HangmanAPIError(response.json())
        else:
            raise HangmanAPIError('Maintype was not text, or querystring')

        if result and isinstance(result, dict) and result.get("error"):
            raise HangmanAPIError(result)
        return result

class HangmanAPIError(Exception):
    def __init__(self, result):
        self.result = result
        self.code = None
        try:
            self.type = result["error_code"]
        except (KeyError, TypeError):
            self.type = ""

        try:
            self.message = result["error_description"]
        except (KeyError, TypeError):
            try:
                self.message = result["error"]["message"]
                self.code = result["error"].get("code")
                if not self.type:
                    self.type = result["error"].get("type", "")
            except (KeyError, TypeError):
                try:
                    self.message = result["error_msg"]
                except (KeyError, TypeError):
                    self.message = result

        Exception.__init__(self, self.message)

# Example usage
if __name__ == "__main__":
    # Initialize the improved API
    api = AdvancedHangmanAPI(access_token="e4a58ba7e054be19f90498a91cd47c", timeout=2000)
    
    # Run practice games
    print("Starting practice games with improved algorithm...")
    api.start_game(practice=True, verbose=True)
    
    try:
        status = api.my_status()
        if isinstance(status, (list, tuple)) and len(status) >= 4:
            total_practice_runs, total_recorded_runs, total_recorded_successes, total_practice_successes = status
            # Ensure values are numbers
            total_practice_runs = int(total_practice_runs) if total_practice_runs else 0
            total_practice_successes = int(total_practice_successes) if total_practice_successes else 0
            
            practice_success_rate = total_practice_successes / total_practice_runs if total_practice_runs > 0 else 0
            print('Run %d practice games out of an allotted 100,000. Practice success rate so far = %.3f' % (total_practice_runs, practice_success_rate))
        else:
            print("Status response format unexpected:", status)
    except Exception as e:
        print("Status check failed - this is normal if running locally without the API server:", str(e))