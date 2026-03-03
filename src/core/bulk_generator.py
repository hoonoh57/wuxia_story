"""
Bulk Generator - One-shot full pipeline execution

User provides a single concept → generates all 6 steps automatically
→ parses and saves each step to DB → user reviews/edits at leisure
"""

import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


# Master prompt that generates ALL steps in one call
FULL_PIPELINE_PROMPT = """
당신은 무협 웹소설/숏폼 드라마 전문 작가 시스템입니다.
아래 소재 컨셉을 받아서, 6단계 전체를 한 번에 완성하세요.

## 소재 컨셉
{concept}

## 제작 규격
- 유튜브 숏폼 60~90초 × 30화
- AI 영상 생성 (Midjourney/Runway/Kling)
- 세로 9:16 형식

## 출력: 아래 JSON 구조를 완전히 채워서 반환하세요

{{
  "step1_material": {{
    "selected_material": {{
      "title": "",
      "source": "",
      "selection_rationale": ""
    }},
    "logline": "",
    "core_conflict": {{
      "protagonist": "",
      "antagonist": "",
      "central_conflict": "",
      "stakes": ""
    }},
    "target_audience": {{
      "primary_demographic": "",
      "geographic_markets": [],
      "psychographic_profile": "",
      "consumption_platform": ""
    }},
    "psychological_hooks": [
      {{"hook": "", "human_motivation": "", "audience_resonance": ""}}
    ],
    "viability_assessment": {{
      "creative_potential": 0,
      "market_potential": 0,
      "production_feasibility": 0,
      "recommendation": ""
    }}
  }},

  "step2_world_design": {{
    "world_setting": {{
      "name": "",
      "era": "",
      "geography": "",
      "key_locations": [
        {{"name": "", "visual_description": "", "usage_scenes": ""}}
      ],
      "magic_system": {{
        "orthodox_visual": "",
        "forbidden_art_visual": "",
        "awakened_visual": "",
        "rank_system": []
      }},
      "social_structure": ""
    }},
    "character_profiles": [
      {{
        "name": "",
        "role": "",
        "layer_1_basic": {{"age": 0, "appearance_keywords": [], "status": ""}},
        "layer_2_personality": {{"core_trait": "", "inner_conflict": "", "speech_style": ""}},
        "layer_3_abilities": {{"initial": "", "awakening_stages": [], "weakness": ""}},
        "layer_4_motivation": {{"surface_goal": "", "true_motivation": ""}},
        "layer_5_arc": {{"start": "", "midpoint": "", "end": ""}}
      }}
    ],
    "relationship_map": [
      {{"char_1": "", "char_2": "", "relationship": "", "arc_direction": ""}}
    ]
  }},

  "step3_episode_structure": {{
    "series_title": "",
    "total_episodes": 30,
    "beats": [
      {{
        "beat_number": 0,
        "beat_name": "",
        "episodes": "",
        "intensity": 0,
        "description": "",
        "cliffhanger_hooks": []
      }}
    ],
    "scenes": [
      {{
        "scene_number": 0,
        "episode_number": 0,
        "beat_number": 0,
        "location": "",
        "characters": [],
        "duration_seconds": 0,
        "purpose": "",
        "emotional_tone": "",
        "visual_highlight": ""
      }}
    ],
    "emotional_curve": [
      {{"beat": 0, "intensity": 0}}
    ]
  }},

  "step4_scene_narration": {{
    "episodes": [
      {{
        "episode_number": 0,
        "episode_title": "",
        "opening_hook": "",
        "scenes": [
          {{
            "scene_number": 0,
            "narration_text": "",
            "dialogue": [
              {{"character": "", "line": "", "subtext": "", "delivery": ""}}
            ],
            "action_description": "",
            "emotion_direction": "",
            "visual_note": ""
          }}
        ],
        "cliffhanger": ""
      }}
    ]
  }},

  "step5_visual_prompts": {{
    "global_style": {{
      "art_direction": "",
      "color_grading": "",
      "negative_prompt_global": ""
    }},
    "character_anchors": {{}},
    "scenes": [
      {{
        "scene_number": 0,
        "episode_number": 0,
        "image_prompt": "",
        "video_prompt": "",
        "negative_prompt": "",
        "camera": {{"shot_type": "", "movement": "", "angle": ""}},
        "lighting": "",
        "audio_mood": ""
      }}
    ]
  }}
}}

## 중요 규칙
1. 30화 전체의 모든 씬을 빠짐없이 포함하라
2. 캐릭터 이름/외형은 step2에서 정한 것을 이후 모든 단계에서 일관되게 사용
3. scene_number는 전체 통번호로 step3~step5에서 동일하게 유지
4. image_prompt와 video_prompt는 반드시 영어로 작성
5. 모든 에피소드는 cliffhanger로 끝남
"""


