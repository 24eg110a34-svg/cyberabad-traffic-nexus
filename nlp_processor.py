"""
CYBERABAD TRAFFIC NEXUS - NLP Processing Module
Processes traffic alerts and generates insights using NLP
"""

import re
import random
from collections import Counter

# NLP Keywords for traffic analysis
TRAFFIC_KEYWORDS = {
    "congestion": ["congestion", "traffic jam", "gridlock", "slow", "stuck", "blocked", "heavy"],
    "accident": ["accident", "crash", "collision", "smash", "vehicle broken down", "stalled"],
    "road_closure": ["road closure", "blocked", "closed", "no entry", "barricade", "divert"],
    "weather": ["rain", "flood", "waterlogging", "storm", "fog", "visibility", "slippery"],
    "event": ["festival", "holiday", "event", "crowd", " procession", "marriage", "rally"],
    "emergency": ["ambulance", "emergency", "fire", "police", "rescue", "urgent"],
    "infrastructure": ["pothole", "construction", "roadwork", "signal", "lights out", "manhole"],
    "violation": ["over speeding", "signal jump", "wrong lane", "illegal parking", "triple riding"]
}

SEVERITY_WORDS = {
    "critical": ["critical", "emergency", "life threatening", "severe", "major", "disaster"],
    "high": ["high", "serious", "urgent", "priority", "important", "alert"],
    "medium": ["moderate", "concerning", "noteworthy", "attention", "monitor"],
    "low": ["minor", "low", "routine", "normal", "standard", "informational"]
}

AREA_KEYWORDS = {
    "OLD_CITY": ["charminar", "chaderghat", "madina", "koti", "laad bazaar", "madin", "nampally", "mj market"],
    "IT_CORRIDOR": ["gachibowli", "hitec", "kondapur", "nanakramguda", "cyber towers", "iiit"],
    "CENTRAL": ["punjagutta", "begumpet", "banjara", "masab tank", "khairatabad", "ameerpet"],
    "EAST": ["uppal", "ghatkesar", "habsiguda", "tarnaka", "lb nagar", "sainikpuri"],
    "SOUTH": ["mehdipatnam", "dilsukhnagar", "nalasopara", "nanal nagar", "bala nagar"]
}

