from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Dict, Any, List
import re
import json

class SearchQueryOptimizerInput(BaseModel):
    """Input schema for Smart Search Query Optimizer Tool."""
    base_query: str = Field(
        ..., 
        description="The original search query to optimize"
    )
    search_context: str = Field(
        ..., 
        description="Context for the search (e.g., 'job search', 'talent acquisition', 'market research')"
    )
    target_results: int = Field(
        default=50, 
        description="Target number of search results desired"
    )
    optimization_level: str = Field(
        default="balanced", 
        description="Level of optimization: 'conservative', 'balanced', or 'aggressive'"
    )

class SmartSearchQueryOptimizer(BaseTool):
    """Tool for optimizing search queries through predictive keyword expansion and effectiveness scoring."""

    name: str = "Smart Search Query Optimizer"
    description: str = (
        "Optimizes search queries by expanding keywords, generating multiple search variations, "
        "scoring effectiveness, and providing strategic search sequences for maximum coverage. "
        "Supports conservative, balanced, and aggressive optimization approaches."
    )
    args_schema: Type[BaseModel] = SearchQueryOptimizerInput

    def _run(self, base_query: str, search_context: str, target_results: int = 50, optimization_level: str = "balanced") -> str:
        try:
            # Industry and context-specific keyword mappings
            industry_keywords = {
                "job search": {
                    "software": ["developer", "engineer", "programmer", "architect", "analyst"],
                    "management": ["manager", "director", "lead", "supervisor", "head"],
                    "sales": ["representative", "executive", "specialist", "consultant", "coordinator"],
                    "marketing": ["specialist", "coordinator", "manager", "analyst", "strategist"],
                    "finance": ["analyst", "accountant", "controller", "advisor", "planner"]
                },
                "talent acquisition": {
                    "technical": ["full-stack", "backend", "frontend", "devops", "cloud"],
                    "experience": ["junior", "senior", "mid-level", "expert", "principal"],
                    "skills": ["agile", "scrum", "leadership", "communication", "problem-solving"],
                    "education": ["degree", "certification", "training", "bootcamp", "course"]
                },
                "market research": {
                    "business": ["enterprise", "startup", "corporation", "company", "organization"],
                    "industry": ["technology", "healthcare", "finance", "retail", "manufacturing"],
                    "metrics": ["growth", "revenue", "market share", "trends", "analysis"],
                    "competitive": ["competitor", "landscape", "positioning", "advantage", "strategy"]
                }
            }

            # Synonyms and related terms
            synonym_map = {
                "developer": ["programmer", "engineer", "coder", "dev"],
                "manager": ["supervisor", "director", "lead", "head"],
                "analyst": ["specialist", "consultant", "researcher", "expert"],
                "software": ["application", "program", "system", "platform"],
                "company": ["organization", "corporation", "business", "firm"],
                "experience": ["expertise", "background", "skills", "knowledge"],
                "remote": ["virtual", "distributed", "telecommute", "work from home"],
                "senior": ["experienced", "advanced", "expert", "principal"],
                "junior": ["entry-level", "associate", "trainee", "beginner"]
            }

            # Extract key terms from base query
            query_terms = self._extract_key_terms(base_query.lower())
            
            # Generate keyword expansions
            keyword_expansions = self._generate_keyword_expansions(
                query_terms, search_context.lower(), industry_keywords, synonym_map
            )

            # Generate search variations
            optimized_queries = self._generate_search_variations(
                base_query, keyword_expansions, optimization_level, target_results
            )

            # Calculate effectiveness scores
            effectiveness_scores = self._calculate_effectiveness_scores(
                optimized_queries, target_results, search_context
            )

            # Create search sequence
            search_sequence = self._create_optimal_search_sequence(
                optimized_queries, effectiveness_scores
            )

            # Analyze coverage overlap
            coverage_analysis = self._analyze_coverage_overlap(optimized_queries)

            # Generate optimization tips
            optimization_tips = self._generate_optimization_tips(
                base_query, search_context, optimization_level, keyword_expansions
            )

            # Prepare result
            result = {
                "optimized_queries": optimized_queries,
                "keyword_expansions": keyword_expansions,
                "search_sequence": search_sequence,
                "effectiveness_scores": effectiveness_scores,
                "coverage_analysis": coverage_analysis,
                "optimization_tips": optimization_tips
            }

            return json.dumps(result, indent=2)

        except Exception as e:
            return f"Error optimizing search query: {str(e)}"

    def _extract_key_terms(self, query: str) -> List[str]:
        """Extract key terms from the base query."""
        # Remove common stop words and extract meaningful terms
        stop_words = {"and", "or", "the", "a", "an", "in", "on", "at", "to", "for", "of", "with", "by"}
        
        # Clean and split query
        cleaned_query = re.sub(r'[^\w\s]', ' ', query)
        terms = [term.strip() for term in cleaned_query.split() if term.strip() and term not in stop_words]
        
        return list(set(terms))

    def _generate_keyword_expansions(self, query_terms: List[str], context: str, 
                                   industry_keywords: Dict, synonym_map: Dict) -> Dict[str, List[str]]:
        """Generate keyword expansions based on context and industry knowledge."""
        expansions = {}
        
        for term in query_terms:
            expanded = [term]  # Start with original term
            
            # Add synonyms
            if term in synonym_map:
                expanded.extend(synonym_map[term])
            
            # Add industry-specific expansions
            for industry, categories in industry_keywords.items():
                if industry in context:
                    for category, keywords in categories.items():
                        if term in keywords or any(keyword in term for keyword in keywords):
                            expanded.extend(keywords[:3])  # Limit to top 3
            
            # Add related terms based on partial matches
            for key, synonyms in synonym_map.items():
                if term in key or key in term:
                    expanded.extend(synonyms[:2])  # Limit to top 2
            
            # Remove duplicates and original term for display
            expansions[term] = list(set([exp for exp in expanded if exp != term]))[:5]
        
        return expansions

    def _generate_search_variations(self, base_query: str, expansions: Dict, 
                                  optimization_level: str, target_results: int) -> List[Dict[str, Any]]:
        """Generate different search query variations."""
        variations = []
        
        # Conservative approach - exact match focused
        conservative_query = f'"{base_query}"'
        variations.append({
            "query": conservative_query,
            "approach": "conservative",
            "description": "Exact match focused for precise results"
        })

        # Balanced approach - mix of exact and expanded terms
        balanced_terms = []
        for term, expanded in expansions.items():
            if expanded:
                balanced_terms.append(f"({term} OR {expanded[0]})")
            else:
                balanced_terms.append(term)
        
        balanced_query = " AND ".join(balanced_terms)
        variations.append({
            "query": balanced_query,
            "approach": "balanced",
            "description": "Mix of exact and expanded terms for balanced coverage"
        })

        # Aggressive approach - broad keyword expansion
        aggressive_terms = []
        for term, expanded in expansions.items():
            all_terms = [term] + expanded[:3]  # Include up to 3 expansions
            aggressive_terms.append(f"({' OR '.join(all_terms)})")
        
        aggressive_query = " AND ".join(aggressive_terms)
        variations.append({
            "query": aggressive_query,
            "approach": "aggressive",
            "description": "Broad keyword expansion for maximum coverage"
        })

        # Boolean combination variations
        if len(expansions) >= 2:
            terms_list = list(expansions.keys())
            boolean_query = f"({terms_list[0]} AND {terms_list[1]}) OR ({terms_list[0]} AND {' OR '.join(expansions[terms_list[0]][:2])})"
            variations.append({
                "query": boolean_query,
                "approach": "boolean_hybrid",
                "description": "Strategic Boolean combinations for targeted results"
            })

        # Phrase-based variation
        key_phrases = base_query.split()
        if len(key_phrases) >= 2:
            phrase_query = f'"{" ".join(key_phrases[:2])}" AND ({" OR ".join(key_phrases[2:] if len(key_phrases) > 2 else list(expansions.keys())[:2])})'
            variations.append({
                "query": phrase_query,
                "approach": "phrase_focused",
                "description": "Phrase-based search with keyword flexibility"
            })

        return variations

    def _calculate_effectiveness_scores(self, queries: List[Dict], target_results: int, context: str) -> Dict[str, int]:
        """Calculate predicted effectiveness scores for each query."""
        scores = {}
        
        for query_info in queries:
            query = query_info["query"]
            approach = query_info["approach"]
            
            base_score = 50  # Starting score
            
            # Score based on approach
            approach_scores = {
                "conservative": 70,  # High precision, lower recall
                "balanced": 85,      # Good balance
                "aggressive": 75,    # High recall, lower precision
                "boolean_hybrid": 80,
                "phrase_focused": 78
            }
            base_score = approach_scores.get(approach, 50)
            
            # Adjust based on query complexity
            complexity_factor = len(query.split()) / 10
            if complexity_factor > 1:
                base_score -= 5  # Penalty for overly complex queries
            
            # Adjust based on Boolean operators
            boolean_count = query.count("AND") + query.count("OR")
            if boolean_count > 3:
                base_score -= 10  # Penalty for too many operators
            
            # Adjust based on target results
            if target_results < 20:
                if approach == "conservative":
                    base_score += 10
            elif target_results > 100:
                if approach == "aggressive":
                    base_score += 10
            
            # Ensure score is within bounds
            final_score = max(10, min(100, base_score))
            scores[query] = final_score
        
        return scores

    def _create_optimal_search_sequence(self, queries: List[Dict], scores: Dict[str, int]) -> List[Dict[str, Any]]:
        """Create optimal search sequence for maximum coverage."""
        # Sort queries by effectiveness score
        sorted_queries = sorted(queries, key=lambda x: scores.get(x["query"], 0), reverse=True)
        
        sequence = []
        for i, query_info in enumerate(sorted_queries):
            sequence.append({
                "order": i + 1,
                "query": query_info["query"],
                "approach": query_info["approach"],
                "rationale": self._get_sequence_rationale(i + 1, query_info["approach"]),
                "expected_results": self._estimate_result_count(query_info["approach"])
            })
        
        return sequence

    def _get_sequence_rationale(self, order: int, approach: str) -> str:
        """Get rationale for query sequence order."""
        rationales = {
            1: f"Start with {approach} approach for optimal initial results",
            2: f"Follow with {approach} to expand coverage",
            3: f"Use {approach} to fill remaining gaps",
            4: f"Apply {approach} for comprehensive coverage",
            5: f"Final {approach} search for complete results"
        }
        return rationales.get(order, f"Additional {approach} search for thorough coverage")

    def _estimate_result_count(self, approach: str) -> str:
        """Estimate result count based on approach."""
        estimates = {
            "conservative": "10-30 highly relevant results",
            "balanced": "30-80 relevant results",
            "aggressive": "80-200+ broad results",
            "boolean_hybrid": "40-100 targeted results",
            "phrase_focused": "20-60 contextually relevant results"
        }
        return estimates.get(approach, "Variable result count")

    def _analyze_coverage_overlap(self, queries: List[Dict]) -> Dict[str, Any]:
        """Analyze potential overlap between different search strategies."""
        analysis = {
            "estimated_unique_coverage": {
                "conservative": "15-20%",
                "balanced": "60-70%",
                "aggressive": "80-90%",
                "boolean_hybrid": "45-55%",
                "phrase_focused": "30-40%"
            },
            "overlap_patterns": {
                "conservative_vs_balanced": "70% overlap expected",
                "balanced_vs_aggressive": "85% overlap expected",
                "boolean_vs_phrase": "40% overlap expected"
            },
            "complementary_strategies": [
                "Conservative + Aggressive for precision-recall balance",
                "Boolean + Phrase for structural variety",
                "Balanced + Phrase for comprehensive coverage"
            ],
            "redundancy_risk": "Medium - recommend running top 3 queries maximum"
        }
        
        return analysis

    def _generate_optimization_tips(self, base_query: str, context: str, 
                                  optimization_level: str, expansions: Dict) -> List[str]:
        """Generate recommendations for further search refinement."""
        tips = [
            f"Current optimization level '{optimization_level}' is suitable for your search context",
            f"Consider {len(expansions)} keyword variations identified for your query terms"
        ]
        
        # Context-specific tips
        if "job search" in context.lower():
            tips.extend([
                "Add location modifiers for geographically relevant results",
                "Include experience level keywords (junior, senior, lead)",
                "Consider industry-specific terminology variations"
            ])
        elif "talent acquisition" in context.lower():
            tips.extend([
                "Use Boolean combinations to target specific skill sets",
                "Include negative keywords to exclude irrelevant candidates",
                "Consider searching by education and certification keywords"
            ])
        elif "market research" in context.lower():
            tips.extend([
                "Add time-based modifiers for recent information",
                "Include industry and market size qualifiers",
                "Consider competitive landscape terminology"
            ])
        
        # General optimization tips
        tips.extend([
            "Monitor search result quality and adjust query complexity accordingly",
            "Test different query approaches based on result volume needs",
            "Consider search platform-specific syntax optimizations",
            "Use quoted phrases for exact match requirements",
            "Implement negative keywords to filter out irrelevant results"
        ])
        
        return tips