# upload pdf: /path/file.pdf

import os
from google import genai
from google.genai import types


def chat_with_bot():
    client = genai.Client(
        api_key="YOUR_API_KEY_HERE",
    )

    model = "gemini-2.5-flash-preview-04-17"

    conversation_history = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text="""You are a smart and supportive university assistant designed to help students with questions about their courses.
Objectives:
Help students understand course content, deadlines, grading, and assignments.
If a syllabus or file is uploaded, extract relevant information to answer the student's question.
Keep memory of the student’s previous questions in the same session to offer helpful, context-aware responses.
Behavior:
Respond in a friendly, professional, and student-friendly tone.
Be clear and concise.
When referencing a file, use its content to inform your response.
If unsure, ask a clarifying question.
Always end with: “Would you like help with anything else?”
Example student questions:
What are the core topics in my AI course?
When is the final project due?
How is the course graded?
Can you summarize the lecture notes I uploaded?
First message:
Hi! I’m your course assistant. You can ask me anything about your class or upload your syllabus. How can I help you today?""")],
        ),
        types.Content(
            role="model",
            parts=[types.Part.from_text(text="""Hi! I’m your course assistant. You can ask me anything about your class or upload your syllabus. How can I help you today?""")],
        ),
    ]

    while True:
        user_input = input("\nYou: ")

        # End chat if user wants
        if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
            print("Assistant: Goodbye! 😊")
            break

        # Upload a PDF
        if user_input.lower().startswith("upload pdf:"):
            file_path = user_input[len("upload pdf:"):].strip()
            if os.path.exists(file_path):
                file = client.files.upload(file=file_path)
                conversation_history.append(
                    types.Content(
                        role="user",
                        parts=[types.Part.from_uri(file_uri=file.uri, mime_type=file.mime_type)],
                    )
                )
                print("Uploading PDF...")
            else:
                print(f"File {file_path} not found.")
                continue

        else:
            conversation_history.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=user_input)],
                )
            )

        tools = [
            types.Tool(google_search=types.GoogleSearch()),
        ]

        generate_content_config = types.GenerateContentConfig(
            temperature=0,
            tools=tools,
            response_mime_type="text/plain",
        )

        # NEW FIXED: collect all stream chunks, print once
        response_text = ""

        for chunk in client.models.generate_content_stream(
            model=model,
            contents=conversation_history,
            config=generate_content_config,
        ):
            response_text += chunk.text

        print(f"\nBot: {response_text}")

        conversation_history.append(
            types.Content(
                role="model",
                parts=[types.Part.from_text(text=response_text)],
            )
        )


if __name__ == "__main__":
    print("Bot: Hi! I’m your course assistant. You can ask me anything about your class or upload your syllabus. How can I help you today?")
    chat_with_bot()
