# Workflow - 6-Step Story Generation Pipeline

## Overview

The workflow guides a story from material selection through final delivery package in 6 sequential steps.

## Step-by-Step Workflow

### STEP 1: Material Selection

**Agent**: Material Agent (L0)

**Input**: 
- Trend data
- TOP-10 material pool
- Target parameters

**Process**:
- Analyze market trends and audience preferences
- Review existing material pool
- Identify gaps and opportunities
- Select material with highest potential

**Output**:
- Material Selection Brief
  - Logline
  - Core conflict identification
  - Target demographic
  - Psychological hooks (why people will care)
  - Success probability assessment

**Default Mode**: A (Human Relay)

**Approval Requirement**: Human must approve before proceeding

**Next Step**: Material Brief → Step 2

---

### STEP 2: World & Character Design

**Agents**: Narrator Agent (L1) + Story Agent (L2)

**Input**: 
- Material Selection Brief from Step 1

**Process**:
- Narrator Agent creates world setting description
- Define magic system, geography, social structures
- Create character profiles (5-layer structure)
- Story Agent sketches overall narrative arc
- Create relationship diagrams

**Output**:
- World Setting Document
  - Geography and environment
  - Social/political structures
  - Magic/power systems
  - History and lore
  
- Character Profiles (5-layer)
  - Layer 1: Basic demographics
  - Layer 2: Personality and psychology
  - Layer 3: Skills and abilities
  - Layer 4: Goals and conflicts
  - Layer 5: Character arc potential

- Relationship Diagram
  - Character connections
  - Conflict points
  - Alliance opportunities

**Default Mode**: C (Mixed)

**Approval Requirement**: Human reviews and can edit for depth

**Next Step**: World Setting → Step 3

---

### STEP 3: Episode Structure

**Agent**: Story Agent (L2)

**Input**: 
- World Setting and Character Profiles from Step 2

**Process**:
- Apply 15-beat narrative framework
- Map character arcs across story beats
- Distribute emotional tension
- Plan pacing and rhythm
- Identify scene requirements

**Output**:
- 15-Beat Outline
  1. Status Quo introduction
  2. Inciting incident
  3-5. Rising tension phase
  6. Midpoint reversal
  7-10. Escalation sequence
  11-12. Climax build and execution
  13-14. Resolution and fallout
  15. New equilibrium

- Scene Breakdown
  - Scene number and location
  - Character involved
  - Beat number
  - Duration estimate
  - Emotional intensity

- Emotional Curve Map
  - Pacing distribution
  - Emotional peaks and valleys
  - Tension management

**Default Mode**: B (Auto) - Can be automated with review

**Approval Requirement**: Human reviews structure and pacing

**Next Step**: 15-Beat Structure → Step 4

---

### STEP 4: Scene Narrative & Dialogue

**Agents**: Narrator Agent (L1) + Language Agent (L3)

**Input**: 
- 15-Beat Structure and Scene Breakdown from Step 3
- World Setting and Characters from Step 2

**Process**:
- Narrator Agent establishes narrative voice and perspective
- Language Agent writes scene prose, dialogue, descriptions
- Embed emotional cues for later visual adaptation
- Polish dialogue for character voice consistency
- Refine action descriptions

**Output**: 
- For Each Scene:
  - Narrative prose (300-1000 words depending on scene)
  - Character dialogue with emotional subtext
  - Action and blocking descriptions
  - Internal thoughts/perspective markers
  - Environmental sensory details
  - Emotional intensity markers (1-10 scale)

**Default Mode**: C (Mixed)

**Approval Requirement**: Human reviews for voice, style, emotional resonance

**Next Step**: Scene Narrative → Step 5

---

### STEP 5: Visual Generation Prompts

**Agent**: Prompt Agent (L4)

**Input**: 
- Scene Narrative and Dialogue from Step 4
- Character Profiles from Step 2
- World Setting from Step 2

