import random
from collections import defaultdict
import re
import os
# Run python executable and read output
# ./Speeches

class NgramTextGenerator:
    def __init__(self, n):
        self.n = n
        self.ngrams = defaultdict(list)
    
    def train(self, corpus):
        words = corpus.split()
        for i in range(len(words) - self.n):
            gram = tuple(words[i:i+self.n])
            next_word = words[i+self.n]
            self.ngrams[gram].append(next_word)
        
        # Remove n-grams that start and end with parentheses (timestamps)
        self.ngrams = {k: v for k, v in self.ngrams.items() 
                        if not (k[0].startswith('(') and k[-1].endswith(')'))}
    
    def generate_text(self, num_words):
        if not self.ngrams:
            return "Error: No n-grams available. The corpus might be empty after preprocessing."
        
        current_gram = random.choice(list(self.ngrams.keys()))
        result = list(current_gram)
        for _ in range(num_words - self.n):
            if current_gram in self.ngrams:
                next_word = random.choice(self.ngrams[current_gram])
                result.append(next_word)
                current_gram = tuple(result[-self.n:])
            else:
                break
        return ' '.join(result)

def preprocess_corpus(text):
    # Make everything lowercase
    text = text.lower()
    
    # Replace all types of apostrophes with standard single quote
    text = re.sub(r'[''`’]', "'", text)
    text = re.sub(r'…', "...", text)
    text = re.sub(r'[“”]', "\"", text)
    
    # Remove standalone parentheses (like timestamps)
    text = re.sub(r'\s*\([^)]*\)\s*', ' ', text)
    
    return text

def load_corpus(folder_path):
    full_corpus = ""
    try:
        for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    raw_text = file.read()
                    processed_text = preprocess_corpus(raw_text)
                    full_corpus += processed_text + " "
        
        if not full_corpus:
            print("No .txt files found in the specified folder.")
            return ""
        
        print(f"Processed {len(os.listdir(folder_path))} files.")
        return full_corpus.strip()
    except FileNotFoundError:
        print(f"Error: Folder '{folder_path}' not found.")
        return ""
    except Exception as e:
        print(f"Error reading files: {e}")
        return ""

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    speeches_folder = os.path.join(script_dir, "Speeches")
    
    corpus = load_corpus(speeches_folder)
    
    if not corpus:
        print("No corpus loaded. Exiting.")
        return
    
    generator = NgramTextGenerator(n=5)
    generator.train(corpus)
    
    print(f"Number of n-grams: {len(generator.ngrams)}")
    
    generated_text = generator.generate_text(num_words=100)
    print("\nGenerated Text:")
    print(generated_text)

if __name__ == "__main__":
    main()
