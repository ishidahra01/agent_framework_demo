# Deep Research Plan Template

## Overview
This template provides a structured approach to deep research tasks requiring:
- Multiple information sources
- Fact verification
- Citation tracking
- Evidence-based conclusions

## Research Phases

### 1. Planning Phase
**Objective**: Break down the research question into actionable steps

**Tasks**:
- Identify key research questions
- Define information sources
- Establish success criteria
- Set constraints (time, token budget)

**Output**: Research plan with step-by-step breakdown

### 2. Information Gathering Phase
**Objective**: Collect relevant information from multiple sources

**Tasks**:
- Web search for current information
- RAG search in knowledge base
- Browse relevant websites
- Access internal APIs/databases (MCP)

**Output**: Raw information with source citations

### 3. Verification Phase
**Objective**: Cross-reference and validate collected information

**Tasks**:
- Compare information from multiple sources
- Check source credibility
- Identify conflicts or inconsistencies
- Rate confidence levels

**Output**: Verified facts with confidence scores

### 4. Synthesis Phase
**Objective**: Combine findings into coherent analysis

**Tasks**:
- Organize information by topic/theme
- Identify patterns and insights
- Draw evidence-based conclusions
- Note limitations and gaps

**Output**: Synthesized findings with supporting evidence

### 5. Reporting Phase
**Objective**: Generate comprehensive report

**Tasks**:
- Write executive summary
- Detail key findings
- List all citations
- Include methodology notes

**Output**: Final report with full citations

## Example: Market Sizing Research

```yaml
task: "Calculate 5-year CAGR for [market] with primary and secondary sources"

steps:
  - id: 1
    phase: gathering
    action: web_search
    query: "[market] market size reports 2019-2024"
    
  - id: 2
    phase: gathering
    action: rag_search
    query: "historical [market] data internal reports"
    
  - id: 3
    phase: verification
    action: cross_reference
    sources: [step_1_results, step_2_results]
    
  - id: 4
    phase: synthesis
    action: calculate_cagr
    data: verified_results
    
  - id: 5
    phase: reporting
    action: generate_report
    include: [summary, findings, calculations, citations]

constraints:
  budget_tokens: 40000
  time_limit_min: 30
  min_sources: 3
  require_citations: true
```

## Quality Criteria

- **Citation Coverage**: Every claim must have at least one citation
- **Source Diversity**: Use multiple independent sources
- **Fact Checking**: Cross-verify critical facts
- **Confidence Scoring**: Rate reliability of each finding
- **Reproducibility**: Document methodology for replication

## Human Review Points

The following actions require human approval:
- Publishing external reports
- Accessing sensitive data sources
- Making business recommendations
- Exporting research data
