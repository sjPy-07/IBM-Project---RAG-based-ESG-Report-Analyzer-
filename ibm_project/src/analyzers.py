# modules 
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

import os 
import json 
from dotenv import load_dotenv

# loading env vals 
load_dotenv()

# ESG Analyzer class 

class ESGAnalyzer:
    """_summary_
    Analyzes ESG reports for metrics and greenwashing.
    """
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model = "gemini-2.5-flash",
            temperature = 0.175   
        )
    
    
    def _validate_metrics(self, metrics: dict) -> dict:
        """Ensure metrics have proper structure with null values for missing data."""
        
        # Template for expected structure
        template = {
            'environmental': {
                'scope_1_emissions': None,
                'scope_2_emissions': None,
                'scope_3_emissions': None,
                'renewable_energy_percentage': None,
                'water_usage': None,
                'waste_recycled_percentage': None
            },
            'social': {
                'women_in_workforce_percentage': None,
                'women_in_leadership_percentage': None,
                'board_diversity_percentage': None,
                'safety_incident_rate': None,
                'employee_training_hours': None
            },
            'governance': {
                'independent_directors_percentage': None,
                'board_size': None,
                'esg_committee_exists': None,
                'ethics_violations_reported': None
            }
        }
        
        # Merge extracted metrics with template
        for category in template:
            if category not in metrics:
                metrics[category] = template[category]
            else:
                for metric in template[category]:
                    if metric not in metrics[category]:
                        metrics[category][metric] = None
        
        return metrics
    
    
    def _get_empty_metrics(self) -> dict:
        """Return empty metrics structure when extraction fails."""
        return {
            'environmental': {
                'scope_1_emissions': None,
                'scope_2_emissions': None,
                'scope_3_emissions': None,
                'renewable_energy_percentage': None,
                'water_usage': None,
                'waste_recycled_percentage': None
            },
            'social': {
                'women_in_workforce_percentage': None,
                'women_in_leadership_percentage': None,
                'board_diversity_percentage': None,
                'safety_incident_rate': None,
                'employee_training_hours': None
            },
            'governance': {
                'independent_directors_percentage': None,
                'board_size': None,
                'esg_committee_exists': None,
                'ethics_violations_reported': None
            }
        }
        
    
    def extract_metrics(self, text: str) -> dict:
        """_summary_
        Extract structured ESG metrics from the text.
        
        Args:
            text (str): Relevant sections of text to analyze 

        Returns:
            dict: Dictionary of extracted metrics 
        """
        
        # Load prompt template 
        with open('.\prompts\sample_metric.txt', 'r') as file:
            template = file.read()
        
        prompt = template.replace('{text}', text[:10000])
        
        try:
            response = self.llm.invoke(prompt).content.strip()
            metrics = json.loads(response.strip())
            return metrics 
        except Exception as e:
            print(f"Error extracting metrics: {e}")
            return {"error" : str(e)}
        
    
    def detect_greenwashing(self, statement: str) -> dict:
        """_summary_
        Analyze a statememt for greenwashing
        
        Args:
            statement (str): Statements extracted form the Corporate Sustainability Report 

        Returns:
            dict: Dictionary showing the greenwashing analysis report 
        """
        
        # Load prompt template 
        with open('.\prompts\sample_gwd.txt', 'r') as file:
            template = file.read()
        
        prompt = template.replace('{statement}', statement)
        
        try:
            response = self.llm.invoke(prompt).content.strip()   
            print("\n\nVerifying the output of gw function :")
            print(response, "\n\n\n")
            analysis = json.loads(response.strip())
            return analysis 
        except Exception as e:
            print(f"Error detecting greenwashing : {e}")
            return {"error" : str(e)}
        
        
    def analyze_commitments(self, text: str) -> dict:
        """_summary_
        Extract and analyze the sustainability claims made in the report 
        
        Args:
            text (str): Claims made 

        Returns:
            dict: Returns a dictionary of commitments and activities with target dates, progress and current status.s
        """
        
        # Load prompt template 
        with open('.\prompts\sample_commits.txt', 'r') as file:
            template = file.read()
        
        prompt = template.replace('{text}', text)
        
        
        try:
            response = self.llm.invoke(prompt).content.strip()
            claim_report = json.loads(response.strip())
            return claim_report
        except Exception as e:
            print(f"Error analyzing commitments : {e}")
            return {"error" : str(e)}
    
        
# Test the analyzer 
if __name__ == "__main__":
    analyzer = ESGAnalyzer()
    
    # Test metric extraction 
    print("Testing metric extraction...")
    sample_text = """
    In 2023, our Scope 1 and 2 emissions totaled 450,000 tons of CO2 equivalent,
    representing a 25% \\reduction from our 2020 baseline. We achieved 65% \\renewable
    energy usage across all operations. Our workforce is 42% women, with 35% women
    in leadership roles. The board consists of 12 directors, of which 50% \\are independent.
    """
    
    metrics = analyzer.extract_metrics(sample_text)
    print(json.dumps(metrics, indent=2))
    print("\n\n\n", "=" * 100, "\n\n")
    
    
    # Test greenwashing detection
    print("\n\nTesting greenwashing detection...")
    test_statements = [
        "We are committed to exploring sustainable solutions for a better tomorrow.",
        "We will reduce Scope 1 and 2 emissions by 50% by 2030, based on our 2020 baseline of 800,000 tons CO2e."
    ]   
    
    for statement in test_statements:
        print(f"\nStatement: {statement}\n")
        result = analyzer.detect_greenwashing(statement)
        print("\n\n\n", "=" * 100, "\n\n")
        print(f"Greenwashing Score: {result.get('greenwashing_score', 'N/A')}/10")
        print(f"Verdict: {result.get('verdict', 'N/A')}")