class BulkGenerator:
    """One-shot full pipeline generator"""

    def __init__(self, gemini_client, skill_loader, repository):
        self.gemini_client = gemini_client
        self.skill_loader = skill_loader
        self.repository = repository
        logger.info("BulkGenerator initialized")

    def generate_full_pipeline(
        self, project_id: int, episode_id: int, concept: str
    ) -> Dict[str, Any]:
        """
        Generate all 6 steps from a single concept.

        Args:
            project_id: Project ID
            episode_id: Episode ID (with 6 steps already created)
            concept: User's story concept (can be one sentence)

        Returns:
            Result dict with success flag and generated data
        """
        logger.info(f"Starting bulk generation for episode {episode_id}")
        logger.info(f"Concept: {concept[:100]}...")

        # Build system prompt from all skills
        system_prompt = self.skill_loader.build_system_prompt("master")

        # Build the full pipeline prompt
        prompt = FULL_PIPELINE_PROMPT.format(concept=concept)

        # Generate with higher token limit
        response = self.gemini_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=30000,
            temperature=0.8,
        )

        if not response["success"]:
            logger.error(f"Bulk generation failed: {response.get('error')}")
            return {"success": False, "error": response.get("error", "")}

        # Parse the response
        parsed = self._parse_full_response(response["text"])
        if not parsed:
            return {
                "success": False,
                "error": "Failed to parse response JSON",
                "raw_text": response["text"],
            }

        # Save each step to DB
        self._save_all_steps(episode_id, parsed)

        logger.info("Bulk generation complete — all 6 steps saved")
        return {
            "success": True,
            "data": parsed,
            "tokens_used": {
                "input": response["input_tokens"],
                "output": response["output_tokens"],
            },
        }

    def _parse_full_response(self, text: str) -> Optional[Dict]:
        """Parse the full JSON response."""
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
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"JSON parse error: {e}")
            return self._try_partial_parse(text)

    def _try_partial_parse(self, text: str) -> Optional[Dict]:
        """Attempt to parse partial/broken JSON."""
        start = text.find("{")
        if start == -1:
            return None

        depth = 0
        end = start
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break

        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            logger.error("Partial parse also failed")
            return None

    def _save_all_steps(self, episode_id: int, data: Dict):
        """Save parsed data to all 6 steps in DB."""

        step_mapping = {
            1: "step1_material",
            2: "step2_world_design",
            3: "step3_episode_structure",
            4: "step4_scene_narration",
            5: "step5_visual_prompts",
            6: None,  # Final approval = aggregate of 1-5
        }

        session = self.repository.get_session()
        try:
            from src.data.models import Step

            for step_num, data_key in step_mapping.items():
                step = session.query(Step).filter(
                    Step.episode_id == episode_id,
                    Step.step_number == step_num,
                ).first()

                if not step:
                    logger.warning(f"Step {step_num} not found")
                    continue

                if data_key and data_key in data:
                    content = json.dumps(
                        data[data_key], ensure_ascii=False, indent=2
                    )
                elif step_num == 6:
                    content = json.dumps(
                        {
                            "status": "ready_for_review",
                            "summary": {
                                "title": data.get("step1_material", {})
                                    .get("selected_material", {})
                                    .get("title", ""),
                                "total_episodes": 30,
                                "total_scenes": len(
                                    data.get("step3_episode_structure", {})
                                        .get("scenes", [])
                                ),
                                "steps_generated": list(step_mapping.keys()),
                            },
                        },
                        ensure_ascii=False,
                        indent=2,
                    )
                else:
                    content = "{}"

                self.repository.create_step_version(
                    step_id=step.id,
                    content=content,
                    ai_generated=True,
                    created_by="bulk_generator",
                )
                logger.info(f"Step {step_num} saved to DB")

        finally:
            session.close()
