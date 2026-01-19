import json

class ESGScorer:
    """Calculate ESG scores based on extracted metrics."""
    
    def __init__(self):
        # Weights for different categories
        self.weights = {
            'environmental': 0.40,
            'social': 0.30,
            'governance': 0.30
        }
    
    def score_environmental(self, metrics: dict) -> dict:
        """Score environmental performance 0-10."""
        score = 0
        details = []
        max_score = 10
        
        # Emissions reporting (2 points)
        scope1 = metrics.get('scope_1_emissions')
        scope2 = metrics.get('scope_2_emissions')
        
        if scope1 and scope1 is not None:
            score += 1.5
            details.append("✓ Reports Scope 1 emissions")
        
        if scope2 and scope2 is not None:
            score += 0.5
            details.append("✓ Reports Scope 2 emissions")
        
        if metrics.get('scope_3_emissions') and metrics.get('scope_3_emissions') is not None:
            score += 1
            details.append("✓ Reports Scope 3 emissions (comprehensive)")
        
        # Renewable energy (3 points)
        renewable_pct = metrics.get('renewable_energy_percentage')
        if renewable_pct is not None and renewable_pct > 0:
            if renewable_pct >= 75:
                score += 3
                details.append(f"✓ Excellent renewable energy usage ({renewable_pct}%)")
            elif renewable_pct >= 50:
                score += 2.5
                details.append(f"✓ Good renewable energy usage ({renewable_pct}%)")
            elif renewable_pct >= 25:
                score += 1.5
                details.append(f"○ Moderate renewable energy usage ({renewable_pct}%)")
            else:
                score += 0.5
                details.append(f"⚠ Low renewable energy usage ({renewable_pct}%)")
        
        # Waste management (1 point)
        waste_pct = metrics.get('waste_recycled_percentage')
        if waste_pct is not None and waste_pct > 0:
            if waste_pct >= 75:
                score += 1
                details.append(f"✓ High waste diversion rate ({waste_pct}%)")
            elif waste_pct >= 50:
                score += 0.7
                details.append(f"○ Moderate waste diversion ({waste_pct}%)")
            elif waste_pct >= 25:
                score += 0.4
                details.append(f"⚠ Limited waste diversion ({waste_pct}%)")
        
        # Water efficiency (1 point) - if reported
        if metrics.get('water_usage') and metrics.get('water_usage') is not None:
            score += 0.5
            details.append("✓ Reports water usage metrics")
        
        # Energy efficiency (1.5 points) - if reported
        if metrics.get('energy_efficiency') and metrics.get('energy_efficiency') is not None:
            score += 0.5
            details.append("✓ Reports energy efficiency metrics")
        
        # Cap at max_score
        score = min(score, max_score)
        
        return {
            'score': round(score, 2),
            'max_score': max_score,
            'percentage': round((score / max_score) * 100, 1),
            'details': details if details else ["⚠ Limited environmental data available"]
        }
    
    def score_social(self, metrics: dict) -> dict:
        """Score social performance 0-10."""
        score = 0
        details = []
        max_score = 10
        
        # Gender diversity - workforce (2 points)
        women_workforce = metrics.get('women_in_workforce_percentage')
        if women_workforce is not None and women_workforce > 0:
            if women_workforce >= 45:
                score += 2
                details.append(f"✓ Strong workforce diversity ({women_workforce}% women)")
            elif women_workforce >= 35:
                score += 1.5
                details.append(f"○ Good workforce diversity ({women_workforce}% women)")
            elif women_workforce >= 25:
                score += 1
                details.append(f"⚠ Improving workforce diversity ({women_workforce}% women)")
            else:
                score += 0.5
                details.append(f"⚠ Limited workforce diversity ({women_workforce}% women)")
        
        # Gender diversity - leadership (3 points)
        women_leadership = metrics.get('women_in_leadership_percentage')
        if women_leadership is not None and women_leadership > 0:
            if women_leadership >= 40:
                score += 3
                details.append(f"✓ Excellent leadership diversity ({women_leadership}% women)")
            elif women_leadership >= 30:
                score += 2
                details.append(f"○ Good leadership diversity ({women_leadership}% women)")
            elif women_leadership >= 20:
                score += 1
                details.append(f"⚠ Limited leadership diversity ({women_leadership}% women)")
            else:
                score += 0.5
                details.append(f"⚠ Very limited leadership diversity ({women_leadership}% women)")
        
        # Board diversity (2 points)
        board_diversity = metrics.get('board_diversity_percentage')
        if board_diversity is not None and board_diversity > 0:
            if board_diversity >= 40:
                score += 2
                details.append(f"✓ Strong board diversity ({board_diversity}%)")
            elif board_diversity >= 30:
                score += 1.5
                details.append(f"○ Good board diversity ({board_diversity}%)")
            elif board_diversity >= 20:
                score += 1
                details.append(f"⚠ Limited board diversity ({board_diversity}%)")
            else:
                score += 0.5
                details.append(f"⚠ Very limited board diversity ({board_diversity}%)")
        
        # Safety metrics (2 points)
        safety_rate = metrics.get('safety_incident_rate')
        if safety_rate is not None:
            if safety_rate < 1.0:
                score += 2
                details.append(f"✓ Excellent safety record ({safety_rate} incidents)")
            elif safety_rate < 2.0:
                score += 1.5
                details.append(f"○ Good safety record ({safety_rate} incidents)")
            elif safety_rate < 3.0:
                score += 1
                details.append(f"⚠ Moderate safety record ({safety_rate} incidents)")
            else:
                score += 0.5
                details.append(f"⚠ Safety improvements needed ({safety_rate} incidents)")
        
        # Employee development (1 point)
        training_hours = metrics.get('employee_training_hours')
        if training_hours is not None and training_hours > 0:
            if training_hours >= 40:
                score += 1
                details.append(f"✓ Strong employee development program ({training_hours} hrs)")
            elif training_hours >= 20:
                score += 0.7
                details.append(f"○ Good employee development ({training_hours} hrs)")
            else:
                score += 0.4
                details.append(f"⚠ Limited employee development ({training_hours} hrs)")
        
        score = min(score, max_score)
        
        return {
            'score': round(score, 2),
            'max_score': max_score,
            'percentage': round((score / max_score) * 100, 1),
            'details': details if details else ["⚠ Limited social data available"]
        }
    
    def score_governance(self, metrics: dict) -> dict:
        """Score governance performance 0-10."""
        score = 0
        details = []
        max_score = 10
        
        # Board independence (3 points)
        independent_pct = metrics.get('independent_directors_percentage')
        if independent_pct is not None and independent_pct > 0:
            if independent_pct >= 75:
                score += 3
                details.append(f"✓ Strong board independence ({independent_pct}%)")
            elif independent_pct >= 50:
                score += 2
                details.append(f"○ Adequate board independence ({independent_pct}%)")
            elif independent_pct > 0:
                score += 1
                details.append(f"⚠ Limited board independence ({independent_pct}%)")
        
        # ESG committee (2 points)
        if metrics.get('esg_committee_exists') is True:
            score += 2
            details.append("✓ Dedicated ESG committee exists")
        elif metrics.get('esg_committee_exists') is False:
            score += 0.5
            details.append("⚠ No dedicated ESG committee")
        
        # Board size (1 point) - optimal is 8-12 directors
        board_size = metrics.get('board_size')
        if board_size is not None and board_size > 0:
            if 8 <= board_size <= 12:
                score += 1
                details.append(f"✓ Optimal board size ({board_size} directors)")
            elif board_size > 0:
                score += 0.5
                details.append(f"○ Board size: {board_size} directors")
        
        # Ethics & compliance (4 points)
        violations = metrics.get('ethics_violations_reported')
        if violations is not None:
            score += 2
            details.append("✓ Transparent ethics reporting")
            
            if violations == 0:
                score += 2
                details.append("✓ No ethics violations reported")
            elif violations < 5:
                score += 1.5
                details.append(f"○ Minimal violations ({violations})")
            elif violations < 10:
                score += 1
                details.append(f"⚠ Some violations reported ({violations})")
            else:
                score += 0.5
                details.append(f"⚠ Multiple violations reported ({violations})")
        
        # Climate risk disclosure (bonus points if available)
        if metrics.get('climate_risk_disclosure'):
            score += 0.5
            details.append("✓ Climate risk disclosure included")
        
        score = min(score, max_score)
        
        return {
            'score': round(score, 2),
            'max_score': max_score,
            'percentage': round((score / max_score) * 100, 1),
            'details': details if details else ["⚠ Limited governance data available"]
        }
    
    def calculate_overall_score(self, metrics: dict) -> dict:
        """Calculate overall ESG score."""
        
        # Score each category
        env_score = self.score_environmental(metrics.get('environmental', {}))
        social_score = self.score_social(metrics.get('social', {}))
        gov_score = self.score_governance(metrics.get('governance', {}))
        
        # Calculate weighted overall score
        overall = (
            env_score['score'] * self.weights['environmental'] +
            social_score['score'] * self.weights['social'] +
            gov_score['score'] * self.weights['governance']
        )
        
        # Determine rating
        if overall >= 8:
            rating = "Excellent"
            rating_emoji = "🌟"
        elif overall >= 6.5:
            rating = "Good"
            rating_emoji = "✅"
        elif overall >= 5:
            rating = "Fair"
            rating_emoji = "⚠️"
        elif overall >= 3:
            rating = "Needs Improvement"
            rating_emoji = "⚠️"
        else:
            rating = "Limited Data"
            rating_emoji = "❓"
        
        return {
            'overall_score': round(overall, 2),
            'max_score': 10,
            'rating': rating,
            'rating_emoji': rating_emoji,
            'environmental': env_score,
            'social': social_score,
            'governance': gov_score,
            'breakdown': {
                'environmental': f"{env_score['score']}/10 ({self.weights['environmental']*100}% weight)",
                'social': f"{social_score['score']}/10 ({self.weights['social']*100}% weight)",
                'governance': f"{gov_score['score']}/10 ({self.weights['governance']*100}% weight)"
            }
        }

