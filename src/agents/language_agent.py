"""
Language Agent (L3) - Writing style, dialogue, and emotional expression

Responsibilities:
- Generate narrative prose with consistent writing style
- Create character-specific dialogue with subtext
- Add sensory details and emotional cues
- Refine action descriptions

Input: Scene structure (Step 3) + World/character context (Step 2)
Output: Full scene text with dialogue, emotions, actions (Step 4)
Default Mode: C (Mixed)
"""

import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

SCENE_TEXT_PROMPT = """
당신은 무협 소설 전문 작가입니다.
날카로운 문체(전투/긴장), 서정적 문체(풍경/감정), 감각적 문체(오감 묘사)를 자유자재로 구사합니다.

아래 씬 구조와 세계관 정보를 바탕으로, 각 씬의 완성된 서술 텍스트를 작성하세요.

## 씬 구조 (비트/씬 리스트)
{scene_structure}

## 세계관/캐릭터 정보
{world_context}

## 작성 규칙
1. 대사는 캐릭터 성격에 맞는 고유한 말투를 사용할 것
2. 무협 한자어를 적절히 사용하되 과하지 않게
3. 오감 묘사를 반드시 포함 (최소 3개 감각)
4. 내면 독백으로 캐릭터 심리를 드러낼 것
5. 액션 씬은 속도감 있는 짧은 문장 사용
6. 감정 씬은 서정적이고 긴 문장 사용

## 출력 형식 (반드시 이 JSON 구조를 따르세요)
{{
  "scenes": [
    {{
      "scene_number": 1,
      "title": "씬 소제목",
      "narrative": "완성된 서술 텍스트 (500~1500자). 묘사, 감정, 분위기를 모두 포함.",
      "dialogue": [
        {{
          "character": "캐릭터명",
          "line": "실제 대사",
          "direction": "연기/감정 지시 (예: 이를 악물며, 쓸쓸한 미소)",
          "subtext": "대사 이면의 진짜 의미"
        }}
      ],
      "action_choreography": "액션/동작 상세 묘사 (무술 장면이 있을 경우)",
      "sensory_details": {{
        "visual": "시각 묘사",
        "auditory": "청각 묘사",
        "tactile": "촉각 묘사",
        "olfactory": "후각 묘사 (있을 경우)",
        "gustatory": "미각 묘사 (있을 경우)"
      }},
      "emotional_markers": {{
        "dominant_emotion": "주요 감정",
        "intensity": 7,
        "transition": "감정의 변화 방향"
      }},
      "internal_monologue": "주인공 내면 독백 (있을 경우)",
      "writing_style": "이 씬에 사용된 문체 (날카로운/서정적/감각적)"
    }}
  ],
  "continuity_notes": [
    "다음 에피소드를 위한 복선/연속성 메모"
  ]
}}
"""


class LanguageAgent:
    """Agent responsible for writing style, dialogue, and emotional expression"""

    def __init__(self, gemini_client):
        self.gemini_client = gemini_client
        self.name = "LanguageAgent"

    def generate_scene_text(
        self, scene_structure: str, world_context: str, system_prompt: str = ""
    ) -> Dict[str, Any]:
        """
        Generate full narrative text, dialogue, and emotional cues for scenes.

        Args:
            scene_structure: Episode structure from Step 3 (JSON string)
            world_context: World/character info from Step 2 (JSON string)
            system_prompt: System prompt from skill loader

        Returns:
            Scenes with full text, dialogue, sensory details
        """
        logger.info("LanguageAgent: Generating scene text and dialogue...")

        prompt = SCENE_TEXT_PROMPT.format(
            scene_structure=scene_structure,
            world_context=world_context,
        )

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

        return {"status": "awaiting_human", "prompt": prompt, "agent": self.name}

    def _parse_response(self, text: str) -> Dict[str, Any]:
        """Parse Gemini response, extracting JSON if present."""
        try:
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
            return {"status": "raw", "content": text, "agent": self.name}
