#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# python.exe '.\Custom Trump Text Generator.py' 
# ./Speeches

import random
from collections import defaultdict, Counter
import re
import os
import plotly.graph_objects as go
import sys

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
    
    def generate_text(self, seed, num_words):
        if not self.ngrams:
            return "Error: No n-grams available. The corpus might be empty after preprocessing."
        
        seed_words = seed.split()
        if len(seed_words) < self.n:
            return f"Error: Seed must be at least {self.n} words long."
        
        result = seed_words
        current_gram = tuple(seed_words[-self.n:])
        
        for _ in range(num_words):
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

def visualize_top_ngrams(generator, top_n=100):
    # Count the frequency of each n-gram
    ngram_counts = Counter({' '.join(gram): len(next_words) for gram, next_words in generator.ngrams.items()})
    
    # Get the top N most common n-grams
    top_ngrams = ngram_counts.most_common(top_n)
    
    # Prepare data for plotting
    ngrams, counts = zip(*top_ngrams)
    
    # Create the bar chart
    fig = go.Figure(data=[go.Bar(x=ngrams, y=counts)])
    
    # Update the layout
    fig.update_layout(
        title=f"Top {top_n} Most Frequent {generator.n}-grams",
        xaxis_title="N-grams",
        yaxis_title="Frequency",
        xaxis_tickangle=-45
    )
    
    # Show the plot
    fig.show()

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    speeches_folder = os.path.join(script_dir, "Speeches")
    
    corpus = load_corpus(speeches_folder)
    
    if not corpus:
        print("No corpus loaded. Exiting.")
        return
    
    # Get user input
    seed = input("Enter a seed text: ")
    seed = preprocess_corpus(seed)  # Preprocess the seed text
    
    # Determine n-gram size based on input length
    n = len(seed.split())
    print(f"Using {n}-grams based on your input.")
    
    generator = NgramTextGenerator(n)
    generator.train(corpus)
    
    print(f"Number of {n}-grams: {len(generator.ngrams)}")
    
    generated_text = generator.generate_text(seed, 100)
    print("\nGenerated Text:")
    print(generated_text)
    
    # Visualize top 100 n-grams
    #visualize_top_ngrams(generator)

if __name__ == "__main__":
    # Redirect stdout to the terminal
    sys.stdout = sys.__stdout__
    main()
