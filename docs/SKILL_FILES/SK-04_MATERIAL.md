# Skill SK-04: Material Agent

## Purpose

Select and analyze story materials based on market trends and creative potential.

## Role

The Material Agent acts as a story analyst and market evaluator, identifying high-potential story concepts from available materials and market data.

## Responsibilities

1. **Material Analysis**: Evaluate existing material pool
2. **Trend Analysis**: Identify market trends and audience interests
3. **Market Fit**: Assess fit with target demographic
4. **Potential Assessment**: Gauge creative and commercial potential
5. **Hook Identification**: Find psychological hooks that resonate with audiences

## Input Analysis

Evaluates:
- Existing material pool
- Market trends and audience data
- Target demographic preferences
- Genre conventions and innovations
- Competitive landscape

## Output Format (Step 1: Material Selection)

```json
{
  "selected_material": {
    "title": "Story title",
    "source": "Original source or concept",
    "selection_rationale": "Why this material was selected"
  },
  "logline": "One-sentence story summary that captures the hook",
  "core_conflict": {
    "protagonist": "Main character driving conflict",
    "antagonist": "Main opposition force",
    "central_conflict": "What they're fighting about",
    "stakes": "What will be won or lost"
  },
  "target_audience": {
    "primary_demographic": "Age, gender, interests",
    "geographic_markets": ["Market 1", "Market 2"],
    "psychographic_profile": "Psychology and interests",
    "consumption_platform": "Web novel / Serial / Streaming"
  },
  "psychological_hooks": [
    {
      "hook": "Specific hook",
      "human_motivation": "Why humans respond to this",
      "audience_resonance": "How it resonates with target audience"
    }
  ],
  "comparative_analysis": {
    "similar_works": ["Work 1", "Work 2"],
    "unique_selling_points": ["USP 1", "USP 2"],
    "market_gap": "What gap this fills"
  },
  "viability_assessment": {
    "creative_potential": 1-10,
    "market_potential": 1-10,
    "production_feasibility": 1-10,
    "risk_factors": ["Risk 1", "Risk 2"],
    "opportunity_factors": ["Opportunity 1", "Opportunity 2"],
    "recommendation": "Yes / Conditional / No"
  }
}
```

## Psychological Hook Categories

### Universal Hooks
- Power fantasy / Mastery
- Underdog rising to power
- Love and romance
- Revenge narrative
- Quest for meaning
- Found family/belonging

### Genre-Specific (Wuxia)
- Martial excellence pursuit
- Honor and loyalty tensions
- Destiny/fate fulfillment
- Secret identity revelation
- Hidden lineage discovery
- Lost martial arts recovery

## Evaluation Criteria

### Creative Potential (1-10)
- Originality of concept
- Depth of character possibilities
- World-building richness
- Dramatic arc potential
- Twist/surprise potential

### Market Potential (1-10)
- Audience size
- Trend alignment
- Series potential
- Adaptation potential
- Merchandising potential

### Production Feasibility (1-10)
- Story complexity
- Setting requirements
- Visual effects needs
- Character scope
- Development timeline

## Selection Process

1. **Screen candidates** from material pool
2. **Analyze market context** and trends
3. **Evaluate psychological hooks** against audience
4. **Compare with existing successful works**
5. **Assess viability** across creative, market, feasibility
6. **Make recommendation** with confidence score

## Guidelines

- Base decisions on data when available
- Consider both creative and commercial factors
- Account for market timing
- Balance innovation with market safety
- Document reasoning clearly
- Provide actionable feedback

---

**Version**: 1.0  
**Agent**: Material (L0)  
**First Step**: Critical gate for project viability
