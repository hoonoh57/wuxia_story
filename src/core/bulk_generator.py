"""
Bulk Generator - One-shot full pipeline execution (sequential mode)

User provides a single concept -> generates 6 steps sequentially
-> each step's output feeds the next step as context
-> all results saved to DB as drafts
"""

import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


# Step-specific prompts (each generates one step only)
STEP_PROMPTS = {
    1: """당신은 무협 웹소설/숏폼 드라마 소재 분석 전문가입니다.

## 소재 컨셉
{concept}

## 제작 규격
- 유튜브 숏폼 60~90초 x 30화, AI 영상 생성 (Midjourney/Runway/Kling)

## 출력: 아래 JSON을 완전히 채워서 반환하세요 (JSON만 출력, 다른 텍스트 없이)

{{
  "selected_material": {{
    "title": "소재 제목",
    "source": "컨셉 출처",
    "selection_rationale": "선정 이유 (2~3문장)"
  }},
  "logline": "한 문장 스토리 요약",
  "core_conflict": {{
    "protagonist": "주인공 설명",
    "antagonist": "대립 세력",
    "central_conflict": "핵심 갈등",
    "stakes": "판돈"
  }},
  "target_audience": {{
    "primary_demographic": "20~35세 남성, 무협/판타지 소비층",
    "geographic_markets": ["한국", "중국", "글로벌"],
    "psychographic_profile": "심리 프로파일",
    "consumption_platform": "유튜브 숏폼"
  }},
  "psychological_hooks": [
    {{"hook": "훅 이름", "human_motivation": "동기", "audience_resonance": "공명점"}}
  ],
  "viability_assessment": {{
    "creative_potential": 8,
    "market_potential": 7,
    "production_feasibility": 8,
    "recommendation": "추천 여부와 이유"
  }}
}}""",

    2: """당신은 무협 세계관/캐릭터 설계 전문가입니다.

## 이전 단계 소재 브리프
{prev_context}

## 제작 규격
- AI 영상 생성용: 모든 캐릭터 외형은 영어 키워드 5개 이상 포함
- 핵심 로케이션 5~7개, 각각 시각적 특징 포함
- 무공 시각 체계: 정파(백/금), 폐공(흑/자→순백+금)

## 출력: JSON만 출력하세요

{{
  "world_setting": {{
    "name": "세계 이름",
    "era": "시대 배경",
    "geography": "지리 설명",
    "key_locations": [
      {{"name": "", "visual_description": "", "color_mood": "", "usage": ""}}
    ],
    "magic_system": {{
      "orthodox_visual": "정파 무공 시각 묘사",
      "forbidden_visual_before": "폐공 각성 전 시각",
      "forbidden_visual_after": "폐공 각성 후 시각",
      "rank_system": ["1단계", "2단계", "3단계", "4단계"]
    }},
    "social_structure": "사회 구조 설명"
  }},
  "character_profiles": [
    {{
      "name": "캐릭터 이름",
      "role": "protagonist/heroine/antagonist/mentor/sub_antagonist",
      "layer_1_basic": {{
        "age": 17,
        "appearance_keywords_en": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
        "appearance_description_ko": "한글 외형 묘사",
        "status": "신분"
      }},
      "layer_2_personality": {{
        "core_trait": "핵심 성격",
        "inner_conflict": "내면 갈등",
        "speech_style": "말투 특징"
      }},
      "layer_3_abilities": {{
        "initial": "초기 능력",
        "awakening_stages": ["1차 각성", "2차 각성", "최종 각성"],
        "weakness": "약점"
      }},
      "layer_4_motivation": {{
        "surface_goal": "표면 목표",
        "true_motivation": "진짜 동기"
      }},
      "layer_5_arc": {{
        "start": "시작 상태",
        "midpoint": "중반 전환점",
        "end": "30화 종료 시점"
      }}
    }}
  ],
  "relationship_map": [
    {{"char_1": "", "char_2": "", "relationship": "", "conflict_point": "", "arc_direction": ""}}
  ]
}}""",

    3: """당신은 무협 스토리 구조 설계 전문가입니다.
15비트 프레임워크로 30화 에피소드 구조를 설계하세요.

## 세계관/캐릭터 (이전 단계)
{prev_context}

## 규칙
- 30화, 화당 60~90초
- 15비트를 30화에 매핑 (비트당 2화 기본, 1~3화 유동)
- 매 화 끝에 클리프행어 필수
- scene_number는 전체 통번호 (001~)

## 15비트
1-Status Quo, 2-Inciting Incident, 3-Rising Action 1, 4-Midpoint Crisis,
5-Rising Action 2, 6-Complication 1, 7-Complication 2, 8-Complication 3,
9-Dark Moment, 10-Recovery, 11-Climax Setup, 12-Climax,
13-Climactic Resolution, 14-Aftermath, 15-New Status Quo

## 출력: JSON만 출력하세요

{{
  "series_title": "시리즈 제목",
  "total_episodes": 30,
  "beats": [
    {{
      "beat_number": 1,
      "beat_name": "Status Quo",
      "episodes": "EP01-EP02",
      "primary_characters": [],
      "intensity": 3,
      "description": "비트 설명 (3문장)",
      "cliffhanger_hooks": ["EP01 훅", "EP02 훅"]
    }}
  ],
  "scenes": [
    {{
      "scene_number": 1,
      "episode_number": 1,
      "beat_number": 1,
      "location": "로케이션 이름 (Step 2 참조)",
      "characters": [],
      "duration_seconds": 35,
      "purpose": "씬 역할",
      "emotional_tone": "감정 톤",
      "visual_highlight": "핵심 비주얼 1줄"
    }}
  ],
  "emotional_curve": [
    {{"beat": 1, "intensity": 3}}
  ]
}}""",

    4: """당신은 무협 씬 내러티브 작가입니다.
초월적 3인칭 화자로 각 씬의 상세 서술을 작성하세요.

## 에피소드 구조 (이전 단계)
{prev_context}

## 규칙
- 나레이션: 고풍스럽되 현대 독자 이해 가능, 짧은 문장 위주
- 대사: 캐릭터별 고유 말투 (성격에 맞게)
- 감각 묘사 필수 (시각 2+, 청각 1+)
- 30화 전체의 처음 10화(EP01~EP10)를 작성하세요

## 출력: JSON만 출력하세요

{{
  "batch": "EP01-EP10",
  "episodes": [
    {{
      "episode_number": 1,
      "episode_title": "에피소드 부제",
      "opening_hook": "첫 3초 훅 문장",
      "scenes": [
        {{
          "scene_number": 1,
          "narration_text": "나레이션 본문 (한글, 300~450자)",
          "dialogue": [
            {{"character": "이름", "line": "대사", "subtext": "숨은 의미", "delivery": "어조"}}
          ],
          "action_description": "동작 묘사",
          "emotion_direction": "감정 + 강도 (1~10)",
          "visual_note": "AI 영상 핵심 비주얼 1~2문장"
        }}
      ],
      "cliffhanger": "화 끝 훅"
    }}
  ]
}}""",

    5: """당신은 AI 영상 프롬프트 변환 전문가입니다.
씬 서술을 Midjourney/Runway용 영상 프롬프트로 변환하세요.

## 씬 서술 (이전 단계)
{prev_context}

## 규칙
- image_prompt, video_prompt는 반드시 영어
- 캐릭터 외형은 Step 2의 appearance_keywords_en 사용
- negative_prompt 포함
- 이전 단계의 처음 10화(EP01~EP10) 씬에 대해 작성

## 출력: JSON만 출력하세요

{{
  "global_style": {{
    "art_direction": "cinematic Chinese wuxia, semi-realistic digital painting, 8K detail",
    "color_grading": "desaturated warm base, jade green and crimson red accents",
    "negative_prompt_global": "modern clothing, glasses, plastic, cars, phones, anime style, cartoon, low quality, blurry, watermark, text, extra fingers, deformed hands"
  }},
  "character_anchors": {{
    "protagonist": "영어 외형 키워드 문장",
    "heroine": "영어 외형 키워드 문장",
    "antagonist": "영어 외형 키워드 문장",
    "mentor": "영어 외형 키워드 문장",
    "sub_antagonist": "영어 외형 키워드 문장"
  }},
  "scenes": [
    {{
      "scene_number": 1,
      "episode_number": 1,
      "image_prompt": "영어 80~150단어 이미지 프롬프트",
      "video_prompt": "영어 60~120단어 비디오 프롬프트",
      "negative_prompt": "씬 특화 네거티브",
      "camera": {{"shot_type": "", "movement": "", "angle": ""}},
      "lighting": "조명 설명",
      "audio_mood": "소리/BGM 무드"
    }}
  ]
}}"""
}


