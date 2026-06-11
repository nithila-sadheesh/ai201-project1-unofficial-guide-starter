import gradio as gr
from generate import generate

TITLE = "The Unofficial Berkeley Guide"
DESCRIPTION = "Student-sourced advice for surviving UC Berkeley"

EXAMPLES = [
    "How many technical classes should EECS students take each semester?",
    "What is Berkeleytime and how does it affect class start times?",
    "How early should I schedule a same-day CAPS appointment?",
    "What areas near campus should I avoid late at night?",
    "When cramming for finals, what content should I review first?",
]

CSS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap');

* { font-family: 'DM Sans', sans-serif !important; }

:root {
    --body-background-fill: #EBF4FF !important;
    --background-fill-primary: #EBF4FF !important;
    --background-fill-secondary: #EBF4FF !important;
}

body, html, .main, footer,
.gradio-app, gradio-app, .app, .wrap, .contain, .svelte-1ipelgc {
    background: #EBF4FF !important;
    background-color: #EBF4FF !important;
    min-height: 100vh;
}

.gradio-container {
    background: #EBF4FF !important;
    max-width: 820px !important;
    margin: 0 auto !important;
    padding: 24px !important;
}

#title, #title *, #title h1, #title h2, #title p {
    text-align: center !important;
    color: #000000 !important;
    margin-bottom: 4px;
}

#subtitle, #subtitle *, #subtitle p {
    text-align: center !important;
    color: #000000 !important;
    margin-top: 0;
    margin-bottom: 20px;
}

#chatbot {
    border-radius: 20px !important;
    border: 1.5px solid #BBDEFB !important;
    background: white !important;
    box-shadow: 0 2px 12px rgba(0, 50, 98, 0.07) !important;
}

#msg-box textarea {
    border-radius: 24px !important;
    border: 1.5px solid #BBDEFB !important;
    padding: 10px 18px !important;
    background: white !important;
    color: #000000 !important;
    resize: none !important;
    font-size: 0.95em !important;
}

#msg-box textarea:focus {
    border-color: #64B5F6 !important;
    box-shadow: 0 0 0 3px rgba(100, 181, 246, 0.2) !important;
    outline: none !important;
}

#send-btn {
    background: #FDB515 !important;
    color: #003262 !important;
    border-radius: 24px !important;
    border: none !important;
    font-weight: 600 !important;
    font-size: 0.95em !important;
}

#send-btn:hover {
    background: #e8a50e !important;
    box-shadow: 0 2px 8px rgba(253, 181, 21, 0.4) !important;
}

#examples-label {
    text-align: center;
    color: #7a9ab5;
    font-size: 0.85em;
    margin-top: 16px;
    margin-bottom: 6px;
}

.example-btn {
    background: white !important;
    border: 1.5px solid #BBDEFB !important;
    border-radius: 20px !important;
    color: #003262 !important;
    font-size: 0.82em !important;
    padding: 8px 14px !important;
    white-space: normal !important;
    height: auto !important;
    line-height: 1.4 !important;
    transition: all 0.15s ease !important;
    box-shadow: 0 1px 4px rgba(0, 50, 98, 0.06) !important;
}

.example-btn:hover {
    background: #E3F2FD !important;
    border-color: #64B5F6 !important;
    box-shadow: 0 2px 8px rgba(100, 181, 246, 0.25) !important;
}
"""


def chat(message, history):
    if not message.strip():
        return "", history
    answer = generate(message)
    history = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": answer},
    ]
    return "", history


def make_example_handler(example):
    def handler(history):
        answer = generate(example)
        return history + [
            {"role": "user", "content": example},
            {"role": "assistant", "content": answer},
        ]
    return handler


with gr.Blocks(css=CSS, title=TITLE) as demo:
    gr.Markdown(f"# {TITLE}", elem_id="title")
    gr.Markdown(DESCRIPTION, elem_id="subtitle")

    chatbot = gr.Chatbot(
        elem_id="chatbot",
        height=440,
        label="",
    )

    with gr.Row():
        msg = gr.Textbox(
            elem_id="msg-box",
            placeholder="Ask anything about student life at Berkeley...",
            label="",
            scale=8,
            container=False,
        )
        send = gr.Button("Ask →", elem_id="send-btn", scale=1, min_width=80)

    gr.Markdown("*Try asking:*", elem_id="examples-label")

    with gr.Row():
        btn1 = gr.Button(EXAMPLES[0], elem_classes="example-btn")
        btn2 = gr.Button(EXAMPLES[1], elem_classes="example-btn")
        btn3 = gr.Button(EXAMPLES[2], elem_classes="example-btn")

    with gr.Row():
        btn4 = gr.Button(EXAMPLES[3], elem_classes="example-btn")
        btn5 = gr.Button(EXAMPLES[4], elem_classes="example-btn")

    send.click(chat, [msg, chatbot], [msg, chatbot])
    msg.submit(chat, [msg, chatbot], [msg, chatbot])

    for btn, ex in zip([btn1, btn2, btn3, btn4, btn5], EXAMPLES):
        btn.click(fn=make_example_handler(ex), inputs=[chatbot], outputs=[chatbot])

if __name__ == "__main__":
    demo.launch()
