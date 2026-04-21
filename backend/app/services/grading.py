import re
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

try:
    import openai
except ImportError:
    openai = None

from ..config import OPENAI_API_KEY


def normalize_text(text: str) -> str:
    text = text.replace('\r', '\n')
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'^(Answer|Correct Answer|Ans|Solution)[:\)\-]*\s*', '', text, flags=re.I)
    text = re.sub(r'^[a-z]\)\s*', '', text, flags=re.I)
    text = re.sub(r'^\d+\s*[\.)]\s*', '', text)
    text = re.sub(r'[\W_]+', ' ', text)
    return text.lower().strip()


def parse_answer_items(text: str) -> List[str]:
    text = text.replace('\r', '\n')
    pattern = re.compile(r'(?:^|\n)\s*(\d{1,3})\s*[\.)]\s*')
    matches = list(pattern.finditer(text))
    if len(matches) < 2:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return [normalize_text(line) for line in lines if line]

    items: List[str] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        item = text[start:end].strip()
        if item:
            items.append(normalize_text(item))
    return items


class GradingEngine:
    def __init__(self):
        if OPENAI_API_KEY and openai:
            openai.api_key = OPENAI_API_KEY

    def _compute_similarity(self, reference: str, response: str) -> float:
        if not reference or not response:
            return 0.0
        vectorizer = TfidfVectorizer(stop_words='english')
        texts = [reference, response]
        matrix = vectorizer.fit_transform(texts).toarray()  # type: ignore[attr-defined]
        if matrix.shape[1] == 0:
            return 0.0
        similarity = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        return float(similarity)

    def _keyword_overlap(self, answer_text: str, student_response: str) -> float:
        if not answer_text or not student_response:
            return 0.0
        answer_tokens = set(re.findall(r"\b[a-z]{3,}\b", answer_text.lower()))
        response_tokens = set(re.findall(r"\b[a-z]{3,}\b", student_response.lower()))
        if not answer_tokens:
            return 0.0
        overlap = len(answer_tokens.intersection(response_tokens))
        return overlap / len(answer_tokens)

    def _sequence_similarity(self, answer_text: str, student_response: str) -> float:
        if not answer_text or not student_response:
            return 0.0
        return SequenceMatcher(None, answer_text, student_response).ratio()

    def _score_question(self, answer_text: str, student_response: str, weight: float) -> float:
        if not answer_text:
            return 0.0
        if answer_text == student_response:
            return weight

        similarity = self._compute_similarity(answer_text, student_response)
        keyword_score = self._keyword_overlap(answer_text, student_response)
        sequence_score = self._sequence_similarity(answer_text, student_response)
        raw = max(similarity, keyword_score, sequence_score)

        if raw >= 0.9:
            return weight
        if raw >= 0.75:
            return round(weight * (0.85 + (raw - 0.75) * 0.75), 2)
        if raw >= 0.5:
            return round(weight * (0.6 + (raw - 0.5) * 0.5), 2)
        if raw >= 0.3:
            return round(weight * (0.35 + raw * 0.4), 2)
        return round(weight * raw * 0.7, 2)

    def _comment_for_question(self, answer_text: str, student_response: str, score: float, weight: float) -> str:
        if score >= weight:
            return 'Excellent answer. Full credit awarded.'
        if score >= weight * 0.75:
            return 'Good answer with minor omissions. Partial credit awarded.'
        if score >= weight * 0.5:
            return 'Some core points are correct, but the response needs more detail.'
        if score >= weight * 0.25:
            return 'Basic concepts are present; add more accuracy and examples to improve.'
        if not student_response:
            return 'No answer provided. The student needs to answer the question fully.'
        return 'The response needs clearer structure and more relevant content.'

    def grade(self, answer_key: str, student_answer: str, weightage: Optional[Dict[int, float]] = None) -> Dict[str, Any]:
        answer_items = parse_answer_items(answer_key)
        student_items = parse_answer_items(student_answer)
        max_score = float(sum(weightage.values()) if weightage else len(answer_items) * 1.0)
        total = 0.0
        details = []

        weight_map = weightage or {}
        for idx, answer in enumerate(answer_items):
            weight = weight_map.get(idx + 1, 1.0)
            response = student_items[idx] if idx < len(student_items) else ''
            score = self._score_question(answer, response, weight)
            details.append({
                'question': idx + 1,
                'answer': answer,
                'response': response,
                'weight': weight,
                'score': round(score, 2),
                'comment': self._comment_for_question(answer, response, score, weight),
            })
            total += score

        feedback = self._generate_feedback(total, max_score)
        return {
            'score': round(total, 2),
            'max_score': round(max_score, 2),
            'feedback': feedback,
            'details': details,
        }

    def _generate_feedback(self, score: float, max_score: float) -> str:
        percentage = (score / max_score) * 100 if max_score else 0
        if percentage >= 90:
            return 'Excellent understanding. Keep up the great work.'
        if percentage >= 70:
            return 'Good performance with a few gaps. Review the missed areas.'
        if percentage >= 50:
            return 'Needs improvement. Revisit the key concepts and answer structure.'
        return 'Significant gaps found. Schedule a detailed review.'

    def llm_inspect(self, question: str, student_response: str) -> str:
        if not openai or not OPENAI_API_KEY:
            return ''
        prompt = (
            'You are a grading assistant. Compare the student answer with the model answer. '
            'Return a concise evaluation with keywords and partial credit suggestions.'
            f'\nModel answer: {question}\nStudent answer: {student_response}\nEvaluation:'
        )
        completion = openai.Completion.create(  # type: ignore[attr-defined]
            engine='text-davinci-003',
            prompt=prompt,
            max_tokens=120,
            temperature=0.3,
        )
        return completion.choices[0].text.strip()
