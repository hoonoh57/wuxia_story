# Wuxia Story - System Architecture

## Overview

Wuxia Story is a multi-agent AI system for generating web novel content through a structured 6-step pipeline with human oversight.

## System Components

### 1. Core Infrastructure (`src/core/`)

#### skill_loader.py
- Loads markdown skill files from `docs/SKILL_FILES/`
- Compiles skills into system prompts for agents
- Supports hot-reloading of skill definitions

#### gemini_client.py
- Wrapper around Gemini API
- Implements retry logic with exponential backoff
- Manages API key rotation and error handling

#### dispatcher.py
- Controls execution mode (A/B/C)
- Routes method calls based on current mode
- Manages human-AI interaction flow

#### pipeline.py
- Orchestrates 6-step workflow
- Ensures step dependencies are met
- Manages data flow between steps

### 2. Agents (`src/agents/`)

#### MaterialAgent (L0)
- Selects story materials from pool
- Analyzes market trends
- Creates material briefs

#### NarratorAgent (L1)
- Designs worldbuilding and character profiles
- Establishes narrative perspective
- Provides scene narration

#### StoryAgent (L2)
- Creates episode structure using 15-beat framework
- Plans scene sequences
- Distributes emotional arcs

#### LanguageAgent (L3)
- Generates narrative prose and dialogue
- Refines writing style
- Creates emotional cues and action descriptions

#### PromptAgent (L4)
- Converts narratives to visual generation prompts
- Specifies camera, lighting, costumes
- Creates image/video generation instructions

### 3. Data Layer (`src/data/`)

#### models.py
SQLAlchemy models:
- `Project`: Top-level container
- `Episode`: Story episode (6 steps each)
- `Step`: Pipeline step within episode
- `StepVersion`: Version history with approval tracking

#### repository.py
- CRUD operations for all models
- Auto-creates 6 steps when episode is created
- Version management for step outputs

### 4. UI Layer (`src/ui/`)

#### main_window.py
- Application entry point
- Project management interface

#### step_editor.py
- Core editing interface
- Step execution controls
- Content review and approval

#### material_dashboard.py
- Material pool management
- Trend analysis display

#### history_viewer.py
- Version history display
- Change tracking

## Workflow

```
New Project
    ↓
Create Episode → Auto-generate 6 Steps
    ↓
STEP 1: Material Selection (Material Agent)
    ↓ [Approve]
STEP 2: World/Character Design (Narrator + Story Agents)
    ↓ [Approve]
STEP 3: Episode Structure (Story Agent)
    ↓ [Approve]
STEP 4: Scene Narration (Narrator + Language Agents)
    ↓ [Approve]
STEP 5: Visual Prompts (Prompt Agent)
    ↓ [Approve]
STEP 6: Final Package (Human Approval)
    ↓ [Approve]
Ready for Video Production
```

## Data Flow

Each step receives input from the approved output of the previous step:

```
Material Brief (Step 1)
    ↓
World Setting + Characters (Step 2)
    ↓
Episode Structure + 15 Beats (Step 3)
    ↓
Scene Narrative + Dialogue (Step 4)
    ↓
Visual Prompts + Specifications (Step 5)
    ↓
Final Package (Step 6)
```

## Version Control

Each step maintains version history:

```
Step
├── v1 (gemini_auto, draft)
├── v2 (human_edit, draft)
└── v3 (human_edit, approved) ← Used as input to next step
```

Only approved versions are passed to subsequent steps.

## Dispatch Modes

- **Mode A (Human Relay)**: Human makes decisions, AI assists
  - Used for: Material selection, Final approval
  
- **Mode B (Auto)**: Fully automated AI generation
  - Used for: Episode structure, Visual prompts
  
- **Mode C (Mixed)**: AI generates draft, human reviews
  - Default for: World design, Scene narration, Language polish

## Error Handling

- API failures trigger automatic retry with exponential backoff
- Failed steps can be re-executed without affecting approval state
- All operations are logged for audit trail

## Database Schema

See [WORKFLOW.md](WORKFLOW.md) for detailed database structure documentation.
