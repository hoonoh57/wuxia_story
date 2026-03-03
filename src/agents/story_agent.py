"""
Story Agent (L2) - Episode structure using 15-beat narrative framework

Responsibilities:
- Create 15-beat episode structure
- Plan scene sequences with timing
- Design emotional arc and pacing
- Map character arcs across beats

Input: World setting and character profiles (Step 2)
Output: 15-beat structure, scene list, emotional curve (Step 3)
Default Mode: B (Auto) possible
"""

import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

EPISODE_STRUCTURE_PROMPT = """
당신은 무협 드라마의 에피소드 구조 설계 전문가입니다.
15비트 서사 프레임워크를 사용하여 에피소드를 구성합니다.

## 세계관/캐릭터 정보
{world_setting}

## 15비트 프레임워크
1. 일상(Status Quo) - 관객에게 세계를 보여줌
2. 사건 발생(Inciting Incident) - 균형을 깨뜨리는 사건
3. 상승 1(Rising Action 1) - 첫 번째 긴장 고조
4. 중반 위기(Midpoint Crisis) - 큰 반전
5. 상승 2(Rising Action 2) - 두 번째 긴장 고조
6. 복잡화 1(Complication 1) - 새로운 장애물
7. 복잡화 2(Complication 2) - 압박 증가
8. 복잡화 3(Complication 3) - 정점의 복잡성
9. 암흑의 순간(Dark Moment) - 최저점
10. 회복(Recovery) - 영웅의 부활
11. 클라이막스 준비(Climax Setup) - 최종 대결 준비
12. 클라이막스(Climax) - 최고 긴장
13. 해결(Resolution) - 승패 결정
14. 여파(Aftermath) - 감정적 정리
15. 새로운 일상(New Status Quo) - 변화된 세계

## 출력 형식 (반드시 이 JSON 구조를 따르세요)
{{
  "episode_title": "에피소드 제목",
  "episode_subtitle": "부제",
  "total_duration_minutes": 3,
  "beats": [
    {{
      "beat_number": 1,
      "beat_name": "일상",
      "description": "이 비트에서 일어나는 일",
      "primary_characters": ["캐릭터A"],
      "location": "장소",
      "duration_seconds": 12,
      "emotional_intensity": 3
    }}
  ],
  "scenes": [
    {{
      "scene_number": 1,
      "beat_numbers": [1],
      "location": "장소",
      "characters": ["캐릭터A", "캐릭터B"],
      "duration_seconds": 12,
      "purpose": "이 씬의 목적",
      "emotional_tone": "분위기",
      "key_action": "핵심 액션/이벤트"
    }}
  ],
  "pacing": {{
    "exposition_percent": 15,
    "rising_tension_percent": 40,
    "climax_percent": 30,
    "resolution_percent": 15
  }},
  "emotional_curve": [
    {{"beat": 1, "intensity": 3, "emotion": "평온"}},
    {{"beat": 2, "intensity": 7, "emotion": "충격"}}
  ]
}}
"""


class StoryAgent:
    """Agent responsible for story structure and episode organization"""

    def __init__(self, gemini_client):
        self.gemini_client = gemini_client
        self.name = "StoryAgent"

    def generate_structure(self, world_setting: str, system_prompt: str = "") -> Dict[str, Any]:
        """
        Generate episode structure using 15-beat framework.

        Args:
            world_setting: World setting and characters from Step 2
            system_prompt: System prompt from skill loader

        Returns:
            Episode structure dictionary
        """
        logger.info("StoryAgent: Generating 15-beat episode structure...")

        prompt = EPISODE_STRUCTURE_PROMPT.format(world_setting=world_setting)

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
