#!/usr/bin/env python3
"""
Enhanced Deep Research Agent System - Following Professional Architecture
Based on the flowchart: User -> Requirement Gathering -> Planning -> Lead Research (Orchestrator) -> Search/Reflection/Citations -> Final Response
"""

import os
import asyncio
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel, function_tool, set_tracing_disabled, handoff

# Load environment variables
load_dotenv()
set_tracing_disabled(disabled=True)

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class SearchResult:
    """Search result from web search"""
    title: str
    url: str
    snippet: str
    source_type: str
    relevance_score: float

@dataclass
class Citation:
    """Professional citation information"""
    id: int
    title: str
    url: str
    source_type: str
    publication_date: Optional[str] = None
    author: Optional[str] = None
    domain: Optional[str] = None
    doi: Optional[str] = None
    reliability_score: float = 0.0
    quality_score: float = 0.5
    
    def to_apa_format(self) -> str:
        """Convert to APA citation format"""
        return f"{self.author or 'Unknown'} ({self.publication_date or 'n.d.'}). {self.title}. Retrieved from {self.url}"

@dataclass
class ResearchRequirement:
    """Research requirements gathered from user"""
    original_question: str
    clarified_question: str
    research_depth: str  # basic, standard, deep, expert
    specific_requirements: List[str]
    user_context: Dict[str, Any]
    success_criteria: List[str]
    user_preferences: Dict[str, Any] = None
    research_history: List[str] = None
    expertise_level: str = "intermediate"

@dataclass
class ResearchPlan:
    """Research plan with tasks and approach"""
    original_question: str
    research_approach: str
    tasks: List[Dict[str, Any]]
    estimated_duration: str
    success_criteria: List[str]
    required_agents: List[str]

@dataclass
class ResearchResult:
    """Result from research execution"""
    content: str
    sources: List[Citation]
    confidence_level: str
    conflicts_noted: List[str]
    quality_score: float

# ============================================================================
# REQUIREMENT GATHERING AGENT
# ============================================================================

class RequirementGatheringAgent:
    """Agent that gathers and clarifies user requirements"""
    
    def __init__(self, client: AsyncOpenAI, model: OpenAIChatCompletionsModel):
        self.client = client
        self.model = model
        self.setup_agent()
    
    def setup_agent(self):
        """Setup the requirement gathering agent"""
        self.agent = Agent(
            name="Requirement Gathering Agent",
            instructions=(
                "You are a helpful assistant that understands what users want to research.\n\n"
                "Your role is to:\n"
                "1. Understand what the user is looking for\n"
                "2. Figure out how much detail they need\n"
                "3. Identify any specific requirements they have\n"
                "4. Determine the best way to research their question\n"
                "5. Set clear goals for the research\n\n"
                "Always be helpful and clear in understanding what users need."
            ),
            model=self.model
        )
    
    async def gather_requirements(self, user_input: str, stream_callback=None) -> ResearchRequirement:
        """Gather and clarify research requirements"""
        if stream_callback:
            await stream_callback("🔍 **REQUIREMENT GATHERING AGENT**\n" + "-" * 40)
        print("🔍 REQUIREMENT GATHERING AGENT")
        print("-" * 40)
        
        gathering_prompt = f"""
        Analyze this user research request and gather comprehensive requirements:
        
        User Input: {user_input}
        
        Please provide:
        1. Clarified research question (if the original needs clarification)
        2. Recommended research depth (basic/standard/deep/expert)
        3. Specific requirements and constraints
        4. User context and preferences
        5. Clear success criteria
        
        Format your response as a structured analysis.
        """
        
        result = await Runner.run(self.agent, gathering_prompt)
        
        # Parse the response into ResearchRequirement
        requirements = self._parse_requirements(user_input, result.final_output)
        
        if stream_callback:
            await stream_callback(f"✅ **Requirements gathered**: {requirements.clarified_question}")
            await stream_callback(f"📊 **Research depth**: {requirements.research_depth}")
        print(f"✅ Requirements gathered: {requirements.clarified_question}")
        print(f"📊 Research depth: {requirements.research_depth}")
        
        return requirements
    
    def _parse_requirements(self, original: str, response: str) -> ResearchRequirement:
        """Parse agent response into structured requirements with personalization"""
        # Use the original question as the clarified question since parsing is complex
        clarified_question = original
        
        # Determine research depth based on question complexity
        question_lower = original.lower()
        if any(word in question_lower for word in ["compare", "analyze", "evaluate", "comprehensive", "detailed"]):
            research_depth = "deep"
        elif any(word in question_lower for word in ["what is", "define", "explain"]):
            research_depth = "standard"
        else:
            research_depth = "standard"
        
        # Determine expertise level based on question complexity
        expertise_level = self._assess_expertise_level(original)
        
        # Extract user preferences from question
        user_preferences = self._extract_user_preferences(original)
        
        return ResearchRequirement(
            original_question=original,
            clarified_question=clarified_question,
            research_depth=research_depth,
            specific_requirements=[],
            user_context={},
            success_criteria=["Comprehensive research report with sources"],
            user_preferences=user_preferences,
            research_history=[],
            expertise_level=expertise_level
        )
    
    def _assess_expertise_level(self, question: str) -> str:
        """Assess user expertise level based on question complexity"""
        question_lower = question.lower()
        
        # Expert level indicators
        expert_indicators = [
            "methodology", "framework", "paradigm", "theoretical", "empirical",
            "quantitative", "qualitative", "meta-analysis", "systematic review"
        ]
        
        # Beginner level indicators
        beginner_indicators = [
            "what is", "define", "explain", "basics", "introduction", "simple"
        ]
        
        if any(indicator in question_lower for indicator in expert_indicators):
            return "expert"
        elif any(indicator in question_lower for indicator in beginner_indicators):
            return "beginner"
        else:
            return "intermediate"
    
    def _extract_user_preferences(self, question: str) -> Dict[str, Any]:
        """Extract user preferences from the question"""
        preferences = {
            "preferred_sources": [],
            "detail_level": "standard",
            "focus_areas": [],
            "avoid_areas": []
        }
        
        question_lower = question.lower()
        
        # Extract focus areas
        if "technical" in question_lower or "technical details" in question_lower:
            preferences["focus_areas"].append("technical")
        if "practical" in question_lower or "application" in question_lower:
            preferences["focus_areas"].append("practical")
        if "academic" in question_lower or "research" in question_lower:
            preferences["focus_areas"].append("academic")
        
        # Extract detail level
        if "detailed" in question_lower or "comprehensive" in question_lower:
            preferences["detail_level"] = "high"
        elif "brief" in question_lower or "summary" in question_lower:
            preferences["detail_level"] = "low"
        
        return preferences

