from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Dict, Any, List
import json

class AdvancedWebBooleanBuilderRequest(BaseModel):
    """Input schema for Advanced Web Boolean Builder Tool."""
    search_intent: str = Field(..., description="The primary intent of the search (e.g., 'find CEO contact', 'locate executives', 'company information')")
    target_platform: str = Field(..., description="Primary platform to optimize for (google, linkedin, directories, or 'all' for all platforms)")
    job_title: str = Field(..., description="Target job title or position (e.g., 'CEO', 'CTO', 'VP Sales')")
    industry: str = Field(..., description="Industry or business sector (e.g., 'technology', 'healthcare', 'finance')")
    location: str = Field(..., description="Geographic location (e.g., 'San Francisco', 'New York', 'California')")

class AdvancedWebBooleanBuilderTool(BaseTool):
    """Tool for generating optimized Boolean search strings for contact discovery across multiple platforms."""

    name: str = "advanced_web_boolean_builder"
    description: str = (
        "Generates sophisticated Boolean search strings optimized for different platforms "
        "(Google, LinkedIn, company directories) to find contact information, executive details, "
        "and company data. Creates platform-specific syntax with smart exclusions and targeting."
    )
    args_schema: Type[BaseModel] = AdvancedWebBooleanBuilderRequest

    def _run(self, search_intent: str, target_platform: str, job_title: str, industry: str, location: str) -> str:
        try:
            # Clean and normalize inputs
            search_intent = search_intent.strip().lower()
            target_platform = target_platform.strip().lower()
            job_title = job_title.strip()
            industry = industry.strip()
            location = location.strip()

            # Generate platform-specific searches
            platform_searches = self._generate_platform_searches(job_title, industry, location)
            
            # Generate contact-focused searches
            contact_focused_searches = self._generate_contact_searches(job_title, industry, location)
            
            # Generate company page searches
            company_page_searches = self._generate_company_page_searches(job_title, industry, location)
            
            # Generate verification searches
            verification_searches = self._generate_verification_searches(job_title, industry, location)
            
            # Generate search strategy explanation
            search_strategy = self._generate_search_strategy(search_intent, target_platform, job_title, industry, location)

            result = {
                "platform_searches": platform_searches,
                "contact_focused_searches": contact_focused_searches,
                "company_page_searches": company_page_searches,
                "verification_searches": verification_searches,
                "search_strategy": search_strategy
            }

            return json.dumps(result, indent=2)

        except Exception as e:
            return f"Error generating Boolean search strings: {str(e)}"

    def _generate_platform_searches(self, job_title: str, industry: str, location: str) -> Dict[str, List[str]]:
        """Generate platform-specific Boolean search strings."""
        
        # Google-specific searches
        google_searches = [
            f'site:linkedin.com/in "{job_title}" "{industry}" "{location}"',
            f'("{job_title}" OR "Chief Executive" OR "President") AND "{industry}" AND "{location}" filetype:pdf',
            f'intitle:"{job_title}" "{industry}" "{location}" -job -jobs -hiring -career',
            f'site:*.com/about "{job_title}" "{industry}" "{location}"',
            f'("{job_title}" AND "{industry}") "{location}" (contact OR email OR phone OR tel)'
        ]
        
        # LinkedIn-specific searches
        linkedin_searches = [
            f'{job_title} AND {industry} AND {location}',
            f'(title:"{job_title}" OR title:"Chief Executive") AND industry:"{industry}" AND location:"{location}"',
            f'current:({job_title}) AND industry:({industry}) AND region:({location})',
            f'people: {job_title} {industry} {location}',
            f'"{job_title}" "{industry}" connections:1st OR connections:2nd location:"{location}"'
        ]
        
        # Company directories searches
        directories_searches = [
            f'{job_title} {industry} {location} site:crunchbase.com',
            f'{job_title} {industry} {location} site:zoominfo.com',
            f'"{job_title}" "{industry}" "{location}" site:bloomberg.com/profiles',
            f'{job_title} {industry} {location} (site:forbes.com OR site:fortune.com)',
            f'company directory "{job_title}" "{industry}" "{location}"'
        ]

        return {
            "google": google_searches,
            "linkedin": linkedin_searches,
            "directories": directories_searches
        }

    def _generate_contact_searches(self, job_title: str, industry: str, location: str) -> List[str]:
        """Generate contact information focused searches."""
        
        contact_searches = [
            f'("{job_title}" OR "CEO" OR "Chief Executive") AND "{industry}" AND "{location}" AND ("email" OR "contact" OR "phone" OR "tel" OR "mobile")',
            f'"{job_title}" "{industry}" "{location}" (email OR "e-mail" OR "@" OR "contact us")',
            f'site:*.com/contact "{job_title}" "{industry}" "{location}"',
            f'("{job_title}" AND "{industry}") "{location}" ("phone number" OR "telephone" OR "direct line")',
            f'inurl:contact "{job_title}" "{industry}" "{location}"',
            f'("{job_title}" OR "executive") "{industry}" "{location}" (biography OR bio OR profile) (email OR phone)',
            f'"executive team" OR "leadership team" "{industry}" "{location}" contact',
            f'"{job_title}" "{industry}" "{location}" ("business card" OR "vcard" OR "contact information")'
        ]
        
        return contact_searches

    def _generate_company_page_searches(self, job_title: str, industry: str, location: str) -> List[str]:
        """Generate searches targeting specific company pages."""
        
        company_page_searches = [
            f'site:*.com/about "{job_title}" "{industry}" "{location}"',
            f'site:*.com/team "{job_title}" "{industry}" "{location}"',
            f'site:*.com/leadership "{job_title}" "{industry}" "{location}"',
            f'site:*.com/executives "{job_title}" "{industry}" "{location}"',
            f'(inurl:about OR inurl:team OR inurl:leadership) "{job_title}" "{industry}" "{location}"',
            f'site:*.com/contact "{industry}" "{location}" ("{job_title}" OR "CEO")',
            f'inurl:company OR inurl:corporate "{job_title}" "{industry}" "{location}"',
            f'"about us" "{job_title}" "{industry}" "{location}"',
            f'(inurl:management OR inurl:board) "{job_title}" "{industry}" "{location}"'
        ]
        
        return company_page_searches

    def _generate_verification_searches(self, job_title: str, industry: str, location: str) -> List[str]:
        """Generate searches to verify executive positions and details."""
        
        verification_searches = [
            f'"{job_title}" "{industry}" "{location}" (appointed OR promoted OR named OR announced)',
            f'"{job_title}" "{industry}" "{location}" (press release OR news OR announcement)',
            f'"{job_title}" "{industry}" "{location}" (interview OR speaking OR conference)',
            f'"{job_title}" "{industry}" "{location}" (award OR recognition OR achievement)',
            f'site:*.com/news "{job_title}" "{industry}" "{location}"',
            f'"{job_title}" "{industry}" "{location}" (board OR director OR executive)',
            f'"{job_title}" "{industry}" "{location}" filetype:pdf (annual report OR investor)',
            f'"{job_title}" "{industry}" "{location}" (keynote OR speaker OR panel)'
        ]
        
        return verification_searches

    def _generate_search_strategy(self, search_intent: str, target_platform: str, job_title: str, industry: str, location: str) -> str:
        """Generate explanation of the search approach."""
        
        strategy_parts = [
            f"Search Strategy for finding {job_title} in {industry} sector, {location}:",
            "",
            "1. PLATFORM OPTIMIZATION:",
        ]
        
        if target_platform == "all" or target_platform == "google":
            strategy_parts.extend([
                "   • Google: Uses site: operators to target LinkedIn, company websites, and professional directories",
                "   • Employs filetype:pdf for executive documents and excludes job posting noise",
                "   • Targets specific URL patterns (about, team, leadership pages)"
            ])
            
        if target_platform == "all" or target_platform == "linkedin":
            strategy_parts.extend([
                "   • LinkedIn: Leverages title:, industry:, and location: operators for precise targeting",
                "   • Uses connection degree filters to find accessible contacts",
                "   • Combines current position and industry filters"
            ])
            
        if target_platform == "all" or target_platform == "directories":
            strategy_parts.extend([
                "   • Directories: Targets professional databases like Crunchbase, ZoomInfo, Bloomberg",
                "   • Uses business publication sites for executive profiles",
                "   • Focuses on company directory structures"
            ])

        strategy_parts.extend([
            "",
            "2. CONTACT DISCOVERY APPROACH:",
            "   • Primary: Direct contact information (email, phone, mobile)",
            "   • Secondary: Company contact pages and team directories",
            "   • Tertiary: Professional biographies and profiles with contact details",
            "",
            "3. VERIFICATION STRATEGY:",
            "   • Cross-reference through news articles and press releases",
            "   • Validate through speaking engagements and professional activities",
            "   • Confirm via annual reports and official company communications",
            "",
            "4. SMART EXCLUSIONS:",
            "   • Filters out job postings and recruitment content (-job -jobs -hiring -career)",
            "   • Focuses on current positions rather than historical roles",
            "   • Prioritizes direct company sources over third-party mentions"
        ])

        return "\n".join(strategy_parts)