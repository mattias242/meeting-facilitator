"""Claude AI service for meeting facilitation."""

import os
from typing import Any

from anthropic import Anthropic


class ClaudeService:
    """Service for interacting with Claude API for meeting facilitation."""

    def __init__(self) -> None:
        """Initialize Claude service with API key from environment."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"  # Latest Sonnet model

    def analyze_transcription_for_triggers(
        self,
        transcription: str,
        meeting_context: dict[str, Any],
        transcription_history: list[str],
    ) -> dict[str, Any]:
        """
        Analyze transcription to detect intervention triggers.

        Args:
            transcription: Current chunk transcription
            meeting_context: IDOARRT meeting data (intent, desired_outcomes, etc.)
            transcription_history: Previous chunk transcriptions for context

        Returns:
            dict with detected triggers and suggested interventions
        """
        prompt = self._build_trigger_analysis_prompt(
            transcription, meeting_context, transcription_history
        )

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.3,  # Lower temperature for more focused analysis
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = message.content[0].text if message.content else ""

            # Parse the response
            return self._parse_trigger_response(response_text)

        except Exception as e:
            print(f"Claude API error during trigger analysis: {e}")
            return {"triggers": [], "error": str(e)}

    def generate_facilitation_question(
        self,
        trigger_type: str,
        context: dict[str, Any],
        transcription: str,
    ) -> str:
        """
        Generate a GROW-based coaching question for a detected trigger.

        Args:
            trigger_type: Type of trigger (goal_deviation, perspective_gap, etc.)
            context: Meeting context and trigger details
            transcription: Recent transcription for context

        Returns:
            Facilitation question as a string
        """
        prompt = self._build_facilitation_prompt(trigger_type, context, transcription)

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=256,
                temperature=0.7,  # Higher temperature for creative questions
                messages=[{"role": "user", "content": prompt}],
            )

            question = message.content[0].text.strip() if message.content else ""
            return question

        except Exception as e:
            print(f"Claude API error during question generation: {e}")
            return f"[Fel vid generering av fråga: {str(e)}]"

    def _build_trigger_analysis_prompt(
        self,
        transcription: str,
        meeting_context: dict[str, Any],
        history: list[str],
    ) -> str:
        """Build prompt for trigger analysis."""
        # Format meeting context
        intent = meeting_context.get("intent", "")
        desired_outcomes = meeting_context.get("desired_outcomes", [])
        outcomes_str = "\n".join(f"- {outcome}" for outcome in desired_outcomes)

        # Format history
        history_str = "\n\n".join(
            f"Tidigare chunk {i+1}:\n{chunk}"
            for i, chunk in enumerate(history[-3:])  # Last 3 chunks for context
        )

        return f"""Du är en AI-mötesassistent som analyserar mötestranskriptioner för att identifiera när facilitering behövs.

MÖTETS KONTEXT:
Intent: {intent}

Önskade utfall:
{outcomes_str}

TIDIGARE TRANSKRIPTIONER:
{history_str if history_str else "Ingen tidigare kontext"}

NUVARANDE TRANSKRIPTION:
{transcription}

ANALYS-UPPGIFT:
Analysera den nuvarande transkriptionen och identifiera om någon av följande triggers förekommer:

1. **goal_deviation**: Diskussionen avviker från mötets intent eller önskade utfall
2. **perspective_gap**: Bara 1-2 personer pratar, andra perspektiv saknas
3. **complexity_mistake**: Gruppen behandlar enkla frågor som komplexa eller vice versa

SVARSFORMAT (JSON):
{{
  "triggers": [
    {{
      "type": "goal_deviation" | "perspective_gap" | "complexity_mistake",
      "confidence": 0.0-1.0,
      "reason": "Kortförklaring varför denna trigger detekterades"
    }}
  ]
}}

Om inga triggers detekteras, returnera: {{"triggers": []}}

Svara ENDAST med JSON, ingen annan text."""

    def _build_facilitation_prompt(
        self,
        trigger_type: str,
        context: dict[str, Any],
        transcription: str,
    ) -> str:
        """Build prompt for facilitation question generation."""
        intent = context.get("intent", "")
        reason = context.get("reason", "")

        trigger_descriptions = {
            "goal_deviation": "Diskussionen har avvikit från mötets mål",
            "perspective_gap": "Bara ett fåtal personer pratar",
            "complexity_mistake": "Gruppen behandlar frågan med fel komplexitetsnivå",
        }

        trigger_desc = trigger_descriptions.get(
            trigger_type, "En intervention behövs"
        )

        return f"""Du är en AI-mötesassistent som använder GROW-coachingmodellen för att facilitera möten.

MÖTETS INTENT: {intent}

SITUATION: {trigger_desc}
ANLEDNING: {reason}

SENASTE TRANSKRIPTION:
{transcription[-500:]}  # Last 500 chars for context

GROW-MODELLEN:
- **G**oal: Var vill vi komma?
- **R**eality: Var är vi nu?
- **O**ptions: Vilka alternativ har vi?
- **W**ill: Vad gör vi härnäst?

UPPGIFT:
Generera EN kraftfull, öppen fråga (på svenska) som:
1. Är baserad på GROW-modellen
2. Hjälper gruppen att återkoppla till mötets intent
3. Öppnar upp för nya perspektiv
4. Är kort och tydlig (max 20 ord)

Exempel på bra frågor:
- "Hur relaterar detta till vårt mål om X?"
- "Vilka andra perspektiv skulle vi behöva höra?"
- "Om vi tänker enkelt - vad är själva kärnan i detta?"
- "Var är vi nu i förhållande till vårt önskade utfall?"

Svara ENDAST med frågan, ingen förklaring."""

    def _parse_trigger_response(self, response: str) -> dict[str, Any]:
        """Parse Claude's trigger analysis response."""
        import json

        try:
            # Try to extract JSON from response
            # Sometimes Claude adds extra text, so find the JSON part
            json_start = response.find("{")
            json_end = response.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                return data

            # Fallback if no JSON found
            return {"triggers": [], "error": "Could not parse JSON response"}

        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"Response was: {response}")
            return {"triggers": [], "error": f"JSON parse error: {str(e)}"}


# Global instance
_claude_service: ClaudeService | None = None


def get_claude_service() -> ClaudeService:
    """Get or create global Claude service instance."""
    global _claude_service
    if _claude_service is None:
        _claude_service = ClaudeService()
    return _claude_service
