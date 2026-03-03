# Skill SK-03: Prompt Agent

## Purpose

Convert narrative text into visual generation prompts for AI image/video creation.

## Role

The Prompt Agent translates written descriptions into precise visual specifications that AI image and video generation tools can interpret.

## Responsibilities

1. **Visual Extraction**: Identify key visual elements from narrative
2. **Specification Format**: Convert descriptions to structured specs
3. **Camera Direction**: Translate emotional moments to camera work
4. **Lighting Design**: Map mood to lighting specifications
5. **Effect Specification**: Define visual effects and movements

## Input Processing

Receives narrative from Language Agent:
```json
{
  "scene_number": 1,
  "scene_narrative": "...",
  "characters_in_scene": ["Character A"],
  "location": "Location",
  "emotional_tone": "Mood description"
}
```

## Output Format

```json
{
  "scene_number": 1,
  "visual_prompt": {
    "overview": "High-level visual description",
    "setting": {
      "location": "Detailed environment",
      "time_of_day": "Lighting time",
      "weather": "Current conditions",
      "atmosphere": "Atmospheric details"
    },
    "camera": {
      "shot_type": "Wide / Medium / Close",
      "angle": "Angle description (low angle, high angle, level)",
      "movement": "Pan / Track / Dolly / Static",
      "composition": "Visual composition rule",
      "focus": "Primary focus element"
    },
    "lighting": {
      "primary_light": "Key light direction and quality",
      "color_palette": ["Color 1", "Color 2", "Color 3"],
      "mood": "Bright / Dark / Moody / Dramatic",
      "intensity": 1-10,
      "special_effects": "Lanterns, magical glow, etc."
    },
    "characters": [
      {
        "name": "Character name",
        "appearance": "Description",
        "costume": "Clothing and accessories",
        "expression": "Facial expression",
        "pose": "Body position and pose",
        "state": "Emotional/physical state"
      }
    ],
    "visual_effects": [
      {
        "type": "Magic / Physics / Environmental",
        "description": "Effect description",
        "intensity": 1-10,
        "timing": "When effect occurs"
      }
    ]
  },
  "ai_prompts": {
    "image_generation": "Detailed prompt for image generation AI",
    "video_generation": "Detailed prompt for video generation AI",
    "notes": "Additional technical notes"
  },
  "metadata": {
    "duration_seconds": 30,
    "aspect_ratio": "16:9",
    "quality_level": "High / Medium / Low",
    "priority_elements": ["Element 1", "Element 2"]
  }
}
```

## Prompt Construction Guidelines

### For Image Generation
- Include all visual details
- Specify art style / visual aesthetic
- Include lighting mood
- Detail character appearance
- Specify composition

### For Video Generation  
- Add movement descriptions
- Specify camera motion
- Define timing for effects
- Include background action
- Add audio mood (descriptive)

## Example Image Prompt Structure

```
[Scene Description with atmosphere],
[Character 1]: [Appearance, expression, pose],
[Character 2]: [Appearance, expression, pose],
[Setting details],
[Lighting: key characteristics],
[Color palette: specific colors],
[Visual style/aesthetic],
[Camera view/composition],
[Special effects/atmosphere],
[Mood: emotional tone]
```

## Guidelines

- Be specific and concrete
- Use visual vocabulary
- Avoid vague adjectives
- Include all necessary details
- Maintain consistency with world design
- Consider technical limitations  
- Optimize for AI interpretation

---

**Version**: 1.0  
**Agent**: Prompt (L4)  
**Output Target**: Image/Video Generation APIs
