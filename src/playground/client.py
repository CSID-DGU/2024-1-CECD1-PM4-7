

def send_request(client, conversation_history, user_input: str):
    conversation_history.append({
        "role": "user",
        "content": user_input
    })

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation_history,
        temperature=0.1,
        max_tokens=256,
        top_p=0.3,
        frequency_penalty=0,
        presence_penalty=0
    )

    assistant_response = response.choices[0].message.content

    conversation_history.append({
        "role": "assistant",
        "content": assistant_response
    })
    return assistant_response
