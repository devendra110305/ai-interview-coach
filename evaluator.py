import os
from dotenv import load_dotenv
from groq import Groq

# Load the .env file
load_dotenv()

# Fetch the API key securely from the environment variable
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def evaluate_answer(question, answer):

    prompt = f"""
You are a Senior Technical Interviewer.

Interview Question:
{question}

Candidate Answer:
{answer}

Evaluate the answer and provide:

1. Technical Score (out of 10)
2. Communication Score (out of 10)
3. Strengths
4. Weaknesses
5. Missing Concepts
6. Improved Answer
7. Final Recommendation

Provide detailed feedback.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": """
You are an expert interviewer specializing in:

- Python
- SQL
- Machine Learning
- Deep Learning
- NLP
- Generative AI
- RAG
- LangChain

Provide professional interview feedback.
"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_tokens=1500
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    print("=" * 70)
    print("INTERVIEW ANSWER EVALUATOR")
    print("=" * 70)

    question = input("\nEnter Interview Question:\n\n")
    answer = input("\nEnter Candidate Answer:\n\n")

    result = evaluate_answer(question, answer)

    print("\n")
    print("=" * 70)
    print("INTERVIEW EVALUATION REPORT")
    print("=" * 70)
    print(result)