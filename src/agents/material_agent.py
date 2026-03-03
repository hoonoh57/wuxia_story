"""
Material Agent (L0) - Story material selection and analysis

Responsibilities:
- Analyze material concepts for story potential
- Create material briefs with logline, conflict, audience, hooks
- Score materials on creative/market/feasibility dimensions

Input: User concept or trend data
Output: Material Selection Brief (JSON)
Default Mode: A (Human Relay) or C (Mixed)
"""

import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

MATERIAL_PROMPT_TEMPLATE = """
당신은 무협 웹소설/마이크로드라마의 소재 분석 전문가입니다.

다음 소재 개념을 분석하여, 아래 JSON 형식으로 소재 선정 브리프를 작성하세요.

## 소재 개념
{concept}

## 출력 형식 (반드시 이 JSON 구조를 따르세요)
{{
  "selected_material": {{
    "title": "소재 제목",
    "source": "원천 또는 컨셉 출처",
    "selection_rationale": "이 소재를 선정한 이유"
  }},
  "logline": "한 문장으로 독자를 끌어당기는 스토리 요약",
  "core_conflict": {{
    "protagonist": "주인공 (누구인가)",
    "antagonist": "대립 세력 (무엇과 싸우는가)",
    "central_conflict": "핵심 갈등",
    "stakes": "승패에 걸린 것"
  }},
  "target_audience": {{
    "primary_demographic": "주 타겟 (연령, 성별, 관심사)",
    "geographic_markets": ["한국", "중국", "글로벌"],
    "psychographic_profile": "타겟의 심리적 특성",
    "consumption_platform": "소비 플랫폼 (유튜브 숏폼 등)"
  }},
  "psychological_hooks": [
    {{
      "hook": "심리 훅 이름",
      "human_motivation": "인간이 반응하는 이유",
      "audience_resonance": "타겟 독자와의 공명점"
    }}
  ],
  "viability_assessment": {{
    "creative_potential": 8,
    "market_potential": 7,
    "production_feasibility": 9,
    "risk_factors": ["리스크1"],
    "opportunity_factors": ["기회1"],
    "recommendation": "Yes"
  }}
}}
"""


class MaterialAgent:
    """Agent responsible for material selection and analysis"""

    def __init__(self, gemini_client):
        self.gemini_client = gemini_client
        self.name = "MaterialAgent"

    def select_material(self, concept: str, system_prompt: str = "") -> Dict[str, Any]:
        """
        Analyze a concept and generate a material selection brief.

        Args:
            concept: Story concept or material idea
            system_prompt: System prompt from skill loader

        Returns:
            Material brief dictionary
        """
        logger.info("MaterialAgent: Analyzing concept...")

        prompt = MATERIAL_PROMPT_TEMPLATE.format(concept=concept)

        if self.gemini_client and self.gemini_client.is_available():
            response = self.gemini_client.generate(
                prompt=prompt,
                system_prompt=system_prompt or None,
            )

            if response["success"]:
                return self._parse_response(response["text"])
            else:
                logger.error(f"Gemini generation failed: {response.get('error')}")
                return {"status": "error", "error": response.get("error", "")}

        # Fallback: return prompt for human relay
        return {
            "status": "awaiting_human",
            "prompt": prompt,
            "agent": self.name,
        }

    def _parse_response(self, text: str) -> Dict[str, Any]:
        """Parse Gemini response, extracting JSON if present."""
        try:
            # Handle markdown code blocks
            if "```json" in text:
                start = text.index("```json") + 7
                end = text.index("```", start)
                text = text[start:end].strip()
            elif "```" in text:
                start = text.index("```") + 3
                end = text.index("```", start)
                text = text[start:end].strip()

            return json.loads(text)
        except (json.JSONDecodeError, ValueError):
            logger.warning("Could not parse JSON from response, returning raw text")
            return {
                "status": "raw",
                "content": text,
                "agent": self.name,
            }
