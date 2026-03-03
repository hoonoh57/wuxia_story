"""
Narrator Agent (L1) - Transcendent narrative voice and worldbuilding

Responsibilities:
- Design world setting (geography, magic system, social structures)
- Create character profiles (5-layer structure)
- Establish relationship maps
- Generate scene narration with emotional cues

Input: Material brief (Step 1) or Scene structure (Step 3)
Output: World design document (Step 2) or Scene narrative (Step 4)
Default Mode: C (Mixed)
"""

import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

WORLD_DESIGN_PROMPT = """
당신은 무협 세계관 설계 전문가입니다.

아래 소재 브리프를 바탕으로 세계관과 캐릭터를 설계하세요.

## 소재 브리프
{material_brief}

## 출력 형식 (반드시 이 JSON 구조를 따르세요)
{{
  "world_setting": {{
    "name": "세계 이름",
    "era": "시대 배경",
    "geography": "지리적 배경 상세",
    "climate": "기후와 환경",
    "political_structure": "정치/세력 구도",
    "magic_system": "무공/내공 체계 상세",
    "social_hierarchy": "사회 계층 구조",
    "key_locations": [
      {{
        "name": "장소명",
        "description": "장소 설명",
        "significance": "서사적 중요도"
      }}
    ],
    "history": "핵심 역사/전설"
  }},
  "character_profiles": [
    {{
      "layer_1_basic": {{
        "name": "이름",
        "age": "나이",
        "gender": "성별",
        "role": "역할 (주인공/적대자/조력자 등)"
      }},
      "layer_2_psychology": {{
        "personality": "성격 핵심",
        "trauma": "내면의 상처",
        "desire": "가장 원하는 것",
        "fear": "가장 두려워하는 것"
      }},
      "layer_3_abilities": {{
        "martial_arts": "무공/능력",
        "strengths": "강점",
        "weaknesses": "약점",
        "signature_move": "대표기"
      }},
      "layer_4_conflict": {{
        "goal": "목표",
        "obstacle": "장애물",
        "internal_conflict": "내적 갈등",
        "external_conflict": "외적 갈등"
      }},
      "layer_5_arc": {{
        "starting_state": "시작 상태",
        "growth_direction": "성장 방향",
        "potential_ending": "잠재적 결말"
      }}
    }}
  ],
  "relationship_map": [
    {{
      "character_1": "캐릭터A",
      "character_2": "캐릭터B",
      "relationship": "관계 유형",
      "conflict_point": "갈등 지점",
      "dynamic": "관계의 변화 방향"
    }}
  ]
}}
"""

SCENE_NARRATION_PROMPT = """
당신은 무협 소설의 초월적 화자입니다.
벌레의 눈(미시적 디테일), 새의 눈(거시적 조망), 심연의 눈(존재론적 깊이)을 갖추고 있습니다.

아래 씬 구조를 바탕으로 생생한 내러티브를 작성하세요.

## 씬 구조
{scene_structure}

## 세계관/캐릭터 정보
{world_context}

## 출력 형식 (반드시 이 JSON 구조를 따르세요)
{{
  "scenes": [
    {{
      "scene_number": 1,
      "narrative": "씬의 서술 텍스트 (300~1000자)",
      "dialogue": [
        {{
          "character": "캐릭터명",
          "line": "대사",
          "subtext": "숨겨진 감정/의도",
          "tone": "말투/어조"
        }}
      ],
      "action_description": "액션/동작 묘사",
      "sensory_details": "오감 묘사 (시각, 청각, 촉각, 후각, 미각)",
      "emotional_intensity": 7,
      "internal_thought": "주인공 내면 독백 (있을 경우)"
    }}
  ]
}}
"""


class NarratorAgent:
    """Agent responsible for narrative perspective and worldbuilding"""

    def __init__(self, gemini_client):
        self.gemini_client = gemini_client
        self.name = "NarratorAgent"

    def design_world(self, material_brief: str, system_prompt: str = "") -> Dict[str, Any]:
        """
        Design world setting and characters based on material brief.

        Args:
            material_brief: Material brief content (JSON string or plain text)
            system_prompt: System prompt from skill loader

        Returns:
            World design dictionary
        """
        logger.info("NarratorAgent: Designing world and characters...")

        prompt = WORLD_DESIGN_PROMPT.format(material_brief=material_brief)

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

    def narrate_scenes(
        self, scene_structure: str, world_context: str, system_prompt: str = ""
    ) -> Dict[str, Any]:
        """
        Generate narrative text for scenes.

        Args:
            scene_structure: Scene structure from Story Agent (JSON string)
            world_context: World/character info from Step 2 (JSON string)
            system_prompt: System prompt from skill loader

        Returns:
            Scene narratives dictionary
        """
        logger.info("NarratorAgent: Narrating scenes...")

        prompt = SCENE_NARRATION_PROMPT.format(
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
