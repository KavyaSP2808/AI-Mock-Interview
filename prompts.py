# prompts.py

QUESTION_PROMPT = """
You are a professional interviewer for a {role} position.
Previous conversation (Q&A pairs):
{history}

Generate ONLY the next interview question (no extra text, no numbering, no commentary).
Make it realistic, relevant to the role, and increase difficulty slightly.
If no history, start with a warm-up question about their background.
"""

FEEDBACK_PROMPT = """
Question: {question}
User's answer: {answer}

Provide concise feedback (2-3 short lines) in this exact format:

Clarity: (how clear and structured the answer is)
Relevance: (how well it addresses the question)
Completeness: (what key points are missing, if any)

Keep it encouraging but specific. Do not write extra introduction or conclusion.
"""

SUMMARY_PROMPT = """
You interviewed a candidate for the role of {role}.
Here is the full interview log (question, answer, feedback per exchange):
{full_log}

Write a final summary in 3 paragraphs:
1. Two strongest aspects of their performance (with examples from their answers).
2. Two specific areas for improvement (with actionable suggestions).
3. One overall encouragement and a concrete next step to prepare further.

Keep it professional, supportive, and no longer than 250 words.
"""