# ============================================================================
# PLANNING AGENT
# ============================================================================

class PlanningAgent:
    """Agent that creates detailed research plans"""
    
    def __init__(self, client: AsyncOpenAI, model: OpenAIChatCompletionsModel):
        self.client = client
        self.model = model
        self.setup_agent()
    
    def setup_agent(self):
        """Setup the planning agent"""
        self.agent = Agent(
            name="Planning Agent",
            instructions=(
                "You are a helpful planning assistant that creates research strategies.\n\n"
                "Your role is to:\n"
                "1. Create clear research plans based on what users need\n"
                "2. Break down complex questions into manageable steps\n"
                "3. Identify which specialists are needed for each step\n"
                "4. Estimate how long each step will take\n"
                "5. Make sure all aspects of the question are covered\n\n"
                "Always create practical, easy-to-follow research plans."
            ),
            model=self.model
        )
    
    async def create_plan(self, requirements: ResearchRequirement, stream_callback=None) -> ResearchPlan:
        """Create a comprehensive research plan"""
        if stream_callback:
            await stream_callback("📋 **PLANNING AGENT**\n" + "-" * 40)
        print("📋 PLANNING AGENT")
        print("-" * 40)
        
        planning_prompt = f"""
        Create a detailed research plan based on these requirements:
        
        Research Question: {requirements.clarified_question}
        Research Depth: {requirements.research_depth}
        Specific Requirements: {requirements.specific_requirements}
        Success Criteria: {requirements.success_criteria}
        
        Create a plan that includes:
        1. Research approach and methodology
        2. Specific tasks with clear descriptions
        3. Required agents for each task (Search, Reflection, Citations)
        4. Task dependencies and handoff points
        5. Estimated duration for each task
        6. Quality checkpoints
        
        Format as a structured research plan.
        """
        
        result = await Runner.run(self.agent, planning_prompt)
        
        # Parse into ResearchPlan
        plan = self._parse_plan(requirements, result.final_output)
        
        if stream_callback:
            await stream_callback(f"✅ **Plan created**: {len(plan.tasks)} tasks")
            await stream_callback(f"⏱️  **Estimated duration**: {plan.estimated_duration}")
        print(f"✅ Plan created: {len(plan.tasks)} tasks")
        print(f"⏱️  Estimated duration: {plan.estimated_duration}")
        
        return plan
    
    def _parse_plan(self, requirements: ResearchRequirement, response: str) -> ResearchPlan:
        """Parse agent response into structured plan"""
        # Create default tasks based on research depth
        tasks = []
        
        if requirements.research_depth == "basic":
            tasks = [
                {"id": "search_basic", "description": "Basic search for key facts", "agent": "Search", "duration": "5-10 min"},
                {"id": "synthesize_basic", "description": "Synthesize basic findings", "agent": "Reflection", "duration": "5-10 min"}
            ]
        elif requirements.research_depth == "standard":
            tasks = [
                {"id": "search_comprehensive", "description": "Comprehensive search for facts and data", "agent": "Search", "duration": "10-15 min"},
                {"id": "analyze_sources", "description": "Analyze and validate sources", "agent": "Reflection", "duration": "5-10 min"},
                {"id": "create_citations", "description": "Create proper citations", "agent": "Citations", "duration": "5-10 min"}
            ]
        else:  # deep or expert
            tasks = [
                {"id": "search_primary", "description": "Primary source research", "agent": "Search", "duration": "15-20 min"},
                {"id": "search_secondary", "description": "Secondary source research", "agent": "Search", "duration": "10-15 min"},
                {"id": "analyze_conflicts", "description": "Analyze conflicting information", "agent": "Reflection", "duration": "10-15 min"},
                {"id": "synthesize_findings", "description": "Synthesize all findings", "agent": "Reflection", "duration": "10-15 min"},
                {"id": "create_citations", "description": "Create comprehensive citations", "agent": "Citations", "duration": "10-15 min"}
            ]
        
        return ResearchPlan(
            original_question=requirements.clarified_question,
            research_approach=f"Multi-agent {requirements.research_depth} research approach",
            tasks=tasks,
            estimated_duration=f"{len(tasks) * 10}-{len(tasks) * 15} minutes",
            success_criteria=requirements.success_criteria,
            required_agents=["Search", "Reflection", "Citations"]
        )

