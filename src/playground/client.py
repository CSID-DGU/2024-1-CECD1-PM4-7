

def send_request(client, conversation_history, user_input: str, MODEL="gpt-4o-mini"):
    conversation_history.append({
        "role": "user",
        "content": user_input
    })

    response = client.chat.completions.create(
        model=MODEL,
        messages=conversation_history,
        temperature=0.0,
        max_tokens=256,
        top_p=0.0,
        frequency_penalty=0,
        presence_penalty=0
    )

    assistant_response = response.choices[0].message.content

    conversation_history.append({
        "role": "assistant",
        "content": assistant_response
    })
    return assistant_response
