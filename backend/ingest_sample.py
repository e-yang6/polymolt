import requests
import json

# Configuration
API_URL = "http://localhost:8000/ai/ingest"

# Sample Toronto location reviews and data
SAMPLES = [
    {
        "texts": [
            "Little Tykes Nursery in North York received glowing reviews for its new outdoor play area, though some parents noted a 10% increase in monthly fees.",
            "The Royal Ontario Museum's new interactive exhibit has been rated 4.5/5 by weekend visitors, significantly improving the attraction's overall appeal."
        ],
        "ids": ["review_littletykes_nursery", "review_rom_exhibit"],
        "collection_name": "rag"
    }
]

def ingest_samples():
    print(f"Connecting to {API_URL}...")
    for entry in SAMPLES:
        try:
            response = requests.post(API_URL, json=entry)
            if response.status_code == 200:
                print(f"Success: {response.json()['message']}")
            else:
                print(f"Failed ({response.status_code}): {response.text}")
        except requests.exceptions.ConnectionError:
            print("Error: Could not connect to the backend server. Make sure it's running at http://localhost:8000")
            break

if __name__ == "__main__":
    ingest_samples()
