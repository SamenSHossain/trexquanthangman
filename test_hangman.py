#!/usr/bin/env python3

from hangman_improved import HangmanAPI

def test_hangman_algorithm():
    """Test the improved hangman algorithm with a few examples."""
    
    # Create an instance of the API
    api = HangmanAPI()
    
    # Test cases with various word patterns
    test_cases = [
        "_ _ _ _ _",      # 5 letter word
        "_ p p _ e",     # apple-like pattern
        "h _ _ _ _",      # word starting with h
        "_ _ _ _ _ _ _",   # 7 letter word
        "t _ _ _",       # 4 letter word starting with t
        "_ _ n _ _",      # 5 letter word with n in middle
    ]
    
    print("Testing improved Hangman algorithm:")
    print("=" * 50)
    
    for i, word_pattern in enumerate(test_cases, 1):
        print(f"\nTest {i}: Pattern '{word_pattern}'")
        
        # Reset for each test
        api.guessed_letters = []
        api.current_dictionary = api.full_dictionary
        
        # Get first guess
        first_guess = api.guess(word_pattern)
        print(f"First guess: '{first_guess}'")
        
        # Simulate a few more guesses
        api.guessed_letters.append(first_guess)
        second_guess = api.guess(word_pattern)
        print(f"Second guess: '{second_guess}'")
        
        api.guessed_letters.append(second_guess)
        third_guess = api.guess(word_pattern)
        print(f"Third guess: '{third_guess}'")
        
        # Show how many words are still possible
        print(f"Possible words remaining: {len(api.current_dictionary)}")
        if len(api.current_dictionary) <= 5:
            print(f"Examples: {api.current_dictionary[:5]}")
        else:
            print(f"Examples: {api.current_dictionary[:5]}...")

def main():
    test_hangman_algorithm()
    
    print("\n" + "=" * 50)
    print("Key improvements in this algorithm:")
    print("1. Better pattern matching that excludes words with incorrect letters")
    print("2. Position-based frequency analysis for more strategic guessing")
    print("3. Length-based dictionary filtering for better performance")
    print("4. Multiple fallback strategies for edge cases")
    print("5. Improved handling of known vs unknown letter positions")
    print("\nThis should significantly improve the success rate beyond 18%!")

if __name__ == "__main__":
    main()