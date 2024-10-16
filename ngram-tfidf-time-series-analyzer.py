#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
from collections import Counter
import plotly.graph_objects as go
from datetime import datetime
from nltk import ngrams
import math

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[''`’]', "'", text)
    text = re.sub(r'…', "...", text)
    text = re.sub(r'[“”]', "\"", text)
    text = re.sub(r'\s*\([^)]*\)\s*', ' ', text)
    return text

def load_corpus(folder_path):
    corpus = []
    try:
        for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):
                file_path = os.path.join(folder_path, filename)
                creation_time = os.path.getctime(file_path)
                with open(file_path, 'r', encoding='utf-8') as file:
                    raw_text = file.read()
                    processed_text = preprocess_text(raw_text)
                    corpus.append((creation_time, processed_text))
        
        if not corpus:
            print("No .txt files found in the specified folder.")
            return []
        
        print(f"Processed {len(corpus)} files.")
        return sorted(corpus, key=lambda x: x[0])
    except Exception as e:
        print(f"Error reading files: {e}")
        return []

def generate_ngrams(text, n):
    words = text.split()
    return list(ngrams(words, n))

def calculate_tf_idf(corpus, n):
    document_ngrams = [generate_ngrams(text, n) for _, text in corpus]
    ngram_doc_freq = Counter()
    
    for doc_ngrams in document_ngrams:
        ngram_doc_freq.update(set(doc_ngrams))
    
    total_docs = len(corpus)
    tf_idf_scores = []
    
    for doc_ngrams in document_ngrams:
        ngram_freq = Counter(doc_ngrams)
        doc_tf_idf = {}
        for ngram, freq in ngram_freq.items():
            tf = freq / len(doc_ngrams)
            idf = math.log(total_docs / (ngram_doc_freq[ngram] + 1))
            doc_tf_idf[ngram] = tf * idf
        tf_idf_scores.append(doc_tf_idf)
    
    return tf_idf_scores

def calculate_top_ngrams_tfidf(corpus, n, window_size):
    tf_idf_scores = calculate_tf_idf(corpus, n)
    results = []
    
    for i in range(len(corpus)):
        start = max(0, i - window_size + 1)
        window_scores = tf_idf_scores[start:i+1]
        combined_scores = Counter()
        for scores in window_scores:
            combined_scores.update(scores)
        
        top_10 = combined_scores.most_common(10)
        results.append((corpus[i][0], top_10))
    
    return results

def visualize_ngram_trends(ngram_data):
    ngram_dict = {}
    dates = [datetime.fromtimestamp(date) for date, _ in ngram_data]

    for date, top_ngrams in ngram_data:
        for ngram, score in top_ngrams:
            ngram_str = " ".join(ngram)
            if ngram_str not in ngram_dict:
                ngram_dict[ngram_str] = [0] * len(ngram_data)
            ngram_dict[ngram_str][ngram_data.index((date, top_ngrams))] = score

    fig = go.Figure()

    for ngram, scores in ngram_dict.items():
        fig.add_trace(go.Scatter(x=dates, y=scores, mode='lines', name=ngram))

    fig.update_layout(
        title="Top 10 N-gram TF-IDF Scores Over Time",
        xaxis_title="Date",
        yaxis_title="TF-IDF Score",
        legend_title="N-grams"
    )

    fig.show()

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    speeches_folder = os.path.join(script_dir, "Speeches")
    
    corpus = load_corpus(speeches_folder)
    
    if not corpus:
        print("No corpus loaded. Exiting.")
        return
    
    n = 3  # Use trigrams
    window_size = 5  # Use a window of 5 documents

    ngram_data = calculate_top_ngrams_tfidf(corpus, n, window_size)
    visualize_ngram_trends(ngram_data)

if __name__ == "__main__":
    main()
