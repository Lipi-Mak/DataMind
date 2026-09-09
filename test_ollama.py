import ollama


response = ollama.chat(
    model="llama3.2:3b",
    messages=[
        {
            "role": "user",
            "content": "Explain what a CSV dataset is in one simple sentence."
        }
    ]
)


print(response["message"]["content"])