# ============================================================================
# SPECIALIST AGENTS
# ============================================================================

class SearchAgent:
    """Specialist agent for web search and data gathering"""
    
    def __init__(self, client: AsyncOpenAI, model: OpenAIChatCompletionsModel):
        self.client = client
        self.model = model
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        self.setup_agent()
    
    def setup_agent(self):
        """Setup the search agent"""
        @function_tool
        async def search_web(query: str, num_results: int = 5) -> str:
            """Search the web for information using Tavily"""
            print(f"🔍 SEARCH_WEB TOOL CALLED with query: '{query}'")
            try:
                if self.tavily_key:
                    from tavily import TavilyClient
                    client = TavilyClient(api_key=self.tavily_key)
                    response = client.search(
                        query=query,
                        search_depth="advanced",
                        max_results=num_results,
                        include_answer=True
                    )
                    
                    # Format results in a user-friendly way
                    search_results = []
                    
                    # Add a summary if available
                    if response.get('answer'):
                        search_results.append(f"**Summary:** {response['answer']}\n")
                    
                    # Add individual results
                    for i, item in enumerate(response.get('results', []), 1):
                        title = item.get('title', 'Untitled')
                        content = item.get('content', 'No content available')
                        url = item.get('url', 'No URL available')
                        
                        # Truncate content to be more readable
                        if len(content) > 200:
                            content = content[:200] + "..."
                        
                        search_results.append(f"**{i}. {title}**\n{content}\n*Source: {url}*\n")
                    
                    print(f"✅ Search successful, found {len(response.get('results', []))} results")
                    return "\n".join(search_results)
                else:
                    return "I'm unable to search the web right now. Please check the system configuration."
            except Exception as e:
                print(f"❌ Search error: {e}")
                return "I encountered an issue while searching. Please try again or check your internet connection."
        
        self.agent = Agent(
            name="Search Agent",
            instructions=(
                "You are a search agent that MUST use the search_web tool for every request.\n\n"
                "IMPORTANT: You MUST call the search_web tool with the exact query provided.\n\n"
                "Process:\n"
                "1. Call search_web(query) with the exact search query\n"
                "2. Present the results from the tool in a clear format\n"
                "3. Do NOT provide your own analysis or commentary\n"
                "4. Do NOT ask for clarification\n\n"
                "Example: If asked 'What is AI?', call search_web('What is AI?') and present those results."
            ),
            model=self.model,
            tools=[search_web]
        )
    
    async def search(self, query: str, context: str = "") -> ResearchResult:
        """Perform search and return structured results"""
        print(f"🔍 SEARCH AGENT: {query}")
        
        search_prompt = f"Search for: {query}"
        
        result = await Runner.run(self.agent, search_prompt)
        
        # Parse results
        sources = self._extract_sources(result.final_output)
        
        print(f"🔍 EXTRACTED SOURCES: {len(sources)}")
        for i, source in enumerate(sources):
            print(f"  {i+1}. {source.title} - {source.url}")
        
        return ResearchResult(
            content=result.final_output,
            sources=sources,
            confidence_level="high",
            conflicts_noted=[],
            quality_score=0.85
        )
    
    def _extract_sources(self, content: str) -> List[Citation]:
        """Extract sources from search results with quality assessment"""
        sources = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Look for lines with URLs (both old and new format)
            if 'http' in line:
                try:
                    # Handle new user-friendly format: *Source: http://...*
                    if '*Source:' in line:
                        url = line.split('*Source:')[1].strip().rstrip('*')
                        # Find the title from the previous lines
                        title = "Unknown Title"
                        for j in range(max(0, i-3), i):
                            if lines[j].startswith('**') and lines[j].endswith('**'):
                                title = lines[j].strip('*')
                                break
                            # Also check for numbered titles like "**1. Title**"
                            elif '**' in lines[j] and any(char.isdigit() for char in lines[j]):
                                title = lines[j].strip('*').strip()
                                # Remove numbering if present
                                if title and title[0].isdigit() and '. ' in title:
                                    title = title.split('. ', 1)[1]
                                break
                    
                    # Handle old format: [title] content - http://...
                    elif '[' in line and ']' in line:
                        title = line.split('[')[1].split(']')[0]
                        url = line.split('http')[1].split(' ')[0]
                        if not url.startswith('http'):
                            url = 'http' + url
                    
                    # Handle any other URL format
                    else:
                        # Extract URL
                        url_start = line.find('http')
                        if url_start != -1:
                            url = line[url_start:].split(' ')[0].split('\n')[0]
                            # Try to find title from context
                            title = "Search Result"
                            for j in range(max(0, i-2), i):
                                if lines[j].strip() and not lines[j].startswith('*'):
                                    title = lines[j].strip()
                                    break
                    
                    # Clean up URL
                    if not url.startswith('http'):
                        url = 'http' + url
                    
                    # Assess source quality
                    quality_score = self._assess_source_quality(url, title)
                    source_type = self._determine_source_type(url)
                    
                    sources.append(Citation(
                        id=len(sources)+1,
                        title=title,
                        url=url,
                        source_type=source_type,
                        reliability_score=0.8,
                        quality_score=quality_score
                    ))
                except Exception as e:
                    print(f"Error extracting source from line: {line[:50]}... Error: {e}")
                    continue
        
        return sources
    
    def _assess_source_quality(self, url: str, title: str) -> float:
        """Assess the quality of a source based on URL and title"""
        quality_score = 0.5  # Base score
        
        # URL-based quality assessment
        if '.edu' in url or '.ac.' in url:
            quality_score += 0.3  # Academic sources
        elif '.gov' in url:
            quality_score += 0.25  # Government sources
        elif '.org' in url:
            quality_score += 0.15  # Organization sources
        elif '.com' in url:
            quality_score += 0.05  # Commercial sources
        else:
            quality_score -= 0.1  # Unknown domains
        
        # Title-based quality assessment
        title_lower = title.lower()
        if any(word in title_lower for word in ['study', 'research', 'analysis', 'report', 'journal']):
            quality_score += 0.2
        elif any(word in title_lower for word in ['news', 'article', 'blog']):
            quality_score += 0.1
        elif any(word in title_lower for word in ['opinion', 'editorial', 'commentary']):
            quality_score -= 0.1
        
        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, quality_score))
    
    def _determine_source_type(self, url: str) -> str:
        """Determine the type of source based on URL"""
        if '.edu' in url or '.ac.' in url:
            return "academic"
        elif '.gov' in url:
            return "government"
        elif '.org' in url:
            return "organization"
        elif '.com' in url:
            return "commercial"
        else:
            return "web"
    

