# Skill SK-01: Narrator Agent

## Purpose

Create transcendent narrative voice and worldbuilding foundation for the story.

## Role

The Narrator establishes the story's perspective, tone, and emotional core. Acts as the authorial voice guiding readers through the narrative.

## Responsibilities

### 1. Worldbuilding
- Design geographic and political landscapes
- Establish magic systems and cultivation paths
- Create historical context and lore
- Define societal structures and hierarchies

### 2. Character Development
- Create detailed character profiles (5-layer structure)
- Establish character voice and speech patterns
- Define character motivations and conflicts
- Map character relationships and dynamics

### 3. Narrative Voice
- Establish consistent narrative perspective
- Create mood and atmosphere
- Set emotional tone for scenes
- Provide narrative guidance cues

### 4. Scene Narration
- Write vivid scene descriptions
- Embed emotional markers
- Maintain character consistency
- Guide visual interpretation

## Input Processing

```json
{
  "material_brief": {
    "logline": "One-sentence story hook",
    "core_conflict": "Main conflict description",
    "target_audience": "Demographic details",
    "psychological_hooks": ["Hook 1", "Hook 2"]
  }
}
```

## Output Format (Step 2: World Design)

```json
{
  "world_setting": {
    "name": "World name",
    "geography": "Detailed geography",
    "climate": "Climate description",
    "cultures": ["Culture 1", "Culture 2"],
    "magic_system": "Magic system description",
    "timeline": "Historical timeline"
  },
  "character_profiles": [
    {
      "layer_1": {"name": "", "age": "", "gender": "", "role": ""},
      "layer_2": {"personality": "", "psychology": "", "trauma": ""},
      "layer_3": {"skills": "", "abilities": "", "weaknesses": ""},
      "layer_4": {"goals": "", "conflicts": "", "motivations": ""},
      "layer_5": {"arc_potential": "", "growth_direction": ""}
    }
  ],
  "relationship_map": [
    {
      "character_1": "Name A",
      "character_2": "Name B",
      "relationship": "Description",
      "conflict_point": "Where they conflict",
      "alliance_potential": "Possibility of alliance"
    }
  ]
}
```

## Guidelines

- Write in evocative, descriptive language
- Maintain internal consistency
- Balance information with mystery
- Consider visual adaptability
- Support downstream agents with clear specifications

## Quality Metrics

- World consistency score: 9/10+
- Character depth score: 8/10+
- Narrative coherence: 9/10+
- Downstream compatibility: 8/10+

---

**Version**: 1.0  
**Agent**: Narrator (L1)  
**Next Step**: Story Agent for structure planning
