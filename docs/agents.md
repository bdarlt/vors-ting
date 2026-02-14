# Agent Development Guide

This guide provides specific information about developing and working with agents in the Vörs ting system.

## Table of Contents

- [Agent Architecture](#agent-architecture)
- [Agent Types](#agent-types)
- [Creating New Agents](#creating-new-agents)
- [Agent Lifecycle](#agent-lifecycle)
- [Best Practices](#best-practices)
- [Testing Agents](#testing-agents)

## Agent Architecture

All agents in Vörs ting inherit from the `BaseAgent` class and implement the core interface:

```python
class BaseAgent(ABC):
    def generate(self, task: str, context: dict[str, Any] | None = None) -> str:
        """Generate content based on the task."""
        ...

    def review(self, content: str, rubric: dict[str, Any] | None = None) -> dict[str, Any]:
        """Review content and provide feedback."""
        ...

    def refine(self, original: str, feedback: dict[str, Any]) -> str:
        """Refine content based on feedback."""
        ...

    def reject(self, reason: str) -> dict[str, Any]:
        """Reject the task with a reason."""
        ...
```

## Agent Types

### Creator Agents

**Purpose**: Generate initial content and refine based on feedback

**Key Characteristics**:
- Focus on content creation
- Implement all three core methods (`generate`, `review`, `refine`)
- Can specialize in different domains (ADRs, tests, documentation)

**Example Use Cases**:
- Writing Architecture Decision Records (ADRs)
- Generating unit tests
- Creating process documentation
- Drafting meeting templates

### Reviewer Agents

**Purpose**: Evaluate content quality and provide constructive feedback

**Key Characteristics**:
- Focus on critical analysis
- Use rubrics for structured evaluation
- Provide actionable feedback
- Can specialize in different criteria (security, usability, performance)

**Example Use Cases**:
- Code reviews
- Architecture reviews
- Documentation quality assessment
- Compliance checking

### Curator Agents

**Purpose**: Organize and synthesize diverse ideas

**Key Characteristics**:
- Focus on information organization
- Cluster similar ideas
- Create summaries and syntheses
- Work with multiple inputs

**Example Use Cases**:
- Brainstorming sessions
- Idea clustering
- Divergent thinking phases
- Landscape analysis

## Creating New Agents

### Step 1: Choose the Right Base Class

```python
# For content generation
from vors_ting.agents.creator import CreatorAgent

# For content review
from vors_ting.agents.reviewer import ReviewerAgent

# For idea organization
from vors_ting.agents.curator import CuratorAgent
```

### Step 2: Define Agent-Specific Behavior

```python
class SecurityReviewer(ReviewerAgent):
    """Specialized reviewer for security analysis."""

    def __init__(self, **kwargs):
        super().__init__(
            name="SecurityReviewer",
            role="reviewer",
            system_prompt=(
                "You are a security expert. Evaluate content for "
                "security vulnerabilities, best practices, and compliance."
            ),
            **kwargs
        )

    def review(self, content: str, rubric: dict[str, Any] | None = None) -> dict[str, Any]:
        """Review content with security focus."""
        # Add security-specific review logic
        return super().review(content, rubric)
```

### Step 3: Configure in YAML

```yaml
agents:
  - name: "SecurityReviewer"
    role: "reviewer"
    model: "gpt-4-turbo"
    provider: "openai"
    temperature: 0.1
    system_prompt: "You are a security expert..."
```

## Agent Lifecycle

### 1. Initialization
- Agent is created with configuration
- System prompt is set
- LLM connection is established

### 2. Generation Phase
- Creator agents generate initial content
- Content is based on task description and context
- Multiple creators can generate diverse solutions

### 3. Review Phase
- Reviewer agents evaluate content
- Feedback is structured according to rubric
- Multiple reviewers can provide different perspectives

### 4. Refinement Phase
- Creator agents refine content based on feedback
- Process may repeat for multiple rounds
- Content improves iteratively

### 5. Convergence
- Process continues until convergence criteria are met
- Final content is saved and returned

## Best Practices

### 1. Role-Specific System Prompts

```python
# ✅ Good: Specific and focused
system_prompt = (
    "You are a security-focused software architect. "
    "Evaluate designs for vulnerabilities and compliance."
)

# ❌ Avoid: Too generic
system_prompt = "You are a helpful assistant."
```

### 2. Error Handling

```python
# ✅ Good: Handle LLM errors gracefully
def generate(self, task: str, context: dict[str, Any] | None = None) -> str:
    try:
        return self._call_llm(prompt)
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return self._fallback_generation(task, context)
```

### 3. Context Management

```python
# ✅ Good: Use context effectively
def generate(self, task: str, context: dict[str, Any] | None = None) -> str:
    prompt = f"Task: {task}"
    if context:
        prompt += f"\n\nContext: {self._format_context(context)}"
    return self._call_llm(prompt)
```

### 4. Performance Optimization

```python
# ✅ Good: Cache frequent LLM calls when appropriate
@lru_cache(maxsize=32)
def _get_cached_response(self, prompt: str) -> str:
    return self._call_llm(prompt)
```

## Testing Agents

### Unit Testing

```python
# Test agent initialization
def test_security_reviewer_initialization():
    agent = SecurityReviewer(model="gpt-4", provider="openai")
    assert agent.name == "SecurityReviewer"
    assert agent.role == "reviewer"

# Test agent methods with mocking
@patch.object(SecurityReviewer, '_call_llm')
def test_security_review(mock_llm):
    mock_llm.return_value = "Security review completed"
    agent = SecurityReviewer(model="gpt-4", provider="openai")
    
    result = agent.review("test content")
    assert "feedback" in result
```

### Integration Testing

```python
# Test agent in orchestration context
def test_agent_in_orchestrator():
    config = Config(
        task="Review security design",
        agents=[AgentConfig(name="SecurityReviewer", role="reviewer", ...)],
        rounds=1
    )
    
    orchestrator = Orchestrator(config)
    # Test the full workflow
```

## Advanced Topics

### Custom Agent Behavior

For agents that need specialized behavior beyond the standard methods:

```python
class AdvancedCurator(CuratorAgent):
    def cluster_ideas(self, ideas: list[str], method: str = "embedding") -> list[list[str]]:
        """Override default clustering with custom implementation."""
        if method == "embedding":
            return self._embedding_based_clustering(ideas)
        elif method == "keyword":
            return self._keyword_based_clustering(ideas)
        else:
            return self._default_clustering(ideas)

    def _embedding_based_clustering(self, ideas: list[str]) -> list[list[str]]:
        """Use sentence embeddings for clustering."""
        # Implement custom clustering logic
        pass
```

### Agent Collaboration

Agents can be designed to work together in specific patterns:

```python
class CollaborativeAgent(BaseAgent):
    def __init__(self, collaborators: list[BaseAgent] | None = None, **kwargs):
        super().__init__(**kwargs)
        self.collaborators = collaborators or []

    def generate(self, task: str, context: dict[str, Any] | None = None) -> str:
        # Get input from collaborators
        collaborator_inputs = [agent.generate(task, context) for agent in self.collaborators]
        
        # Synthesize results
        return self._synthesize_inputs(task, collaborator_inputs)
```

## Related Documentation

- [Coding Standards](CODING_STANDARDS.md) - General coding guidelines
- [Development Guide](development_guide.md) - Comprehensive development advice
- [Design Document](design.md) - Overall system architecture

## Contributing Agent Code

When adding new agents:

1. **Follow existing patterns** in the codebase
2. **Add comprehensive tests** for new functionality
3. **Document agent capabilities** in docstrings
4. **Update configuration examples** to show usage
5. **Consider performance implications** of new agent types

Agent development is where the domain-specific intelligence of Vörs ting resides. Well-designed agents can significantly improve the quality and relevance of the feedback loops.
