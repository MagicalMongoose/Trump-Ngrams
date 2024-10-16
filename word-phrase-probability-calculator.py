#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# python.exe .\word-phrase-probability-calculator.py
# ./Speeches

import re
import os
from collections import Counter
import plotly.graph_objects as go

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

def calculate_probabilities(corpus, input_array):
    # Split the corpus into words
    words = corpus.split()
    total_words = len(words)
    
    # Count the occurrences of each word
    word_counts = Counter(words)
    
    # Calculate probabilities
    probabilities = {}
    for item in input_array:
        item = item.lower()  # Convert to lowercase for consistency
        if ' ' in item:  # It's a phrase
            phrase_count = corpus.count(item)
            probabilities[item] = phrase_count / (total_words - len(item.split()) + 1)
        else:  # It's a single word
            probabilities[item] = word_counts[item] / total_words
    
    return probabilities

def visualize_probabilities(probabilities):
    # Sort probabilities from highest to lowest
    sorted_probs = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
    words, probs = zip(*sorted_probs)

    # Convert probabilities to percentages
    percentages = [prob * 100 for prob in probs]

    # Create the bar chart
    fig = go.Figure(data=[go.Bar(x=words, y=percentages)])

    # Update the layout
    fig.update_layout(
        title="Word/Phrase Probabilities in Corpus",
        xaxis_title="Words/Phrases",
        yaxis_title="Probability (%)",
        xaxis_tickangle=-45
    )

    # Update y-axis to show percentages
    fig.update_yaxes(ticksuffix="%")

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
    print("Enter words or phrases, one per line. Enter an empty line to finish:")
    input_array = []
    while True:
        item = input().strip()
        if not item:
            break
        input_array.append(item)
    
    # Calculate probabilities
    probabilities = calculate_probabilities(corpus, input_array)
    
    # Display probabilities as percentages
    print("\nProbabilities:")
    for item, prob in sorted(probabilities.items(), key=lambda x: x[1], reverse=True):
        print(f"{item}: {prob*100:.4f}%")    

    # Visualize probabilities
    visualize_probabilities(probabilities)

if __name__ == "__main__":
    main()
