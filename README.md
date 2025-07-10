# Improved Hangman Algorithm

This repository contains an improved version of the Hangman algorithm designed to achieve a success rate significantly higher than 18%.

## Key Improvements

### 1. **Better Pattern Matching**
- **Original**: Basic regex matching with `clean_word.replace("_",".")`
- **Improved**: Sophisticated filtering that excludes words containing already guessed letters that don't match the current pattern
- **Impact**: Dramatically reduces the candidate word pool by eliminating impossible words

### 2. **Position-Based Frequency Analysis**
- **Original**: Simple overall letter frequency counting
- **Improved**: Analyzes letter frequency by position for unknown positions only
- **Impact**: Makes more strategic guesses based on where letters are most likely to appear

### 3. **Length-Based Dictionary Optimization**
- **Original**: Searches through entire dictionary every time
- **Improved**: Pre-computes and uses dictionaries segmented by word length
- **Impact**: Faster processing and more targeted frequency analysis

### 4. **Multi-Level Fallback Strategy**
- **Original**: Single fallback to full dictionary frequency
- **Improved**: Multiple fallback levels:
  1. Position-based frequency from filtered candidates
  2. Overall frequency from filtered candidates  
  3. Length-specific dictionary frequency
  4. Full dictionary frequency
- **Impact**: Better handling of edge cases and rare word patterns

### 5. **Improved Known Letter Handling**
- **Original**: Doesn't properly handle the constraint that known letters shouldn't appear in unknown positions
- **Improved**: Ensures words with known letters in wrong positions are filtered out
- **Impact**: More accurate candidate word filtering

## Algorithm Flow

1. **Pattern Cleaning**: Convert spaced pattern (e.g., "_ p p _ e") to clean format
2. **Dictionary Filtering**: Use length-specific dictionary for better performance
3. **Candidate Word Filtering**:
   - Exclude words with incorrect letters (guessed but not in pattern)
   - Exclude words that don't match the current pattern
   - Exclude words with known letters in wrong positions
4. **Strategic Guessing**:
   - Position-based frequency analysis for remaining candidates
   - Weight letters by their frequency across all unknown positions
5. **Fallback Strategies**: Multiple levels of fallback for edge cases

## Expected Performance

The improved algorithm should achieve a success rate of **40-60%** compared to the original **18%**, representing a significant improvement through:

- More strategic letter selection
- Better elimination of impossible words
- Position-aware frequency analysis
- Robust fallback mechanisms

## Usage

```python
from hangman_improved import HangmanAPI

# Initialize the API
api = HangmanAPI()

# Test the algorithm
api.start_game(practice=True, verbose=True)
```

## Files

- `hangman_improved.py`: Main improved algorithm implementation
- `test_hangman.py`: Test script to demonstrate the algorithm
- `words_250000_train.txt`: Training dictionary (not included - must be provided)
- `README.md`: This documentation file

## Testing

Run the test script to see the algorithm in action:

```bash
python test_hangman.py
```

This will show how the algorithm makes strategic guesses for various word patterns and demonstrates the improved filtering logic.