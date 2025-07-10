import json
import requests
import random
import string
import secrets
import time
import re
import collections

try:
    from urllib.parse import parse_qs, urlencode, urlparse
except ImportError:
    from urlparse import parse_qs, urlparse
    from urllib import urlencode

# Disable SSL warnings if available
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    pass

class HangmanAPI(object):
    def __init__(self, access_token=None, session=None, timeout=None):
        self.hangman_url = self.determine_hangman_url()
        self.access_token = access_token
        self.session = session or requests.Session()
        self.timeout = timeout
        self.guessed_letters = []
        
        full_dictionary_location = "words_250000_train.txt"
        self.full_dictionary = self.build_dictionary(full_dictionary_location)        
        self.full_dictionary_common_letter_sorted = collections.Counter("".join(self.full_dictionary)).most_common()
        
        # Pre-compute dictionaries by length for better performance
        self.dictionary_by_length = {}
        for word in self.full_dictionary:
            length = len(word)
            if length not in self.dictionary_by_length:
                self.dictionary_by_length[length] = []
            self.dictionary_by_length[length].append(word)
        
        self.current_dictionary = []
        
    @staticmethod
    def determine_hangman_url():
        links = ['https://trexsim.com']

        data = {link: 0.0 for link in links}

        for link in links:
            try:
                requests.get(link)
            except:
                continue

            for i in range(10):
                s = time.time()
                try:
                    requests.get(link)
                    data[link] = time.time() - s
                except:
                    continue

        link = sorted(data.items(), key=lambda x: x[1])[0][0]
        link += '/trexsim/hangman'
        return link

    def guess(self, word): # word input example: "_ p p _ e "
        ###############################################
        # Improved "guess" function with better logic #
        ###############################################

        # Clean the word - remove spaces and get positions
        clean_word = word[::2]  # Every other character (skipping spaces)
        len_word = len(clean_word)
        
        # Get current dictionary filtered by length
        if len_word in self.dictionary_by_length:
            current_dictionary = self.dictionary_by_length[len_word]
        else:
            current_dictionary = self.full_dictionary
        
        # Filter dictionary based on current pattern and guessed letters
        new_dictionary = []
        
        # Extract known letters and their positions
        known_letters = set()
        for i, char in enumerate(clean_word):
            if char != '_':
                known_letters.add(char)
        
        # Extract incorrect letters (guessed but not in current pattern)
        incorrect_letters = set(self.guessed_letters) - known_letters
        
        for dict_word in current_dictionary:
            if len(dict_word) != len_word:
                continue
            
            # Check if word contains any incorrect letters
            if any(letter in dict_word for letter in incorrect_letters):
                continue
            
            # Check if word matches the current pattern
            match = True
            for i, char in enumerate(clean_word):
                if char != '_' and dict_word[i] != char:
                    match = False
                    break
                elif char == '_' and dict_word[i] in known_letters:
                    # This position should not have a known letter if it's still blank
                    match = False
                    break
            
            if match:
                new_dictionary.append(dict_word)
        
        # Update current dictionary
        self.current_dictionary = new_dictionary
        
        # If we have candidate words, use position-based frequency analysis
        if new_dictionary:
            # Count letter frequencies by position
            position_freq = {}
            for pos in range(len_word):
                if clean_word[pos] == '_':  # Only count for unknown positions
                    position_freq[pos] = collections.Counter()
            
            # Count letters at each unknown position
            for dict_word in new_dictionary:
                for pos in range(len_word):
                    if clean_word[pos] == '_':
                        letter = dict_word[pos]
                        if letter not in self.guessed_letters:
                            position_freq[pos][letter] += 1
            
            # Find the best letter to guess
            best_letter = None
            best_score = 0
            
            # Calculate weighted score for each letter
            letter_scores = collections.defaultdict(int)
            
            for pos, counter in position_freq.items():
                for letter, count in counter.items():
                    if letter not in self.guessed_letters:
                        # Weight by frequency and position importance
                        letter_scores[letter] += count
            
            # Get the letter with highest score
            if letter_scores:
                best_letter = max(letter_scores.items(), key=lambda x: x[1])[0]
            
            if best_letter:
                return best_letter
        
        # Fallback 1: Use overall frequency from current dictionary
        if new_dictionary:
            full_dict_string = "".join(new_dictionary)
            c = collections.Counter(full_dict_string)
            sorted_letter_count = c.most_common()
            
            for letter, count in sorted_letter_count:
                if letter not in self.guessed_letters:
                    return letter
        
        # Fallback 2: Use common letters from full dictionary
        # But prioritize letters that are more likely to appear in words of this length
        if len_word in self.dictionary_by_length:
            length_dict_string = "".join(self.dictionary_by_length[len_word])
            c = collections.Counter(length_dict_string)
            sorted_letter_count = c.most_common()
            
            for letter, count in sorted_letter_count:
                if letter not in self.guessed_letters:
                    return letter
        
        # Final fallback: Use full dictionary frequency
        for letter, count in self.full_dictionary_common_letter_sorted:
            if letter not in self.guessed_letters:
                return letter
        
        # Should never reach here, but just in case
        return 'e'

    ##########################################################
    # You'll likely not need to modify any of the code below #
    ##########################################################
    
    def build_dictionary(self, dictionary_file_location):
        text_file = open(dictionary_file_location,"r")
        full_dictionary = text_file.read().splitlines()
        text_file.close()
        return full_dictionary
                
    def start_game(self, practice=True, verbose=True):
        # reset guessed letters to empty set and current plausible dictionary to the full dictionary
        self.guessed_letters = []
        self.current_dictionary = self.full_dictionary
                         
        response = self.request("/new_game", {"practice":practice})
        if response.get('status')=="approved":
            game_id = response.get('game_id')
            word = response.get('word')
            tries_remains = response.get('tries_remains')
            if verbose:
                print("Successfully start a new game! Game ID: {0}. # of tries remaining: {1}. Word: {2}.".format(game_id, tries_remains, word))
            
            # Convert tries_remains to int if it's a string
            try:
                tries_remains = int(tries_remains) if tries_remains is not None else 0
            except (ValueError, TypeError):
                tries_remains = 0
                
            while tries_remains > 0:
                # get guessed letter from user code
                guess_letter = self.guess(word)
                    
                # append guessed letter to guessed letters field in hangman object
                self.guessed_letters.append(guess_letter)
                if verbose:
                    print("Guessing letter: {0}".format(guess_letter))
                    
                try:    
                    res = self.request("/guess_letter", {"request":"guess_letter", "game_id":game_id, "letter":guess_letter})
                except HangmanAPIError:
                    print('HangmanAPIError exception caught on request.')
                    continue
                except Exception as e:
                    print('Other exception caught on request.')
                    raise e
               
                if verbose:
                    print("Sever response: {0}".format(res))
                status = res.get('status')
                tries_remains = res.get('tries_remains')
                
                # Convert tries_remains to int if it's a string
                try:
                    tries_remains = int(tries_remains) if tries_remains is not None else 0
                except (ValueError, TypeError):
                    tries_remains = 0
                    
                if status=="success":
                    if verbose:
                        print("Successfully finished game: {0}".format(game_id))
                    return True
                elif status=="failed":
                    reason = res.get('reason', '# of tries exceeded!')
                    if verbose:
                        print("Failed game: {0}. Because of: {1}".format(game_id, reason))
                    return False
                elif status=="ongoing":
                    word = res.get('word')
        else:
            if verbose:
                print("Failed to start a new game")
        return status=="success"
        
    def my_status(self):
        return self.request("/my_status", {})
    
    def request(
            self, path, args=None, post_args=None, method=None):
        if args is None:
            args = dict()
        if post_args is not None:
            method = "POST"

        # Add `access_token` to post_args or args if it has not already been
        # included.
        if self.access_token:
            # If post_args exists, we assume that args either does not exists
            # or it does not need `access_token`.
            if post_args and "access_token" not in post_args:
                post_args["access_token"] = self.access_token
            elif "access_token" not in args:
                args["access_token"] = self.access_token

        time.sleep(0.2)

        num_retry, time_sleep = 50, 2
        for it in range(num_retry):
            try:
                response = self.session.request(
                    method or "GET",
                    self.hangman_url + path,
                    timeout=self.timeout,
                    params=args,
                    data=post_args,
                    verify=False
                )
                break
            except requests.HTTPError as e:
                try:
                    response = json.loads(str(e))
                    raise HangmanAPIError(response)
                except:
                    raise HangmanAPIError({'error': str(e)})
            except requests.exceptions.SSLError as e:
                if it + 1 == num_retry:
                    raise
                time.sleep(time_sleep)

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