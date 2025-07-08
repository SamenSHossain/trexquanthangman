#!/usr/bin/env python3
"""
Test script for the improved Hangman algorithm.
This script simulates hangman games locally to test the algorithm without using API calls.
"""

import random
from improved_hangman import AdvancedHangmanAPI

class HangmanSimulator:
    """Local simulator for testing the hangman algorithm"""
    
    def __init__(self, dictionary):
        self.dictionary = [word.lower() for word in dictionary]
        
    def simulate_game(self, target_word, algorithm, max_wrong_guesses=6, verbose=False):
        """Simulate a single hangman game"""
        target_word = target_word.lower()
        guessed_letters = []
        wrong_guesses = 0
        
        # Initialize current word display
        current_display = ['_' for _ in target_word]
        
        if verbose:
            print(f"\nSimulating game with word: {target_word}")
            print(f"Initial display: {' '.join(current_display)}")
        
        while wrong_guesses < max_wrong_guesses:
            # Create word display for algorithm
            word_display = ' '.join(current_display)
            
            # Set up algorithm state
            algorithm.guessed_letters = guessed_letters[:]
            
            # Get guess from algorithm
            guess = algorithm.guess(word_display)
            
            if guess in guessed_letters:
                if verbose:
                    print(f"Algorithm made duplicate guess: {guess}")
                wrong_guesses += 1
                continue
                
            guessed_letters.append(guess)
            
            # Check if guess is correct
            if guess in target_word:
                # Update display
                for i, letter in enumerate(target_word):
                    if letter == guess:
                        current_display[i] = letter
                        
                if verbose:
                    print(f"Guessed '{guess}' - CORRECT! Display: {' '.join(current_display)}")
                    
                # Check if word is complete
                if '_' not in current_display:
                    if verbose:
                        print(f"Word completed! Total wrong guesses: {wrong_guesses}")
                    return True, wrong_guesses, len(guessed_letters)
            else:
                wrong_guesses += 1
                if verbose:
                    print(f"Guessed '{guess}' - WRONG! ({wrong_guesses}/{max_wrong_guesses})")
        
        if verbose:
            print(f"Game failed. Word was: {target_word}")
        return False, wrong_guesses, len(guessed_letters)
    
    def run_test_suite(self, algorithm, num_games=100, verbose=False):
        """Run a comprehensive test suite"""
        print(f"\nRunning {num_games} simulated games...")
        
        wins = 0
        total_wrong_guesses = 0
        total_guesses = 0
        word_length_stats = {}
        
        # Test with random words from dictionary
        test_words = random.sample(self.dictionary, min(num_games, len(self.dictionary)))
        
        for i, word in enumerate(test_words):
            if verbose and i < 5:  # Show details for first 5 games
                print(f"\n--- Game {i+1} ---")
                success, wrong_guesses, total_guesses_made = self.simulate_game(
                    word, algorithm, verbose=True
                )
            else:
                success, wrong_guesses, total_guesses_made = self.simulate_game(
                    word, algorithm, verbose=False
                )
            
            if success:
                wins += 1
            
            total_wrong_guesses += wrong_guesses
            total_guesses += total_guesses_made
            
            # Track stats by word length
            word_len = len(word)
            if word_len not in word_length_stats:
                word_length_stats[word_len] = {'wins': 0, 'total': 0}
            word_length_stats[word_len]['total'] += 1
            if success:
                word_length_stats[word_len]['wins'] += 1
        
        # Print results
        success_rate = wins / num_games
        avg_wrong_guesses = total_wrong_guesses / num_games
        avg_total_guesses = total_guesses / num_games
        
        print(f"\n{'='*50}")
        print(f"TEST RESULTS")
        print(f"{'='*50}")
        print(f"Games played: {num_games}")
        print(f"Wins: {wins}")
        print(f"Success rate: {success_rate:.3f} ({success_rate*100:.1f}%)")
        print(f"Average wrong guesses per game: {avg_wrong_guesses:.2f}")
        print(f"Average total guesses per game: {avg_total_guesses:.2f}")
        
        print(f"\nSuccess rate by word length:")
        for length in sorted(word_length_stats.keys()):
            stats = word_length_stats[length]
            if stats['total'] > 0:
                rate = stats['wins'] / stats['total']
                print(f"  {length} letters: {rate:.3f} ({stats['wins']}/{stats['total']})")
        
        return success_rate

def main():
    """Main test function"""
    print("Initializing Advanced Hangman Algorithm...")
    
    # Initialize the algorithm
    api = AdvancedHangmanAPI()
    
    # Get the dictionary
    dictionary = api.full_dictionary
    print(f"Dictionary loaded: {len(dictionary)} words")
    
    # Create simulator
    simulator = HangmanSimulator(dictionary)
    
    # Run tests
    print("\n" + "="*60)
    print("TESTING IMPROVED HANGMAN ALGORITHM")
    print("="*60)
    
    # Test with small sample first (verbose)
    print("\nRunning detailed test with 10 games...")
    simulator.run_test_suite(api, num_games=10, verbose=True)
    
    # Run larger test suite
    print(f"\n{'='*60}")
    print("Running comprehensive test...")
    success_rate = simulator.run_test_suite(api, num_games=100, verbose=False)
    
    # Expected performance analysis
    print(f"\n{'='*60}")
    print("PERFORMANCE ANALYSIS")
    print(f"{'='*60}")
    print(f"Achieved success rate: {success_rate:.3f} ({success_rate*100:.1f}%)")
    print(f"Target success rate: 0.550-0.650 (55-65%)")
    
    if success_rate >= 0.55:
        print("✅ SUCCESS: Algorithm meets target performance!")
        if success_rate >= 0.60:
            print("🎉 EXCELLENT: Algorithm exceeds expectations!")
    else:
        print("⚠️  NEEDS IMPROVEMENT: Algorithm below target performance")
        print("   Consider tuning parameters or adding more sophisticated strategies")
    
    # Test specific challenging scenarios
    print(f"\n{'='*60}")
    print("TESTING CHALLENGING SCENARIOS")
    print(f"{'='*60}")
    
    challenging_words = [
        "rhythm", "syzygy", "jazz", "quiz", "gypsy", 
        "lymph", "nymph", "psych", "crypt", "myths"
    ]
    
    challenging_words = [w for w in challenging_words if w in dictionary]
    if challenging_words:
        print(f"Testing {len(challenging_words)} challenging words...")
        challenging_wins = 0
        for word in challenging_words:
            success, _, _ = simulator.simulate_game(word, api, verbose=False)
            if success:
                challenging_wins += 1
        
        challenging_rate = challenging_wins / len(challenging_words)
        print(f"Challenging words success rate: {challenging_rate:.3f} ({challenging_wins}/{len(challenging_words)})")
    
    print(f"\n{'='*60}")
    print("TEST COMPLETE")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()