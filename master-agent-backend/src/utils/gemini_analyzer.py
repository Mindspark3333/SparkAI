import os
import google.generativeai as genai
from typing import Dict, Any, List


class GeminiAnalyzer:
    """
    Wrapper around Google Gemini (Generative AI) for analyzing extracted content.
    Provides summarization, sentiment, key points, and categorization.
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY environment variable not set")
        genai.configure(api_key=api_key)

        # Load a default model
        self.model = genai.GenerativeModel("gemini-pro")

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Send text to Gemini for analysis.
        Returns structured dict with summary, key points, sentiment, etc.
        """
        prompt = f"""
        You are an AI research assistant. Analyze the following text and provide results in JSON format.

        Text:
        {text[:4000]}  # Truncate to avoid token overflow

        Return JSON with these fields:
        - content_summary: a concise 3-5 sentence summary
        - key_points: a list of 5-7 bullet points
        - sentiment: overall sentiment (positive, neutral, negative)
        - category: primary category/topic
        - importance_score: integer 1-100 (higher = more important)
        - tags: a list of relevant keywords
        """

        try:
            response = self.model.generate_content(prompt)
            # Try parsing as JSON (Gemini usually returns JSON-like output)
            text_out = response.text.strip()
            if text_out.startswith("```"):
                # Strip code fences if present
                text_out = text_out.split("```")[1]
                if text_out.startswith("json"):
                    text_out = text_out[len("json"):].strip()
            import json
            return json.loads(text_out)
        except Exception as e:
            raise RuntimeError(f"Gemini analysis failed: {e}")

    def analyze_url_content(self, extracted: Dict[str, Any]) -> Dict[str, Any]:
        """
        Given extracted dict {title, raw_text, description}, return analysis enriched with metadata.
        """
        raw_text = extracted.get("raw_text") or ""
        if not raw_text.strip():
            return {
                "content_summary": None,
                "key_points": [],
                "sentiment": None,
                "category": None,
                "importance_score": None,
                "tags": [],
            }

        analysis = self.analyze_text(raw_text)
        return {**extracted, **analysis}