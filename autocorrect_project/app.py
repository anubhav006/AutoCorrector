from flask import Flask, render_template, request, jsonify
import re
from collections import Counter

app = Flask(__name__)

# --- Global Storage (In-memory for simplicity) ---
MODEL_DATA = {
    "vocab": set(),
    "word_probs": {},
    "is_trained": False
}

# --- NLP Logic (Peter Norvig's Approach) ---
def words(text): 
    return re.findall(r'\w+', text.lower())

def train(features):
    # Count frequency of every word
    model = Counter(features)
    total_count = sum(model.values())
    # Calculate probability for each word
    probs = {word: count/total_count for word, count in model.items()}
    return set(features), probs

def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word): 
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))

def check_corrections(word):
    "Generate best candidates."
    vocab = MODEL_DATA["vocab"]
    probs = MODEL_DATA["word_probs"]
    
    # 1. Exact match
    if word in vocab:
        return [(word, 1.0)]
    
    # 2. Distance 1
    candidates = list(edits1(word).intersection(vocab))
    
    # 3. Distance 2 (if no distance 1 found)
    if not candidates:
        candidates = list(edits2(word).intersection(vocab))
    
    # 4. Return word itself if no corrections found
    if not candidates:
        return [(word, 0.0)]

    # Sort candidates by probability
    ranked = sorted([(c, probs.get(c, 0)) for c in candidates], key=lambda x: x[1], reverse=True)
    return ranked[:3] # Return top 3

# --- Routes ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file uploaded"}), 400
    
    try:
        text_data = file.read().decode('utf-8')
        vocab, probs = train(words(text_data))
        
        MODEL_DATA["vocab"] = vocab
        MODEL_DATA["word_probs"] = probs
        MODEL_DATA["is_trained"] = True
        
        return jsonify({"success": True, "vocab_size": len(vocab)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/correct', methods=['POST'])
def correct():
    if not MODEL_DATA["is_trained"]:
        return jsonify({"error": "Model not trained yet"}), 400
        
    data = request.json
    word = data.get('word', '').strip()
    
    if not word:
        return jsonify({"error": "Empty word"}), 400

    suggestions = check_corrections(word.lower())
    
    # Format data for frontend
    response_data = [
        {"word": w, "prob": f"{p:.5f}"} for w, p in suggestions
    ]
    
    return jsonify({"suggestions": response_data})

if __name__ == '__main__':
    app.run(debug=True)