**Process**:
- Convert each scene narrative to visual specifications
- Extract key visual elements
- Create camera/framing directions
- Specify lighting and color mood
- Detail character appearance/costume
- Define environmental effects
- Create prompts for AI image/video generation

**Output**: 
- For Each Scene:
  - Visual Generation Prompt (for Midjourney, Runway, etc.)
  - Camera Specifications
    * Angle (low/mid/high, wide/close)
    * Movement (pan, track, dolly, etc.)
    * Framing (rule of thirds, composition)
  - Lighting Specifications
    * Color palette
    * Mood (warm/cool, bright/dim)
    * Key light direction
  - Character/Costume Details
    * Appearance description
    * Clothing and armor
    * Weapon/tool specifications
  - Environmental Effects
    * Weather/atmosphere
    * Magical effects
    * Physics/movement
  - Timing & Duration
    * Scene length in seconds
    * Beat timing

**Default Mode**: B (Auto) - Rule-based mapping

**Approval Requirement**: Human reviews visual coherence and consistency

**Next Step**: Visual Prompts → Step 6

---

### STEP 6: Final Package Approval

**Human**: Project Lead/Editor

**Input**: 
- Complete package from all previous steps
- Visual Prompts from Step 5
- Full narrative and character documents

**Process**:
- Review complete story package for:
  * Internal consistency
  * Narrative quality
  * Visual coherence
  * Production feasibility
- Make final adjustments if needed
- Approve for video production

**Output**:
- Final Approved Package
  - All narrative, character, and world documents
  - Visual generation prompts ready for production
  - Metadata and specifications
  - Production guidelines

**Default Mode**: A (Human Relay)

**Approval Requirement**: Mandatory human approval

**Next Step**: Package → Video Production Team

---

## Version Control System

Each step creates versions tracked in the database:

```
Step
├── v1
│   ├── created_by: "gemini_auto"
│   ├── status: "draft"
│   ├── content: [AI-generated content]
│   └── timestamp: [creation time]
├── v2
│   ├── created_by: "human_edit"
│   ├── status: "draft"
│   ├── content: [edited by human]
│   └── timestamp: [edit time]
└── v3 ✓ APPROVED
    ├── created_by: "human_edit"
    ├── status: "approved"
    ├── content: [final approved version]
    └── timestamp: [approval time]
```

**Rule**: Only APPROVED versions are passed to the next step.

---

## Error Recovery

If a step fails or needs revision:

1. Create new version within same step
2. Maintain previous version history
3. Can re-generate from previous approved step without losing work
4. Multiple iterations possible before final approval

Example revision flow:
```
Step 4 v1: Draft generated → Needs work
Step 4 v2: Human edits v1 → Still needs work
Step 4 v3: Human major rewrite → Approved ✓
        ↓
Step 5 uses v3 as input
```

---

## Database Schema

### Steps Table
```sql
CREATE TABLE steps (
    id INTEGER PRIMARY KEY,
    episode_id INTEGER FOREIGN KEY,
    step_number INTEGER (1-6),
    step_name VARCHAR (material_selection, world_design, etc.),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### StepVersion Table
```sql
CREATE TABLE step_versions (
    id INTEGER PRIMARY KEY,
    step_id INTEGER FOREIGN KEY,
    version_number INTEGER,
    status ENUM (draft, approved),
    content TEXT (JSON),
    ai_generated BOOLEAN,
    created_by VARCHAR (gemini_auto, human_edit),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

## Mode Guidelines

**Recommended Modes by Step:**

| Step | Recommended | Rationale |
|------|-------------|-----------|
| 1. Material | A | Human judgment critical for business decision |
| 2. World/Character | C | AI draft + human depth |
| 3. Structure | B | Rule-based, can automate |
| 4. Narrative | C | Quality requires human touch |
| 5. Prompts | B | Rule-based conversion |
| 6. Final | A | Human responsible for quality gate |

**Mode Flexibility:**
- Can override recommended modes per project
- Can change modes mid-project
- Can set different modes for different episodes
