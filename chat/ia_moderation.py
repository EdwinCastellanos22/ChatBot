import re
from ollama import chat

blacklist = [
    "idiota", "estupido", "estupida", "imbecil", 
    "bomba", "veneno", "asesinar", "morite", "sexo", "polla",
    "tetas"
]

def message_moderate(message: str) -> bool:
    mensaje_min = message.lower()
    for word in blacklist:
        if re.search(r'\b' + re.escape(word) + r'\b', mensaje_min):
            print(f"Bloqueado por Blacklist: {word}")
            return True
    
    prompt = """Eres un moderador estricto.
    REGLAS:
    - Insultos o agresividad -> UNSAFE S2
    - Violencia -> UNSAFE S1
    - Mensaje normal/educado -> SAFE
    Responde SOLO la palabra del código."""

    try:
        response = chat(
            model='llama3.2:1b',
            messages=[
                {'role': 'system', 'content': prompt},
                {'role': 'user', 'content': message}
            ],
            options={
                'temperature': 0,
                'num_predict': 5,
                'top_k': 40,
                'top_p': 0.9,
                'repeat_last_n': 64,
                'repeat_penalty': 1.18,
            }
        )
        
        content = response.message.content.strip().upper()
        
        if "UNSAFE" in content:
            print(f"Bloqueado por IA: {content}")
            return True
            
    except Exception as e:
        print(f"Error en Ollama: {e}")
        return False 
    
    return False