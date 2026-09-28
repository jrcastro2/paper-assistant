import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from environment

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "What are the main metadata fields used to describe a scientific paper?",
        }
    ],
)

print(response.content[0].text)
