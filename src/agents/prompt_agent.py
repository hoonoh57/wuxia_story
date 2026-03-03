"""
Prompt Agent (L4) - Visual generation prompt formatting (output layer)

Responsibilities:
- Convert narrative text to image/video generation prompts
- Specify camera angles, movements, framing
- Define lighting, color palettes, mood
- Detail character appearance and costumes
- Describe visual effects and environment

Input: Scene narrative and dialogue (Step 4) + World/character context (Step 2)
Output: Visual generation prompts per scene (Step 5)
Default Mode: B (Auto) possible
"""

import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

VISUAL_PROMPT_TEMPLATE = """
당신은 AI 영상 생성 프롬프트 전문가입니다.
무협 영상의 시각적 요소를 정밀하게 지정하는 프롬프트를 작성합니다.

아래 씬 서술을 바탕으로 각 씬의 영상 생성 프롬프트를 작성하세요.

## 씬 서술 (Step 4 출력)
{scene_narrative}

## 세계관/캐릭터 정보
{world_context}

## 프롬프트 작성 규칙
1. 스타일: 동양 고대 무협 세계 (현대 요소 절대 금지)
2. 캐릭터: 한국/동아시아 외모, 무협 의상, 무기 상세
3. 카메라: 구체적인 앵글, 움직임, 프레이밍 지정
4. 조명: 시간대에 맞는 색온도와 분위기 지정
5. 네거티브: 현대 건물, 서양 갑옷, 총기, 전자기기 등 금지
6. 영어로 프롬프트 작성 (AI 이미지/비디오 모델용)

## 출력 형식 (반드시 이 JSON 구조를 따르세요)
{{
  "scenes": [
    {{
      "scene_number": 1,
      "scene_title": "씬 제목",
      "duration_seconds": 12,
      "visual_prompt": {{
        "setting": {{
          "location": "구체적 장소 묘사 (영어)",
          "time_of_day": "시간대",
          "weather": "날씨/대기",
          "atmosphere": "분위기 묘사"
        }},
        "camera": {{
          "shot_type": "Wide / Medium / Close-up / Extreme Close-up",
          "angle": "Low angle / Eye level / High angle / Bird's eye",
          "movement": "Static / Pan left / Track forward / Dolly zoom / etc.",
          "composition": "Rule of thirds / Center frame / etc.",
          "focus": "주 초점 대상"
        }},
        "lighting": {{
          "key_light": "주광 방향과 강도",
          "color_palette": ["#color1", "#color2", "#color3"],
          "mood": "Warm golden / Cool blue / Dramatic red / etc.",
          "intensity": 7,
          "special": "촛불, 달빛, 마법 빛 등"
        }},
        "characters": [
          {{
            "name": "캐릭터명",
            "appearance": "외모 묘사 (영어)",
            "costume": "의상 상세 (영어)",
            "expression": "표정",
            "pose": "포즈/자세",
            "action": "동작"
          }}
        ],
        "effects": [
          {{
            "type": "Environmental / Martial / Magical",
            "description": "효과 설명 (영어)",
            "intensity": 5
          }}
        ]
      }},
      "image_prompt": "이미지 생성용 프롬프트 (영어, 한 문단)",
      "video_prompt": "비디오 생성용 프롬프트 (영어, 한 문단, 동작 포함)",
      "negative_prompt": "네거티브 프롬프트 (금지 요소)"
    }}
  ],
  "global_style": {{
    "art_direction": "전체 아트 디렉션 (예: cinematic wuxia, ink wash aesthetic)",
    "color_grading": "전체 컬러 그레이딩 방향",
    "aspect_ratio": "16:9",
    "quality": "4K cinematic"
  }}
}}
"""


class PromptAgent:
    """Agent responsible for converting narrative to visual generation prompts"""

    def __init__(self, gemini_client):
        self.gemini_client = gemini_client
        self.name = "PromptAgent"

    def convert_to_visual(
        self, scene_narrative: str, world_context: str, system_prompt: str = ""
    ) -> Dict[str, Any]:
        """
        Convert scene narratives to visual generation prompts.

        Args:
            scene_narrative: Scene text from Step 4 (JSON string)
            world_context: World/character info from Step 2 (JSON string)
            system_prompt: System prompt from skill loader

        Returns:
            Visual prompts dictionary
        """
        logger.info("PromptAgent: Converting narrative to visual prompts...")

        prompt = VISUAL_PROMPT_TEMPLATE.format(
            scene_narrative=scene_narrative,
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
