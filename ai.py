
from openai import OpenAI


API_KEY = open("API_KEY", 'r').read()

client = OpenAI(api_key=API_KEY)

assistant_id = 'asst_kWCxzWFs1Y72zioxSPQB8GhO'

def save_playlist_to_data(c, n):
    vibe = c
    num = int(n)

    content = f"Give me a playlist for a {vibe} with {num} songs"

    get_ai_response(content)
    print('SAVED CONTENT')

def get_ai_response(content):
    assistant = client.beta.assistants.retrieve(assistant_id=assistant_id)

    my_thread = client.beta.threads.create()

    my_thread_message = client.beta.threads.messages.create(
        thread_id=my_thread.id,
        role='user',
        content=content
    )

    my_run = client.beta.threads.runs.create(
        thread_id=my_thread.id,
        assistant_id=assistant.id
    )

    while my_run.status in ["queued", "in_progress"]:
        keep_retrieving_run = client.beta.threads.runs.retrieve(
            thread_id=my_thread.id,
            run_id=my_run.id
        )
        print(f"Run status: {keep_retrieving_run.status}")

        if keep_retrieving_run.status == "completed":
            print("\n")

            all_messages = client.beta.threads.messages.list(
                thread_id=my_thread.id
            )

            print("------------------------------------------------------------ \n")

            print(f"User: {my_thread_message.content[0].text.value}")
            assistant_content = all_messages.data[0].content[0].text.value
            print(f"Assistant: {assistant_content}")

            with open('data.txt', 'w+') as f:
                f.write(assistant_content.strip())

            break
        elif keep_retrieving_run.status == "queued" or keep_retrieving_run.status == "in_progress":
            pass
        else:
            print(f"Run status: {keep_retrieving_run.status}")
            break





