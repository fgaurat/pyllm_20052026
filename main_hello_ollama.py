import requests
from ollama import chat
from ollama import ChatResponse

def main():
    response: ChatResponse = chat(model='mistral', messages=[
    {
        'role': 'user',
        'content': 'Why is the sky blue?',
    },
    ])
    print(response['message']['content'])
    # or access fields directly from the response object
    print(response.message.content)


def oldmain():
    response = requests.post('http://localhost:11434/v1/chat/completions',
        json={
            'model': 'mistral',
            'messages': [
                {'role': 'system', 'content': 'Tu es enfin connaisseur du guide du voyageur intergalactique.'},
                {'role': 'user', 'content': 'Parle moi du sens de la vie.'},
            ],
        })
    print(response.json())

if __name__=='__main__':
    main()
