import requests
import os

# 1. The URL for the high-accuracy dataset (Peter Norvig's Corpus)
URL = "https://norvig.com/big.txt"
FILE_NAME = "final.txt"

def download_pro_dataset():
    print(f"🚀 Downloading High-Accuracy Dataset from {URL}...")
    
    try:
        # Download the file
        response = requests.get(URL)
        response.raise_for_status()
        data = response.text
        
        # Save it directly as final.txt (Overwriting the old bad file)
        with open(FILE_NAME, "w", encoding="utf-8") as f:
            f.write(data)
            
        print(f"✅ Success! Saved to '{FILE_NAME}'")
        print(f"📊 Dataset Size: {len(data)} characters (Huge!)")
        print("👉 Now run 'python module.py' again to see 90%+ accuracy.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    download_pro_dataset()