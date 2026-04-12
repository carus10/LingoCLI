import requests
import json

url = 'http://localhost:1234/v1/chat/completions'
headers = {'Content-Type': 'application/json'}
data = {
    'model': 'local-model',
    'messages': [
        {'role': 'system', 'content': 'Sen bir Windows Terminal yapay zekasısın. SADECE type ve content değerlerini içeren bir JSON objesi döndür. Markdown veya ekstra açıklama kullanma.'},
        {'role': 'user', 'content': 'merhaba'}
    ],
    'temperature': 0.1
}

try:
    response = requests.post(url, headers=headers, json=data)
    print('RAW RESPONSE:')
    print(response.text)
except Exception as e:
    print('Error:', e)