# Test the scorer
if __name__ == "__main__":
    scorer = ESGScorer()
    
    # Test with sample metrics (including None values)
    sample_metrics = {
        'environmental': {
            'scope_1_emissions': {'value': 200000, 'unit': 'tons CO2e', 'year': 2023},
            'scope_2_emissions': {'value': 150000, 'unit': 'tons CO2e', 'year': 2023},
            'scope_3_emissions': None,  # Testing None value
            'renewable_energy_percentage': 78,
            'waste_recycled_percentage': None  # Testing None value
        },
        'social': {
            'women_in_workforce_percentage': 42,
            'women_in_leadership_percentage': None,  # Testing None value
            'board_diversity_percentage': 45,
            'safety_incident_rate': 0.8,
            'employee_training_hours': None  # Testing None value
        },
        'governance': {
            'independent_directors_percentage': None,  # Testing None value
            'board_size': 10,
            'esg_committee_exists': True,
            'ethics_violations_reported': 0
        }
    }
    
    result = scorer.calculate_overall_score(sample_metrics)
    
    print("ESG SCORE REPORT")
    print("=" * 50)
    print(f"Overall Score: {result['overall_score']}/10")
    print(f"Rating: {result['rating']} {result['rating_emoji']}")
    print()
    print("Category Breakdown:")
    print(f"  Environmental: {result['environmental']['score']}/10 ({result['environmental']['percentage']}%)")
    print(f"  Social: {result['social']['score']}/10 ({result['social']['percentage']}%)")
    print(f"  Governance: {result['governance']['score']}/10 ({result['governance']['percentage']}%)")
    print()
    print("Details:")
    for category, data in [('Environmental', result['environmental']), 
                           ('Social', result['social']), 
                           ('Governance', result['governance'])]:
        print(f"\n{category}:")
        for detail in data['details']:
            print(f"  {detail}")