class TrafficNLP:
    def __init__(self):
        self.history = []
    
    def analyze_text(self, text):
        """Analyze text for traffic-related information"""
        text_lower = text.lower()
        
        result = {
            "sentiment": self.analyze_sentiment(text),
            "entities": self.extract_entities(text),
            "keywords": self.extract_keywords(text),
            "severity": self.assess_severity(text),
            "action_items": self.extract_action_items(text),
            "confidence": 0.85
        }
        
        self.history.append(result)
        return result
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of text"""
        text_lower = text.lower()
        
        positive_words = ["clear", "smooth", "good", "improved", "better", "optimized", "green wave"]
        negative_words = ["congestion", "blocked", "heavy", "critical", "danger", "emergency", "alert", "warning"]
        neutral_words = ["normal", "routine", "standard", "moderate"]
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if neg_count > pos_count:
            sentiment = "negative"
            score = min(0.9, 0.5 + neg_count * 0.1)
        elif pos_count > neg_count:
            sentiment = "positive"
            score = min(0.9, 0.5 + pos_count * 0.1)
        else:
            sentiment = "neutral"
            score = 0.5
        
        return {
            "label": sentiment,
            "score": round(score, 2),
            "is_actionable": neg_count > 1
        }
    
    def extract_entities(self, text):
        """Extract named entities (locations, times, etc.)"""
        text_lower = text.lower()
        entities = {"areas": [], "times": [], "numbers": [], "keywords": []}
        
        # Extract areas
        for area, keywords in AREA_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    entities["areas"].append(area)
                    break
        
        # Extract time patterns
        time_patterns = [
            r'\d{1,2}:\d{2}',  # 10:30
            r'\d{1,2}\s*(am|pm)',  # 10am
            r'\d+\s*minutes?',  # 30 minutes
            r'\d+\s*hours?'  # 2 hours
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities["times"].extend(matches)
        
        # Extract numbers
        numbers = re.findall(r'\d+', text)
        entities["numbers"] = [int(n) for n in numbers if int(n) < 1000]
        
        # Extract keywords
        for category, keywords in TRAFFIC_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    entities["keywords"].append(category)
        
        return entities
    
    def extract_keywords(self, text):
        """Extract traffic-related keywords"""
        text_lower = text.lower()
        keywords = []
        
        for category, word_list in TRAFFIC_KEYWORDS.items():
            for word in word_list:
                if word in text_lower:
                    keywords.append({
                        "word": word,
                        "category": category
                    })
        
        return keywords
    
    def assess_severity(self, text):
        """Assess severity level from text"""
        text_lower = text.lower()
        
        severity_score = 0.5
        
        # Check severity words
        for level, words in SEVERITY_WORDS.items():
            for word in words:
                if word in text_lower:
                    if level == "critical":
                        severity_score = max(severity_score, 0.95)
                    elif level == "high":
                        severity_score = max(severity_score, 0.75)
                    elif level == "medium":
                        severity_score = max(severity_score, 0.55)
                    else:
                        severity_score = min(severity_score, 0.35)
        
        # Check for numbers
        numbers = re.findall(r'\d+', text)
        for num in numbers:
            num_int = int(num)
            if num_int > 80:  # High percentage
                severity_score = max(severity_score, 0.7)
            elif num_int > 50:
                severity_score = max(severity_score, 0.6)
        
        # Determine severity label
        if severity_score >= 0.8:
            label = "critical"
        elif severity_score >= 0.65:
            label = "high"
        elif severity_score >= 0.45:
            label = "medium"
        else:
            label = "low"
        
        return {
            "label": label,
            "score": round(severity_score, 2)
        }
    
    def extract_action_items(self, text):
        """Extract action items from alert text"""
        text_lower = text.lower()
        actions = []
        
        action_patterns = {
            "dispatch_police": ["dispatch traffic police", "send police", "traffic police"],
            "adjust_signals": ["adjust signals", "change timing", "signal optimization"],
            "road_closure": ["close road", "block road", "divert traffic"],
            "emergency_vehicle": ["ambulance", "emergency vehicle", "green corridor"],
            "public_warning": ["advise commuters", "avoid area", "take alternative route"],
            "monitor": ["monitor closely", "keep watching", "surveillance"]
        }
        
        for action, patterns in action_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    actions.append(action)
                    break
        
        return actions
    
    def generate_alert_summary(self, alert):
        """Generate NLP-powered alert summary"""
        text = alert.get("message", "") + " " + alert.get("location", "")
        
        analysis = self.analyze_text(text)
        
        summary = {
            "headline": self.generate_headline(alert, analysis),
            "impact": self.assess_impact(alert, analysis),
            "recommendation": self.generate_recommendation(alert, analysis),
            "affected_areas": list(set(analysis["entities"]["areas"])),
            "sentiment": analysis["sentiment"],
            "priority_score": self.calculate_priority(alert, analysis)
        }
        
        return summary
    
    def generate_headline(self, alert, analysis):
        """Generate alert headline"""
        location = alert.get("location", "Unknown Location")
        severity = analysis["severity"]["label"]
        alert_type = alert.get("type", "incident")
        
        templates = {
            "critical": "🚨 CRITICAL: {location} - Immediate action required",
            "high": "⚠️ ALERT: {location} - {type} reported",
            "medium": "📢 UPDATE: {location} - {type} affecting traffic",
            "low": "ℹ️ INFO: {location} - {type}"
        }
        
        template = templates.get(severity, templates["medium"])
        return template.format(location=location, type=alert_type)
    
    def assess_impact(self, alert, analysis):
        """Assess traffic impact"""
        score = alert.get("score", 50)
        
        impact_level = "low"
        if score > 80:
            impact_level = "severe"
        elif score > 65:
            impact_level = "high"
        elif score > 45:
            impact_level = "moderate"
        
        return {
            "level": impact_level,
            "delay_estimate": f"{int(score * 0.5)}-{int(score * 0.8)} minutes",
            "vehicles_affected": self.estimate_affected_vehicles(score)
        }
    
    def estimate_affected_vehicles(self, score):
        """Estimate number of affected vehicles"""
        base = 100
        multiplier = score / 50
        return int(base * multiplier * random.uniform(0.8, 1.2))
    
    def generate_recommendation(self, alert, analysis):
        """Generate recommendation based on analysis"""
        severity = analysis["severity"]["label"]
        actions = analysis["action_items"]
        
        if severity == "critical":
            return "Dispatch traffic police immediately. Consider road closure."
        elif severity == "high":
            if "adjust_signals" in actions:
                return "Optimize signal timing. Increase green wave coverage."
            return "Deploy traffic personnel. Monitor situation closely."
        elif severity == "medium":
            return "Monitor area. Prepare for signal adjustments if needed."
        else:
            return "Log for analysis. No immediate action required."
    
    def calculate_priority(self, alert, analysis):
        """Calculate priority score for alert"""
        severity_weight = {
            "critical": 40,
            "high": 30,
            "medium": 20,
            "low": 10
        }
        
        score_weight = alert.get("score", 50) / 2
        sentiment_weight = (1 - analysis["sentiment"]["score"]) * 20
        
        priority = (
            severity_weight.get(analysis["severity"]["label"], 20) +
            score_weight +
            sentiment_weight
        )
        
        return min(100, int(priority))
    
    def batch_analyze_alerts(self, alerts):
        """Analyze multiple alerts"""
        summaries = []
        for alert in alerts:
            summary = self.generate_alert_summary(alert)
            summary["original_alert"] = alert
            summaries.append(summary)
        
        # Sort by priority
        summaries.sort(key=lambda x: x["priority_score"], reverse=True)
        
        return summaries
    
    def get_keyword_stats(self):
        """Get keyword statistics from history"""
        all_keywords = []
        for item in self.history:
            all_keywords.extend([k["category"] for k in item.get("keywords", [])])
        
        return dict(Counter(all_keywords))


# Global NLP instance
_nlp_processor = None

def get_nlp_processor():
    """Get global NLP processor instance"""
    global _nlp_processor
    if _nlp_processor is None:
        _nlp_processor = TrafficNLP()
    return _nlp_processor


# Test NLP module
if __name__ == "__main__":
    nlp = TrafficNLP()
    
    test_text = "Critical congestion at Charminar junction. Heavy traffic jam with 95% congestion. Ambulance stuck in traffic."
    result = nlp.analyze_text(test_text)
    
    print("Analysis Result:")
    print(f"Sentiment: {result['sentiment']}")
    print(f"Severity: {result['severity']}")
    print(f"Entities: {result['entities']}")
    print(f"Keywords: {result['keywords']}")
    print(f"Action Items: {result['action_items']}")