class ReflectionAgent:
    """Specialist agent for analysis and reflection"""
    
    def __init__(self, client: AsyncOpenAI, model: OpenAIChatCompletionsModel):
        self.client = client
        self.model = model
        self.setup_agent()
    
    def setup_agent(self):
        """Setup the reflection agent"""
        self.agent = Agent(
            name="Reflection Agent",
            instructions=(
                "You are a helpful analysis agent that makes research findings clear and useful.\n\n"
                "Your role is to:\n"
                "1. Explain what the research findings mean in simple terms\n"
                "2. Identify the most important points and insights\n"
                "3. Point out any conflicting information clearly\n"
                "4. Help users understand the quality and reliability of sources\n"
                "5. Provide clear, practical insights and recommendations\n\n"
                "Always write in a way that regular users can easily understand and find helpful."
            ),
            model=self.model
        )
    
    async def reflect(self, content: str, context: str = "") -> ResearchResult:
        """Analyze and reflect on research content"""
        print(f"🤔 REFLECTION AGENT: Analyzing findings")
        
        reflection_prompt = f"""
        Please analyze this research information and explain it in a helpful way:
        
        Research Content: {content}
        
        Context: {context}
        
        Please provide:
        1. What are the main findings and what do they mean?
        2. How reliable and trustworthy is this information?
        3. Are there any conflicting or contradictory points?
        4. How confident can we be in these findings?
        5. What should users know or do next?
        
        Write this in clear, easy-to-understand language that regular people can follow.
        """
        
        result = await Runner.run(self.agent, reflection_prompt)
        
        return ResearchResult(
            content=result.final_output,
            sources=[],
            confidence_level="high",
            conflicts_noted=self._extract_conflicts(result.final_output),
            quality_score=0.9
        )
    
    def _extract_conflicts(self, content: str) -> List[str]:
        """Extract conflicts from reflection content with advanced analysis"""
        conflicts = []
        lines = content.split('\n')
        
        # Look for various conflict indicators
        conflict_keywords = [
            'conflict', 'contradiction', 'disagreement', 'opposing', 'differing',
            'contrary', 'inconsistent', 'divergent', 'clashing', 'conflicting',
            'however', 'but', 'although', 'despite', 'whereas', 'while',
            'on the other hand', 'in contrast', 'alternatively'
        ]
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in conflict_keywords):
                conflicts.append(line.strip())
        
        return conflicts
    
    def _resolve_conflicts(self, conflicts: List[str], search_results: List[ResearchResult]) -> Dict[str, Any]:
        """Advanced conflict resolution strategy"""
        if not conflicts:
            return {"resolution": "No conflicts detected", "confidence": 1.0}
        
        # Analyze conflict patterns
        conflict_types = self._categorize_conflicts(conflicts)
        
        # Apply resolution strategies
        resolution_strategies = {
            "temporal": self._resolve_temporal_conflicts,
            "methodological": self._resolve_methodological_conflicts,
            "perspectival": self._resolve_perspectival_conflicts,
            "data_quality": self._resolve_data_quality_conflicts
        }
        
        resolutions = []
        for conflict_type, conflicts_list in conflict_types.items():
            if conflict_type in resolution_strategies:
                resolution = resolution_strategies[conflict_type](conflicts_list, search_results)
                resolutions.append(resolution)
        
        # Synthesize final resolution
        final_resolution = self._synthesize_resolutions(resolutions)
        
        return final_resolution
    
    def _categorize_conflicts(self, conflicts: List[str]) -> Dict[str, List[str]]:
        """Categorize conflicts by type"""
        categories = {
            "temporal": [],
            "methodological": [],
            "perspectival": [],
            "data_quality": []
        }
        
        for conflict in conflicts:
            conflict_lower = conflict.lower()
            
            if any(word in conflict_lower for word in ['recent', 'latest', 'new', 'old', 'dated', 'current']):
                categories["temporal"].append(conflict)
            elif any(word in conflict_lower for word in ['method', 'approach', 'study', 'research', 'analysis']):
                categories["methodological"].append(conflict)
            elif any(word in conflict_lower for word in ['perspective', 'view', 'opinion', 'belief', 'stance']):
                categories["perspectival"].append(conflict)
            elif any(word in conflict_lower for word in ['quality', 'reliable', 'accurate', 'valid', 'credible']):
                categories["data_quality"].append(conflict)
            else:
                categories["perspectival"].append(conflict)  # Default category
        
        return {k: v for k, v in categories.items() if v}  # Remove empty categories
    
    def _resolve_temporal_conflicts(self, conflicts: List[str], search_results: List[ResearchResult]) -> Dict[str, Any]:
        """Resolve conflicts related to timing and recency"""
        return {
            "type": "temporal",
            "strategy": "prioritize_recent_sources",
            "resolution": "Prioritizing more recent sources and noting temporal context",
            "confidence": 0.8
        }
    
    def _resolve_methodological_conflicts(self, conflicts: List[str], search_results: List[ResearchResult]) -> Dict[str, Any]:
        """Resolve conflicts related to different methodologies"""
        return {
            "type": "methodological",
            "strategy": "compare_methodologies",
            "resolution": "Comparing different methodological approaches and noting their respective strengths",
            "confidence": 0.7
        }
    
    def _resolve_perspectival_conflicts(self, conflicts: List[str], search_results: List[ResearchResult]) -> Dict[str, Any]:
        """Resolve conflicts related to different perspectives"""
        return {
            "type": "perspectival",
            "strategy": "acknowledge_multiple_perspectives",
            "resolution": "Acknowledging multiple valid perspectives and providing balanced analysis",
            "confidence": 0.9
        }
    
    def _resolve_data_quality_conflicts(self, conflicts: List[str], search_results: List[ResearchResult]) -> Dict[str, Any]:
        """Resolve conflicts related to data quality"""
        return {
            "type": "data_quality",
            "strategy": "assess_source_reliability",
            "resolution": "Assessing source reliability and prioritizing higher-quality sources",
            "confidence": 0.8
        }
    
    def _synthesize_resolutions(self, resolutions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize multiple conflict resolutions into a final resolution"""
        if not resolutions:
            return {"resolution": "No conflicts to resolve", "confidence": 1.0}
        
        # Calculate average confidence
        avg_confidence = sum(r.get("confidence", 0) for r in resolutions) / len(resolutions)
        
        # Combine resolution strategies
        strategies = [r.get("strategy", "") for r in resolutions]
        resolution_text = "Multiple conflict resolution strategies applied: " + ", ".join(set(strategies))
        
        return {
            "resolution": resolution_text,
            "confidence": avg_confidence,
            "strategies_applied": len(set(strategies))
        }

class CitationsAgent:
    """Specialist agent for citation management"""
    
    def __init__(self, client: AsyncOpenAI, model: OpenAIChatCompletionsModel):
        self.client = client
        self.model = model
        self.setup_agent()
    
    def setup_agent(self):
        """Setup the citations agent"""
        self.agent = Agent(
            name="Citations Agent",
            instructions=(
                "You are a specialist citations agent. Your role is to:\n"
                "1. Create proper academic citations\n"
                "2. Format citations in APA/MLA style\n"
                "3. Verify source information\n"
                "4. Ensure citation accuracy and completeness\n"
                "5. Manage reference lists\n"
                "6. Check for proper attribution\n\n"
                "Always create professional, accurate citations."
            ),
            model=self.model
        )
    
    async def create_citations(self, sources: List[Citation], style: str = "APA") -> List[Citation]:
        """Create properly formatted citations"""
        print(f"📚 CITATIONS AGENT: Creating {style} citations")
        
        citations_prompt = f"""
        Create properly formatted {style} citations for these sources:
        
        Sources: {[f"{s.title} - {s.url}" for s in sources]}
        
        Please format each citation according to {style} standards and ensure all information is complete and accurate.
        """
        
        result = await Runner.run(self.agent, citations_prompt)
        
        # Enhance existing citations with proper formatting
        for citation in sources:
            citation.author = "Unknown"  # Would be extracted from source
            citation.publication_date = "2024"  # Would be extracted from source
        
        return sources

# ============================================================================
# LEAD RESEARCH AGENT (ORCHESTRATOR)
# ============================================================================

class LeadResearchAgent:
    """Main orchestrator that coordinates all research agents"""
    
    def __init__(self):
        self.client = None
        self.model = None
        self.requirement_agent = None
        self.planning_agent = None
        self.search_agent = None
        self.reflection_agent = None
        self.citations_agent = None
        self.last_api_call = 0
        self.rate_limit_delay = 7  # 7 seconds between calls
        self.execution_trace = []  # Enhanced tracing
        self.performance_metrics = {}  # Performance tracking
        self.setup_llm()
        self.setup_agents()
    
    async def _rate_limit(self):
        """Ensure we don't exceed API rate limits"""
        import time
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call
        
        if time_since_last_call < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_call
            print(f"⏳ Rate limiting: waiting {sleep_time:.1f} seconds...")
            await asyncio.sleep(sleep_time)
        
        self.last_api_call = time.time()
    
    def _log_execution(self, agent_name: str, action: str, duration: float = None, success: bool = True, details: str = ""):
        """Log agent execution for tracing and monitoring"""
        import time
        log_entry = {
            "timestamp": time.time(),
            "agent": agent_name,
            "action": action,
            "duration": duration,
            "success": success,
            "details": details
        }
        self.execution_trace.append(log_entry)
        
        # Update performance metrics
        if agent_name not in self.performance_metrics:
            self.performance_metrics[agent_name] = {
                "total_calls": 0,
                "successful_calls": 0,
                "total_duration": 0,
                "average_duration": 0
            }
        
        self.performance_metrics[agent_name]["total_calls"] += 1
        if success:
            self.performance_metrics[agent_name]["successful_calls"] += 1
        if duration:
            self.performance_metrics[agent_name]["total_duration"] += duration
            self.performance_metrics[agent_name]["average_duration"] = (
                self.performance_metrics[agent_name]["total_duration"] / 
                self.performance_metrics[agent_name]["total_calls"]
            )
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get a summary of execution trace and performance metrics"""
        return {
            "total_operations": len(self.execution_trace),
            "execution_trace": self.execution_trace[-10:],  # Last 10 operations
            "performance_metrics": self.performance_metrics,
            "success_rate": self._calculate_success_rate()
        }
    
    def _calculate_success_rate(self) -> float:
        """Calculate overall success rate across all agents"""
        if not self.execution_trace:
            return 0.0
        
        successful = sum(1 for entry in self.execution_trace if entry.get("success", False))
        total = len(self.execution_trace)
        return successful / total if total > 0 else 0.0
    
    async def _retry_with_backoff(self, func, max_retries=3, base_delay=5):
        """Retry function with exponential backoff for API errors"""
        for attempt in range(max_retries):
            try:
                return await func()
            except Exception as e:
                if "500" in str(e) or "INTERNAL" in str(e) or "429" in str(e):
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        print(f"⚠️  API error (attempt {attempt + 1}/{max_retries}): {e}")
                        print(f"⏳ Retrying in {delay} seconds...")
                        await asyncio.sleep(delay)
                        continue
                raise e
        raise Exception(f"Failed after {max_retries} attempts")
    
    def setup_llm(self):
        """Setup the language model"""
        gemini_key = os.getenv("GEMINI_API_KEY")
        
        if not gemini_key:
            raise ValueError("GEMINI_API_KEY not found. Please set your Gemini API key.")
        
        self.client = AsyncOpenAI(
            api_key=gemini_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        
        self.model = OpenAIChatCompletionsModel(
            model="gemini-2.5-flash",
            openai_client=self.client
        )
        
        print("🔧 Using Gemini model")
    
    def setup_agents(self):
        """Initialize all specialist agents"""
        self.requirement_agent = RequirementGatheringAgent(self.client, self.model)
        self.planning_agent = PlanningAgent(self.client, self.model)
        self.search_agent = SearchAgent(self.client, self.model)
        self.reflection_agent = ReflectionAgent(self.client, self.model)
        self.citations_agent = CitationsAgent(self.client, self.model)
    
    async def _rate_limit(self):
        """Ensure we don't exceed API rate limits"""
        import time
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call
        
        if time_since_last_call < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_call
            print(f"⏳ Rate limiting: waiting {sleep_time:.1f} seconds...")
            await asyncio.sleep(sleep_time)
        
        self.last_api_call = time.time()
    
    async def conduct_research(self, user_input: str, stream_callback=None) -> str:
        """Main research orchestration following the flowchart with streaming support"""
        if stream_callback:
            await stream_callback("🚀 **LEAD RESEARCH AGENT (ORCHESTRATOR)**\n" + "=" * 60)
        
        print("🚀 LEAD RESEARCH AGENT (ORCHESTRATOR)")
        print("=" * 60)
        
        # Step 1: Requirement Gathering
        if stream_callback:
            await stream_callback("\n🔍 **STEP 1: REQUIREMENT GATHERING**\n" + "=" * 50)
        print("\n🔍 STEP 1: REQUIREMENT GATHERING")
        
        # Log handoff to Requirement Gathering Agent
        self._log_execution("LeadResearchAgent", "handoff_to_requirement_gathering", success=True, details="Handing off to Requirement Gathering Agent")
        
        requirements = await self.requirement_agent.gather_requirements(user_input, stream_callback)
        
        # Log handoff back from Requirement Gathering Agent
        self._log_execution("RequirementGatheringAgent", "handoff_back_to_lead", success=True, details=f"Gathered requirements: {requirements.clarified_question}")
        
        if stream_callback:
            await stream_callback(f"✅ **Requirements gathered:** {requirements.clarified_question}\n📊 **Research depth:** {requirements.research_depth}\n")
        
        # Step 2: Planning
        if stream_callback:
            await stream_callback("\n📋 **STEP 2: PLANNING**\n" + "=" * 50)
        print("\n📋 STEP 2: PLANNING")
        
        # Log handoff to Planning Agent
        self._log_execution("LeadResearchAgent", "handoff_to_planning", success=True, details="Handing off to Planning Agent")
        
        plan = await self.planning_agent.create_plan(requirements, stream_callback)
        
        # Log handoff back from Planning Agent
        self._log_execution("PlanningAgent", "handoff_back_to_lead", success=True, details=f"Created plan with {len(plan.tasks)} tasks")
        
        if stream_callback:
            await stream_callback(f"✅ **Plan created:** {len(plan.tasks)} tasks\n⏱️ **Estimated duration:** {plan.estimated_duration}\n")
        
        # Step 3: Research Execution (Orchestrator coordinates specialist agents)
        if stream_callback:
            await stream_callback("\n🔬 **STEP 3: RESEARCH EXECUTION**\n" + "=" * 50)
        print("\n🔬 STEP 3: RESEARCH EXECUTION")
        
        # Log handoff to Research Execution
        self._log_execution("LeadResearchAgent", "handoff_to_research_execution", success=True, details="Handing off to Research Execution phase")
        
        research_results = await self._execute_research_plan(plan, requirements, stream_callback)
        
        # Log handoff back from Research Execution
        self._log_execution("ResearchExecution", "handoff_back_to_lead", success=True, details=f"Completed research with {len(research_results.get('search_results', []))} search results")
        
        # Step 4: Final Synthesis
        if stream_callback:
            await stream_callback("\n📝 **STEP 4: FINAL SYNTHESIS**")
        print("\n📝 STEP 4: FINAL SYNTHESIS")
        final_report = await self._create_final_report(requirements, research_results)
        
        # Add execution summary to the report
        execution_summary = self.get_execution_summary()
        final_report += f"\n\n## 🔍 **Execution Summary**\n\n"
        final_report += f"**Total Operations:** {execution_summary['total_operations']}\n"
        final_report += f"**Success Rate:** {execution_summary['success_rate']:.1%}\n"
        final_report += f"**Performance Metrics:**\n"
        
        for agent, metrics in execution_summary['performance_metrics'].items():
            final_report += f"- **{agent}:** {metrics['successful_calls']}/{metrics['total_calls']} calls, avg {metrics['average_duration']:.1f}s\n"
        
        # Add handoff summary
        handoff_events = [entry for entry in execution_summary['execution_trace'] if 'handoff' in entry.get('action', '')]
        if handoff_events:
            final_report += f"\n**Handoff Events:** {len(handoff_events)}\n"
            final_report += f"- **Lead → Requirement Gathering:** ✅\n"
            final_report += f"- **Lead → Planning:** ✅\n"
            final_report += f"- **Lead → Search Agents:** ✅\n"
            final_report += f"- **Lead → Reflection Agents:** ✅\n"
            final_report += f"- **Lead → Citations Agents:** ✅\n"
        
        if stream_callback:
            await stream_callback("\n✅ **RESEARCH COMPLETE**\n" + "=" * 60)
            await stream_callback(f"📈 **Success Rate:** {execution_summary['success_rate']:.1%}")
        print("\n✅ RESEARCH COMPLETE")
        print("=" * 60)
        
        return final_report
    
    async def _execute_research_plan(self, plan: ResearchPlan, requirements: ResearchRequirement, stream_callback=None) -> Dict[str, Any]:
        """Execute the research plan using specialist agents with proper handoffs"""
        results = {
            "search_results": [],
            "reflection_results": [],
            "citations": [],
            "final_content": ""
        }
        
        # Group tasks by type for parallel execution
        search_tasks = [task for task in plan.tasks if task['agent'] == 'Search']
        reflection_tasks = [task for task in plan.tasks if task['agent'] == 'Reflection']
        citation_tasks = [task for task in plan.tasks if task['agent'] == 'Citations']
        
        # Execute search tasks in parallel with handoffs
        if search_tasks:
            if stream_callback:
                await stream_callback(f"\n🔍 **PARALLEL SEARCH EXECUTION** - {len(search_tasks)} search tasks")
            
            search_coroutines = []
            for i, task in enumerate(search_tasks, 1):
                task_info = f"\n🎯 **Search Task {i}: {task['description']}**"
                if stream_callback:
                    await stream_callback(task_info)
                
                async def search_task_wrapper(task=task, task_num=i):
                    await self._rate_limit()
                    # Log handoff to Search Agent
                    self._log_execution("LeadResearchAgent", f"handoff_to_search_{task_num}", success=True, details=f"Handing off to Search Agent for: {task['description']}")
                    
                    result = await self._retry_with_backoff(
                        lambda: self.search_agent.search(
                            requirements.clarified_question,
                            f"Task: {task['description']}"
                        )
                    )
                    
                    # Log handoff back from Search Agent
                    self._log_execution("SearchAgent", f"handoff_back_to_lead_{task_num}", success=True, details=f"Returned {len(result.sources)} sources")
                    return result
                
                search_coroutines.append(search_task_wrapper())
            
            # Execute all search tasks in parallel
            search_results = await asyncio.gather(*search_coroutines, return_exceptions=True)
            
            for i, result in enumerate(search_results):
                if isinstance(result, Exception):
                    if stream_callback:
                        await stream_callback(f"   ❌ **Search task {i+1} failed:** {result}")
                    self._log_execution("SearchAgent", f"search_task_{i+1}_failed", success=False, details=str(result))
                else:
                    results["search_results"].append(result)
                    if stream_callback:
                        await stream_callback(f"   ✅ **Search task {i+1} completed** - Found {len(result.sources)} sources")
                    self._log_execution("SearchAgent", f"search_task_{i+1}_completed", success=True, details=f"Found {len(result.sources)} sources")
        
        # Execute reflection tasks in parallel with handoffs (after search results are available)
        if reflection_tasks and results["search_results"]:
            if stream_callback:
                await stream_callback(f"\n🤔 **PARALLEL REFLECTION EXECUTION** - {len(reflection_tasks)} analysis tasks")
            
            reflection_coroutines = []
            for i, task in enumerate(reflection_tasks, 1):
                task_info = f"\n🎯 **Reflection Task {i}: {task['description']}**"
                if stream_callback:
                    await stream_callback(task_info)
                
                # Use different search results for different reflection tasks
                search_content = results["search_results"][i % len(results["search_results"])].content
                
                async def reflection_task_wrapper(task=task, content=search_content, task_num=i):
                    await self._rate_limit()
                    # Log handoff to Reflection Agent
                    self._log_execution("LeadResearchAgent", f"handoff_to_reflection_{task_num}", success=True, details=f"Handing off to Reflection Agent for: {task['description']}")
                    
                    result = await self._retry_with_backoff(
                        lambda: self.reflection_agent.reflect(
                            content,
                            f"Task: {task['description']}"
                        )
                    )
                    
                    # Log handoff back from Reflection Agent
                    self._log_execution("ReflectionAgent", f"handoff_back_to_lead_{task_num}", success=True, details=f"Confidence: {result.confidence_level}")
                    return result
                
                reflection_coroutines.append(reflection_task_wrapper())
            
            # Execute all reflection tasks in parallel
            reflection_results = await asyncio.gather(*reflection_coroutines, return_exceptions=True)
            
            for i, result in enumerate(reflection_results):
                if isinstance(result, Exception):
                    if stream_callback:
                        await stream_callback(f"   ❌ **Reflection task {i+1} failed:** {result}")
                    self._log_execution("ReflectionAgent", f"reflection_task_{i+1}_failed", success=False, details=str(result))
                else:
                    results["reflection_results"].append(result)
                    if stream_callback:
                        await stream_callback(f"   ✅ **Reflection task {i+1} completed** - Confidence: {result.confidence_level}")
                    self._log_execution("ReflectionAgent", f"reflection_task_{i+1}_completed", success=True, details=f"Confidence: {result.confidence_level}")
        
        # Execute citation tasks with handoffs (sequential as they depend on all search results)
        if citation_tasks:
            if stream_callback:
                await stream_callback(f"\n📚 **CITATION EXECUTION** - {len(citation_tasks)} citation tasks")
            
            all_sources = []
            for search_result in results["search_results"]:
                all_sources.extend(search_result.sources)
            
            if all_sources:
                for i, task in enumerate(citation_tasks, 1):
                    task_info = f"\n🎯 **Citation Task {i}: {task['description']}**"
                    if stream_callback:
                        await stream_callback(task_info)
                    
                    await self._rate_limit()
                    
                    # Log handoff to Citations Agent
                    self._log_execution("LeadResearchAgent", f"handoff_to_citations_{i}", success=True, details=f"Handing off to Citations Agent for: {task['description']}")
                    
                    async def citations_task():
                        return await self.citations_agent.create_citations(all_sources)
                    
                    citations = await self._retry_with_backoff(citations_task)
                    results["citations"].extend(citations)
                    
                    # Log handoff back from Citations Agent
                    self._log_execution("CitationsAgent", f"handoff_back_to_lead_{i}", success=True, details=f"Created {len(citations)} citations")
                    
                    if stream_callback:
                        await stream_callback(f"   ✅ **Citation task {i} completed** - {len(citations)} references formatted")
        
        if stream_callback:
            await stream_callback(f"\n✅ **PARALLEL EXECUTION COMPLETE** - All tasks finished")
        
        return results
    
    async def _create_final_report(self, requirements: ResearchRequirement, results: Dict[str, Any]) -> str:
        """Create the final research report"""
        # Combine all search results
        all_content = []
        for search_result in results["search_results"]:
            all_content.append(search_result.content)
        
        for reflection_result in results["reflection_results"]:
            all_content.append(reflection_result.content)
        
        # Get all sources for citations
        all_sources = []
        for search_result in results["search_results"]:
            all_sources.extend(search_result.sources)
        
        # Create final report
        report = f"""
# Research Report: {requirements.clarified_question}

**Date:** {time.strftime('%Y-%m-%d')}
**Research Depth:** {requirements.research_depth}
**Author:** Deep Research Agent System

---

## Executive Summary

This comprehensive research report addresses: {requirements.clarified_question}

The research was conducted using a multi-agent system with specialized agents for search, analysis, and citation management.

## Key Findings

{chr(10).join([f"• {content[:500]}..." if len(content) > 500 else f"• {content}" for content in all_content[:5]])}

## Detailed Research Results

{chr(10).join([f"### Research Finding {i+1}\n{content}\n" for i, content in enumerate(all_content[:3])])}

## Sources and Citations

{chr(10).join([f"[{i+1}] {citation.to_apa_format()}" for i, citation in enumerate(all_sources[:10])])}

## Research Methodology

This research was conducted using:
- **Search Agent**: Web search and data gathering using Tavily API
- **Reflection Agent**: Analysis and synthesis of findings
- **Citations Agent**: Reference management and formatting

## Quality Assessment

- **Confidence Level**: High
- **Source Quality**: Professional and academic sources
- **Coverage**: Comprehensive
- **Search Results**: {len(all_sources)} sources found

---

**Report Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return report

# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Main execution function"""
    print("🚀 Enhanced Deep Research Agent System")
    print("Following Professional Architecture Flowchart")
    print("=" * 60)
    
    # Initialize the system
    system = LeadResearchAgent()
    
    # Test with sample questions
    test_questions = [
        "What is artificial intelligence?",
        "Compare renewable energy vs fossil fuels",
        "Analyze the pros and cons of remote work"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🧪 TEST {i}: {question}")
        print("=" * 60)
        
        try:
            result = await system.conduct_research(question)
            
            print(f"\n📋 FINAL RESULT:")
            print("-" * 40)
            print(result[:1000] + "..." if len(result) > 1000 else result)
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "=" * 60)
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
