import requests , os

from dotenv import load_dotenv
load_dotenv()

url = os.getenv("IA_URL")
token = os.getenv("IA_TOKEN")

headers = {
    "Authorization": f"Bearer {token}"
}


def message_moderate(message: str) -> bool:
    payload = {
        "inputs": message
    }
    
    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=10
    )
    
    response.raise_for_status()
    data = response.json()[0]
    
    for l in data:
        if l['label'] in ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate', 'hate'] :
            if l['score'] > 0.6:
                return True
    return False