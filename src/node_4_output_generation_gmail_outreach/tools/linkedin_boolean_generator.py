from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Dict, Any, List
import json

class LinkedInBooleanGeneratorRequest(BaseModel):
    """Input schema for LinkedIn Boolean Generator Tool."""
    job_title: str = Field(..., description="Primary job title to search for (e.g., 'CEO', 'Software Engineer', 'Marketing Manager')")
    industry: str = Field(..., description="Industry or sector (e.g., 'Technology', 'Healthcare', 'Finance')")
    location: str = Field(..., description="Location or region (e.g., 'Sydney', 'California', 'Europe')")
    company_size: str = Field(..., description="Company size preference (e.g., 'startup', 'enterprise', 'mid-size', 'any')")

class LinkedInBooleanGeneratorTool(BaseTool):
    """Tool for generating optimized Boolean search strings for LinkedIn searches."""

    name: str = "LinkedIn Boolean Generator Tool"
    description: str = (
        "Generates optimized Boolean search strings for LinkedIn with job title variations, "
        "location alternatives, industry keywords, company size filters, and exclusion terms. "
        "Returns multiple search variations for comprehensive professional searches."
    )
    args_schema: Type[BaseModel] = LinkedInBooleanGeneratorRequest

    def _get_job_title_variations(self, job_title: str) -> List[str]:
        """Generate variations and synonyms for job titles."""
        title_lower = job_title.lower()
        variations = [job_title]
        
        # Common job title variations
        title_maps = {
            'ceo': ['CEO', 'Chief Executive Officer', 'President', 'Managing Director', 'Founder'],
            'cto': ['CTO', 'Chief Technology Officer', 'VP Technology', 'Head of Technology'],
            'cfo': ['CFO', 'Chief Financial Officer', 'VP Finance', 'Finance Director'],
            'software engineer': ['Software Engineer', 'Software Developer', 'Developer', 'Programmer', 'Software Dev'],
            'data scientist': ['Data Scientist', 'Machine Learning Engineer', 'Data Analyst', 'ML Engineer'],
            'marketing manager': ['Marketing Manager', 'Marketing Director', 'Brand Manager', 'Digital Marketing Manager'],
            'sales manager': ['Sales Manager', 'Sales Director', 'Business Development Manager', 'Account Manager'],
            'product manager': ['Product Manager', 'Product Owner', 'Product Director', 'PM'],
            'hr manager': ['HR Manager', 'Human Resources Manager', 'People Manager', 'Talent Manager'],
            'designer': ['Designer', 'UX Designer', 'UI Designer', 'Graphic Designer', 'Product Designer'],
        }
        
        for key, vals in title_maps.items():
            if key in title_lower:
                variations.extend(vals)
                break
        
        # Remove duplicates while preserving order
        seen = set()
        unique_variations = []
        for var in variations:
            if var not in seen:
                seen.add(var)
                unique_variations.append(var)
        
        return unique_variations[:5]  # Limit to 5 variations

    def _get_location_variations(self, location: str) -> List[str]:
        """Generate location variations and alternatives."""
        location_lower = location.lower()
        variations = [location]
        
        # Location maps for major cities/regions
        location_maps = {
            'sydney': ['Sydney', 'NSW', 'New South Wales', 'Australia'],
            'melbourne': ['Melbourne', 'VIC', 'Victoria', 'Australia'],
            'san francisco': ['San Francisco', 'SF', 'Bay Area', 'California', 'CA'],
            'new york': ['New York', 'NYC', 'NY', 'Manhattan'],
            'london': ['London', 'UK', 'United Kingdom', 'England'],
            'singapore': ['Singapore', 'SG', 'Asia Pacific'],
            'toronto': ['Toronto', 'Canada', 'ON', 'Ontario'],
            'california': ['California', 'CA', 'San Francisco', 'Los Angeles', 'Silicon Valley'],
            'europe': ['Europe', 'EU', 'European Union'],
            'asia': ['Asia', 'APAC', 'Asia Pacific'],
        }
        
        for key, vals in location_maps.items():
            if key in location_lower:
                variations.extend(vals)
                break
        
        # Remove duplicates
        return list(dict.fromkeys(variations))[:4]

    def _get_industry_keywords(self, industry: str) -> List[str]:
        """Get relevant keywords for the industry."""
        industry_lower = industry.lower()
        
        industry_maps = {
            'technology': ['tech', 'software', 'IT', 'digital', 'innovation', 'startup'],
            'finance': ['banking', 'investment', 'fintech', 'financial services', 'capital'],
            'healthcare': ['medical', 'pharmaceutical', 'biotech', 'health', 'clinical'],
            'marketing': ['advertising', 'digital marketing', 'brand', 'communications', 'media'],
            'consulting': ['advisory', 'strategy', 'management consulting', 'professional services'],
            'retail': ['e-commerce', 'consumer goods', 'fashion', 'merchandising'],
            'education': ['academic', 'university', 'learning', 'training', 'educational'],
            'manufacturing': ['industrial', 'production', 'operations', 'supply chain'],
        }
        
        for key, keywords in industry_maps.items():
            if key in industry_lower:
                return keywords[:4]
        
        return [industry]

    def _get_company_size_terms(self, company_size: str) -> List[str]:
        """Get company size related terms."""
        size_lower = company_size.lower()
        
        if 'startup' in size_lower:
            return ['startup', 'early stage', 'seed', 'Series A']
        elif 'enterprise' in size_lower or 'large' in size_lower:
            return ['Fortune 500', 'enterprise', 'global', 'multinational']
        elif 'mid' in size_lower:
            return ['mid-size', 'growing company', 'scale-up']
        else:
            return []

    def _run(self, job_title: str, industry: str, location: str, company_size: str) -> str:
        try:
            # Generate variations
            job_variations = self._get_job_title_variations(job_title)
            location_variations = self._get_location_variations(location)
            industry_keywords = self._get_industry_keywords(industry)
            company_size_terms = self._get_company_size_terms(company_size)
            
            # Create OR groups
            job_or_group = ' OR '.join(f'"{title}"' for title in job_variations)
            location_or_group = ' OR '.join(f'"{loc}"' for loc in location_variations)
            industry_or_group = ' OR '.join(industry_keywords)
            
            # Standard exclusion terms
            exclusion_terms = [
                'former', 'ex-', 'retired', 'previous', 'past', 'emeritus', 
                'intern', 'student', 'seeking', 'looking for'
            ]
            exclusion_string = ' AND NOT (' + ' OR '.join(exclusion_terms) + ')'
            
            # Build primary search
            primary_components = [
                f'({job_or_group})',
                f'({location_or_group})',
                f'({industry_or_group})'
            ]
            
            if company_size_terms:
                company_or_group = ' OR '.join(company_size_terms)
                primary_components.append(f'({company_or_group})')
            
            primary_search = f'site:linkedin.com/in/ AND {" AND ".join(primary_components)}{exclusion_string}'
            
            # Generate alternative searches
            alternative_searches = []
            
            # Alternative 1: Focus on job title and location only
            alt1 = f'site:linkedin.com/in/ AND ({job_or_group}) AND ({location_or_group}){exclusion_string}'
            alternative_searches.append(alt1)
            
            # Alternative 2: Broader industry focus
            if len(job_variations) > 1:
                broader_job = ' OR '.join(f'"{title}"' for title in job_variations[:3])
                alt2 = f'site:linkedin.com/in/ AND ({broader_job}) AND ({industry_or_group}) AND ({location_or_group}){exclusion_string}'
                alternative_searches.append(alt2)
            
            # Alternative 3: Company size specific (if applicable)
            if company_size_terms:
                company_focus = f'site:linkedin.com/in/ AND ({job_or_group}) AND ({" OR ".join(company_size_terms)}) AND ({location_or_group}){exclusion_string}'
                alternative_searches.append(company_focus)
            
            # Generate search tips
            search_tips = [
                f"Primary search combines {len(job_variations)} job title variations with location and industry filters",
                "Use quotation marks around exact phrases for precise matching",
                f"Excludes {len(exclusion_terms)} irrelevant terms to improve result quality",
                "Try alternative searches for broader or more targeted results",
                "Consider removing industry filter if results are too narrow"
            ]
            
            result = {
                "primary_search": primary_search,
                "alternative_searches": alternative_searches,
                "exclusion_terms": exclusion_terms,
                "search_tips": search_tips,
                "job_variations_used": job_variations,
                "location_variations_used": location_variations,
                "industry_keywords_used": industry_keywords,
                "company_size_terms_used": company_size_terms
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error generating LinkedIn Boolean search: {str(e)}"