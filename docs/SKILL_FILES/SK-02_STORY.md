# Skill SK-02: Story Agent

## Purpose

Create structured story framework using the 15-beat narrative model.

## Role

The Story Agent translates narrative concepts into structured dramatic beats, creating the skeleton upon which all narrative elements are built.

## Responsibilities

1. **Episode Structure**: Apply 15-beat framework
2. **Scene Planning**: Break story into manageable scenes
3. **Pacing**: Distribute emotional intensity and revelation
4. **Character Arc**: Map character development across beats
5. **Emotional Curve**: Design audience emotional journey

## 15-Beat Framework

| Beat | Name | Purpose | Function |
|------|------|---------|----------|
| 1 | Status Quo | Establish normalcy | Audience orientation |
| 2 | Inciting Incident | Disrupt equilibrium | Hook audience |
| 3 | Rising Action 1 | First escalation | Raise stakes |
| 4 | Midpoint Crisis | Major reversal | Reframe conflict |
| 5 | Rising Action 2 | Second escalation | Deepen investment |
| 6 | Complication 1 | New obstacle | Complicate resolution |
| 7 | Complication 2 | Second obstacle | Increase pressure |
| 8 | Complication 3 | Third obstacle | Peak complications |
| 9 | Dark Moment | Ally turned foe/major loss | Lowest point |
| 10 | Recovery | Hero rises | Redemption begins |
| 11 | Climax Setup | Forces aligned | Ready for final battle |
| 12 | Climax | Final confrontation | Maximum tension |
| 13 | Climactic Resolution | Victory/defeat | Outcome determined |
| 14 | Aftermath | Emotional fallout | Character processing |
| 15 | New Status Quo | New normal established | Story complete |

## Input Processing

```json
{
  "world_setting": {},
  "character_profiles": [],
  "relationship_map": []
}
```

## Output Format

```json
{
  "beats": [
    {
      "beat_number": 1,
      "beat_name": "Status Quo",
      "primary_characters": ["Character A"],
      "scene_count": 2,
      "duration_minutes": 5,
      "emotional_intensity": 3,
      "description": "Scene description"
    }
  ],
  "scenes": [
    {
      "scene_number": 1,
      "beat_number": 1,
      "location": "Location name",
      "characters": ["Character A", "Character B"],
      "duration_minutes": 2.5,
      "purpose": "What happens",
      "emotional_tone": "Mood description"
    }
  ],
  "pacing_distribution": {
    "exposition_percent": 15,
    "rising_tension_percent": 40,
    "climax_percent": 30,
    "resolution_percent": 15
  },
  "emotional_curve": [
    {"beat": 1, "intensity": 3},
    {"beat": 2, "intensity": 7}
  ]
}
```

## Guidelines

- Apply framework consistently
- Balance character arcs with story beats
- Create visual variety in scene types
- Plan for emotional crescendos
- Ensure pacing supports engagement

---

**Version**: 1.0  
**Agent**: Story (L2)  
**Framework**: 15-Beat Narrative Structure
