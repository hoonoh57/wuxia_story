# Agent Specifications

## Material Agent (L0)

**Purpose**: Select story materials based on trends and TOP-10 pool

**Input**:
- Trend data
- Existing TOP-10 material pool
- Target audience parameters

**Output**:
- Selected material brief containing:
  - Logline (one-sentence hook)
  - Core conflict
  - Target audience analysis
  - Psychological hooks

**Default Mode**: A (Human Relay) or C (Mixed)

**Rationale**: Material selection is strategic and requires human judgment about market viability.

---

## Narrator Agent (L1)

**Purpose**: Establish narrative perspective and create worldbuilding

**Input**:
- Material brief from Material Agent

**Output** (Step 2):
- World setting description
- Character profiles (5-layer structure)
- Relationship diagrams
- Narrative tone guidelines

**Output** (Step 4):
- Scene-by-scene narrative prose
- Emotional cues for actors/editors
- Action descriptions

**Default Mode**: C (Mixed)

**Rationale**: Narrative quality requires human refinement for depth and nuance.

---

## Story Agent (L2)

**Purpose**: Create structured episode storyboards using 15-beat framework

**Input**:
- World setting and character profiles from Narrator Agent

**Output**:
- 15-beat sequence (full episode structure)
- Scene breakdown (number, duration, beats)
- Timing distribution (pacing)
- Emotional arc graph

**15-Beat Structure**:
1. Status Quo
2. Inciting Incident
3. Rising Action 1
4. Midpoint Crisis
5. Rising Action 2
6-10. Beat sequences with escalation
11. Climax Setup
12. Climax
13. Climactic Resolution
14. Emotional Fallout
15. New Status Quo

**Default Mode**: B (Auto) possible

**Rationale**: Story structure is rule-based and can be automated with framework.

---

## Language Agent (L3)

**Purpose**: Refine narrative prose, dialogue, and emotional language

**Input**:
- Scene structure from Story Agent
- Character profiles and world setting

**Output**:
- Full narrative prose for each scene
- Character dialogue (with emotional subtext)
- Sensory descriptions
- Pacing and rhythm annotations

**Default Mode**: C (Mixed)

**Rationale**: Writing quality is subjective; human review essential for voice and style.

---

## Prompt Agent (L4)

**Purpose**: Convert narrative to visual generation prompts (AI image/video generation input)

**Input**:
- Complete scene narrative from Language Agent
- World setting and character descriptions

**Output**:
- Image/video generation prompts for each scene
- Camera specifications (angle, movement, framing)
- Lighting specifications (mood, color, intensity)
- Costume/prop specifications
- Effect descriptions (weather, magic, etc.)

**Prompt Format Example**:
```
Scene 5: [Location], [time of day]
Camera: [Angle/framing], [Movement]
Lighting: [Color palette], [Mood]
Characters: [Description with costume details]
Effects: [Environmental/magical effects]
Background: [Setting details]
Action: [Key movements and timing]
```

**Default Mode**: B (Auto) possible

**Rationale**: Mapping is rule-based; can be automated with visual framework.

---

## Agent Interaction

```
Material Agent (L0)
    ↓ [Material Brief]
Narrator Agent (L1) + Story Agent (L2)
    ↓ [World Setting + 15-Beat Structure]
Story Agent (L2: Detailed Planning)
    ↓ [Scene Breakdown]
Narrator Agent (L1) + Language Agent (L3)
    ↓ [Scene Narrative + Dialogue]
Prompt Agent (L4)
    ↓ [Visual Generation Prompts]
[Ready for Video Production]
```

## Skill System

Each agent has a corresponding skill file in `docs/SKILL_FILES/`:
- `SK-01_NARRATOR.md`: Narrator Agent system prompt
- `SK-02_STORY.md`: Story Agent system prompt
- `SK-03_PROMPT.md`: Prompt Agent system prompt
- `SK-04_MATERIAL.md`: Material Agent system prompt
- `MASTER_SYSTEM_v3.0.md`: Base system prompt for all agents
