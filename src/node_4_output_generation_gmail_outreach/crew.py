import os

from crewai import LLM
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import (
	SerperDevTool,
	FirecrawlScrapeWebsiteTool
)
from node_4_output_generation_gmail_outreach.tools.linkedin_boolean_generator import LinkedInBooleanGeneratorTool
from node_4_output_generation_gmail_outreach.tools.advanced_web_boolean_builder import AdvancedWebBooleanBuilderTool
from node_4_output_generation_gmail_outreach.tools.smart_search_query_optimizer import SmartSearchQueryOptimizer
from node_4_output_generation_gmail_outreach.tools.phone_enrichment_tool import PhoneEnrichmentTool
from node_4_output_generation_gmail_outreach.tools.multi_source_phone_validator import MultiSourcePhoneValidatorTool





@CrewBase
class Node4OutputGenerationGmailOutreachCrew:
    """Node4OutputGenerationGmailOutreach crew"""

    
    @agent
    def company_discovery_specialist(self) -> Agent:
        
        
        return Agent(
            config=self.agents_config["company_discovery_specialist"],
            
            
            tools=[				SerperDevTool(),
				FirecrawlScrapeWebsiteTool(),
				LinkedInBooleanGeneratorTool(),
				AdvancedWebBooleanBuilderTool(),
				SmartSearchQueryOptimizer(),
				PhoneEnrichmentTool(),
				MultiSourcePhoneValidatorTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                
                
            ),
            
        )
        
    
    @agent
    def contact_discovery_specialist(self) -> Agent:
        
        
        return Agent(
            config=self.agents_config["contact_discovery_specialist"],
            
            
            tools=[				LinkedInBooleanGeneratorTool(),
				AdvancedWebBooleanBuilderTool(),
				PhoneEnrichmentTool(),
				SerperDevTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                
                
            ),
            
        )
        
    
    @agent
    def lead_quality_analyst(self) -> Agent:
        
        
        return Agent(
            config=self.agents_config["lead_quality_analyst"],
            
            
            tools=[				MultiSourcePhoneValidatorTool(),
				SerperDevTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                
                
            ),
            
        )
        
    
    @agent
    def output_coordinator(self) -> Agent:
        
        
        return Agent(
            config=self.agents_config["output_coordinator"],
            
            
            tools=[],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            apps=[
                    "google_sheets/create_spreadsheet",
                    
                    "google_sheets/append_values",
                    
                    "google_sheets/update_values",
                    
                    "google_gmail/create_draft",
                    
                    "google_gmail/send_email",
                    ],
            
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                
                
            ),
            
        )
        
    

    
    @task
    def discover_target_companies_and_websites(self) -> Task:
        return Task(
            config=self.tasks_config["discover_target_companies_and_websites"],
            markdown=False,
            
            
        )
    
    @task
    def discover_executive_contacts(self) -> Task:
        return Task(
            config=self.tasks_config["discover_executive_contacts"],
            markdown=False,
            
            
        )
    
    @task
    def validate_and_score_leads(self) -> Task:
        return Task(
            config=self.tasks_config["validate_and_score_leads"],
            markdown=False,
            
            
        )
    
    @task
    def generate_output_and_manage_outreach(self) -> Task:
        return Task(
            config=self.tasks_config["generate_output_and_manage_outreach"],
            markdown=False,
            
            
        )
    

    @crew
    def crew(self) -> Crew:
        """Creates the Node4OutputGenerationGmailOutreach crew"""

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,

            chat_llm=LLM(model="openai/gpt-4o-mini"),
        )


