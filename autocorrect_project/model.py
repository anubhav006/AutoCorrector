import re
from collections import Counter
import os
import random

class SpellCorrector:
    def __init__(self):
        self.WORDS = Counter()
        self.N = 0
        
    def words(self, text): 
        return re.findall(r'\w+', text.lower())

    def train(self, path_to_file):
        """
        Loads 'final.txt', trains the model, and calculates accuracy.
        """
        print(f"📂 Loading file: {path_to_file}...")
        
        if not os.path.exists(path_to_file):
            print(f"❌ Error: File '{path_to_file}' not found.")
            return False

        try:
            with open(path_to_file, 'r', encoding='utf-8') as f:
                text_data = f.read()
                
            all_tokens = self.words(text_data)
            
            # --- SPLIT DATA (90% Train, 10% Test) ---
            split_index = int(len(all_tokens) * 0.9)
            train_tokens = all_tokens[:split_index]
            test_tokens = all_tokens[split_index:]
            
            # Train on the 90%
            self.WORDS = Counter(train_tokens)
            self.N = sum(self.WORDS.values())
            
            print(f"✅ Training Complete!")
            print(f"📊 Vocabulary Size: {len(self.WORDS)} unique words")
            print(f"📚 Total Word Count: {self.N}")
            
            # Calculate Accuracy on the remaining 10%
            self.calculate_accuracy(test_tokens)
            
            return True
            
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return False

    def calculate_accuracy(self, test_tokens):
        """
        Tests the model by masking words from the test set 
        and checking if the model recognizes them as valid.
        """
        print("\n--- 🎯 Calculating Accuracy ---")
        if not test_tokens:
            print("   Not enough data to test.")
            return

        # We test if the model 'knows' the words in the test set
        # (Since we don't have a labeled 'wrong->right' dataset, 
        # we check 'Coverage Accuracy': how many valid words are recognized?)
        
        known_count = 0
        unknown_count = 0
        
        # Test a sample of 1000 words to be fast
        sample_size = min(len(test_tokens), 1000)
        sample_tokens = random.sample(test_tokens, sample_size)
        
        for word in sample_tokens:
            if word in self.WORDS:
                known_count += 1
            else:
                unknown_count += 1
        
        accuracy = (known_count / sample_size) * 100
        print(f"   ✅ Known Words: {known_count}")
        print(f"   ❌ Unknown Words: {unknown_count}")
        print(f"   🏆 Model Accuracy (Coverage): {accuracy:.2f}%")
        print("   (Note: Higher is better. It means the model knows most words.)")

    # --- Probability & Correction Logic ---
    def P(self, word): 
        return self.WORDS[word] / self.N

    def correction(self, word): 
        return max(self.candidates(word), key=self.P)

    def candidates(self, word): 
        return (self.known([word]) or self.known(self.edits1(word)) or 
                self.known(self.edits2(word)) or [word])

    def known(self, words): 
        return set(w for w in words if w in self.WORDS)

    def edits1(self, word):
        letters    = 'abcdefghijklmnopqrstuvwxyz'
        splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
        deletes    = [L + R[1:]               for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
        replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
        inserts    = [L + c + R               for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def edits2(self, word): 
        return (e2 for e1 in self.edits1(word) for e2 in self.edits1(e1))

# --- Main Execution Block ---
if __name__ == "__main__":
    corrector = SpellCorrector()
    file_name = "final.txt"
    
    # Train and Show Accuracy
    success = corrector.train(file_name)

    if success:
        print("\n--- 📝 Live Test Mode (Type 'exit' to quit) ---")
        while True:
            user_input = input("Enter a word: ").strip()
            if user_input.lower() == 'exit':
                break
            
            result = corrector.correction(user_input.lower())
            if result == user_input.lower():
                print(f"   ✅ Correct.")
            else:
                print(f"   🔧 Suggestion: {result}")