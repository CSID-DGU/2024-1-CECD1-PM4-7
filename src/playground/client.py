
# 대화모델용 - 지속적으로 대화맥락을 유지해야할 때 사용
def send_request_with_history(client, conversation_history, user_input: str, MODEL="gpt-4o-mini"):
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


# 일반 질답용 - 대화맥락이 필요없는 경우 사용함
def send_request_without_history(client, prompt, user_input: str, MODEL="gpt-4o-mini"):
    conversation_history = [
        {
            "role": "system",
            "content": prompt
        },
        {
            "role": "user",
            "content": user_input
        }
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=conversation_history,
        temperature=0.0,
        max_tokens=256,
        top_p=0.0,
        frequency_penalty=0,
        presence_penalty=0
    )

    return response.choices[0].message.content