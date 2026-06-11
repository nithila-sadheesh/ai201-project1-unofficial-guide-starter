import os
from groq import Groq
from dotenv import load_dotenv
from retrieve import retrieve

load_dotenv()

GROQ_MODEL = "llama-3.3-70b-versatile"
FALLBACK = "The sources I have don't directly answer that. Try rephrasing your question or asking something more specific."

_SYSTEM_PROMPT = f"""You are a helpful guide answering questions about student life at UC Berkeley.
You answer based solely on the context provided, which comes from Reddit threads, student blogs, and campus newspaper articles written by Berkeley students.

Rules:
- Use ONLY information explicitly stated in the provided context. Do not use any general knowledge.
- If the context does not contain a direct, specific answer to the question, respond with exactly: "{FALLBACK}"
- Do not guess, infer beyond what is stated, or fill gaps with outside knowledge.
- Keep answers concise.
- After any claim you draw from the context, cite the source name in square brackets immediately, e.g. [reddit_eecs]. Do not cite source names that are not in the provided context.
- If multiple sources agree, you may briefly synthesize them."""


_EXPAND_PROMPT = (
    "Rewrite the following question to be more specific and descriptive for searching "
    "a UC Berkeley student advice database. Include 'Berkeley' and relevant context words. "
    "Return only the rewritten question, nothing else."
)


def _expand_query(query):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": _EXPAND_PROMPT},
            {"role": "user", "content": query},
        ],
        temperature=0.0,
        max_tokens=80,
    )
    return response.choices[0].message.content.strip()


def _build_context(chunks):
    parts = []
    for chunk in chunks:
        parts.append(f"[{chunk['source_name']}]\n{chunk['text']}")
    return "\n\n".join(parts)


def generate(query, k=5):
    expanded = _expand_query(query)
    chunks = retrieve(expanded, k=k)

    if not chunks:
        return FALLBACK

    context = _build_context(chunks)
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
        ],
        temperature=0.1,
    )

    return response.choices[0].message.content.strip()


if __name__ == "__main__":
    TEST_QUERIES = [
        "If studying EECS, how many technical classes is it recommended to take each semester?",
        "What is Berkeleytime and by how many minutes do Berkeley classes actually start after their listed time?",
        "How early should students schedule a same-day CAPS counseling appointment to guarantee they are seen?",
        "What specific locations near Berkeley campus do students warn to avoid walking through late at night?",
        "When cramming for Berkeley finals, which part of the semester's content should students prioritize reviewing first, and why?",
    ]

    for query in TEST_QUERIES:
        print(f"\nQ: {query}")
        print("-" * 70)
        print(generate(query))
        print()
