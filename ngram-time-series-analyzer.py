import re
import os
from collections import Counter
import plotly.graph_objects as go
from datetime import datetime
from nltk import ngrams

# Run python executable and read output
# ./Speeches

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

def calculate_top_ngrams(corpus, n, window_size):
    results = []
    for i in range(len(corpus)):
        start = max(0, i - window_size + 1)
        window_text = " ".join([text for _, text in corpus[start:i+1]])
        window_ngrams = generate_ngrams(window_text, n)
        ngram_freq = Counter(window_ngrams)
        top_10 = ngram_freq.most_common(10)
        results.append((corpus[i][0], top_10))
    return results

def visualize_ngram_trends(ngram_data):
    ngram_dict = {}
    dates = [datetime.fromtimestamp(date) for date, _ in ngram_data]

    for date, top_ngrams in ngram_data:
        for ngram, freq in top_ngrams:
            ngram_str = " ".join(ngram)
            if ngram_str not in ngram_dict:
                ngram_dict[ngram_str] = [0] * len(ngram_data)
            ngram_dict[ngram_str][ngram_data.index((date, top_ngrams))] = freq

    fig = go.Figure()

    for ngram, freqs in ngram_dict.items():
        fig.add_trace(go.Scatter(x=dates, y=freqs, mode='lines', name=ngram))

    fig.update_layout(
        title="Top 10 N-gram Frequencies Over Time",
        xaxis_title="Date",
        yaxis_title="Frequency",
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

    ngram_data = calculate_top_ngrams(corpus, n, window_size)
    visualize_ngram_trends(ngram_data)

if __name__ == "__main__":
    main()