class BulkGenerator:
    """Sequential full pipeline generator"""

    def __init__(self, gemini_client, skill_loader, repository):
        self.gemini_client = gemini_client
        self.skill_loader = skill_loader
        self.repository = repository
        logger.info("BulkGenerator initialized")

    def generate_full_pipeline(
        self,
        project_id: int,
        episode_id: int,
        concept: str,
        progress_callback=None,
    ) -> Dict[str, Any]:
        """
        Generate all 6 steps sequentially from a single concept.
        Each step's output feeds the next step as context.
        """
        logger.info(f"Starting sequential bulk generation for episode {episode_id}")

        results = {}
        prev_context = ""

        for step_num in range(1, 6):  # Steps 1-5
            step_label = f"Step {step_num}/5"
            logger.info(f"Generating {step_label}...")

            if progress_callback:
                progress_callback(step_num, f"Generating {step_label}...")

            # Build prompt
            prompt_template = STEP_PROMPTS[step_num]
            if step_num == 1:
                prompt = prompt_template.format(concept=concept)
            else:
                prompt = prompt_template.format(prev_context=prev_context)

            # Get system prompt
            system_prompt = self.skill_loader.build_system_prompt("master")

            # Call Gemini
            response = self.gemini_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=8000,
                temperature=0.7,
            )

            if not response["success"]:
                error_msg = response.get("error", "Unknown error")
                logger.error(f"{step_label} failed: {error_msg}")
                return {
                    "success": False,
                    "error": f"{step_label} failed: {error_msg}",
                    "completed_steps": list(results.keys()),
                }

            # Parse response
            parsed = self._parse_response(response["text"])
            raw_text = response["text"]

            if parsed:
                content = json.dumps(parsed, ensure_ascii=False, indent=2)
                prev_context = content
            else:
                content = raw_text
                prev_context = raw_text

            # Save to DB
            self._save_step(episode_id, step_num, content)
            results[step_num] = {
                "success": True,
                "tokens": {
                    "input": response.get("input_tokens", 0),
                    "output": response.get("output_tokens", 0),
                },
            }

            logger.info(
                f"{step_label} complete: "
                f"{response.get('input_tokens', 0)}+{response.get('output_tokens', 0)} tokens"
            )

        # Step 6: compile summary
        self._save_step6_summary(episode_id, results, concept)
        results[6] = {"success": True, "tokens": {"input": 0, "output": 0}}

        total_in = sum(r["tokens"]["input"] for r in results.values())
        total_out = sum(r["tokens"]["output"] for r in results.values())

        logger.info(f"Bulk generation complete: {total_in}+{total_out} tokens total")

        return {
            "success": True,
            "completed_steps": list(results.keys()),
            "tokens_used": {"input": total_in, "output": total_out},
        }

    def _parse_response(self, text: str) -> Optional[Dict]:
        """Parse JSON from response, handling code blocks."""
        try:
            clean = text.strip()

            if "```json" in clean:
                start = clean.index("```json") + 7
                end = clean.index("```", start)
                clean = clean[start:end].strip()
            elif "```" in clean:
                start = clean.index("```") + 3
                end = clean.index("```", start)
                clean = clean[start:end].strip()

            return json.loads(clean)
        except (json.JSONDecodeError, ValueError):
            return self._try_brace_parse(text)

    def _try_brace_parse(self, text: str) -> Optional[Dict]:
        """Find and parse the outermost JSON object."""
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
            logger.warning("Brace parse failed, saving as raw text")
            return None

    def _save_step(self, episode_id: int, step_num: int, content: str):
        """Save step content to DB."""
        session = self.repository.get_session()
        try:
            from src.data.models import Step

            step = session.query(Step).filter(
                Step.episode_id == episode_id,
                Step.step_number == step_num,
            ).first()

            if step:
                self.repository.create_step_version(
                    step_id=step.id,
                    content=content,
                    ai_generated=True,
                    created_by="bulk_generator",
                )
                logger.info(f"Step {step_num} saved to DB (step_id={step.id})")
            else:
                logger.warning(f"Step {step_num} record not found for episode {episode_id}")
        finally:
            session.close()

    def _save_step6_summary(self, episode_id: int, results: Dict, concept: str):
        """Save Step 6 summary."""
        summary = {
            "status": "ready_for_review",
            "concept": concept[:200],
            "steps_completed": len(results),
            "total_input_tokens": sum(r["tokens"]["input"] for r in results.values()),
            "total_output_tokens": sum(r["tokens"]["output"] for r in results.values()),
        }
        content = json.dumps(summary, ensure_ascii=False, indent=2)
        self._save_step(episode_id, 6, content)
