"""
AI Service for generating personalized learning roadmaps
Uses Meta Llama 3.3 8B Instruct via OpenRouter API
"""

import os
import json
import requests
from typing import Dict, Any

class AIRoadmapGenerator:
    """AI-powered roadmap generator using Meta Llama 3.3 8B Instruct"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "meta-llama/llama-3.3-70B-instruct"  # Meta Llama 3.3 8B Instruct
        
        if not self.api_key:
            print("Warning: OPENROUTER_API_KEY not set. AI features will be disabled.")
            self.api_available = False
        else:
            self.api_available = True
    
    def generate_roadmap(self, topic: str, brain_type: str, duration: str = "intermediate", 
                        intensity: str = "intermediate") -> Dict[str, Any]:
        """
        Generate AI-powered personalized learning roadmap
        
        Args:
            topic: Learning topic (e.g., "Design", "Data Science")
            brain_type: One of Visual, Auditory, Kinesthetic, ReadWrite
            duration: Learning duration preference
            intensity: Learning intensity preference
            
        Returns:
            Dict containing the generated roadmap data
        """
        if not self.api_available:
            raise ValueError("OpenRouter API key not configured. Please set OPENROUTER_API_KEY environment variable.")
            
        try:
            # Construct the prompt using the provided template
            prompt = self._build_prompt(topic, brain_type, duration, intensity)
            
            # Make API call to OpenRouter
            response = self._call_openrouter_api(prompt)
            
            # Parse and structure the response
            roadmap_data = self._parse_ai_response(response, topic, brain_type)
            
            return roadmap_data
            
        except Exception as e:
            raise Exception(f"AI roadmap generation failed: {str(e)}")
    
    def _build_prompt(self, topic: str, brain_type: str, duration: str, intensity: str) -> str:
        """Build the prompt using the provided template"""
        
        prompt = f"""Generate a personalized learning roadmap for the topic: {topic}, tailored to a {brain_type} learner (one of: Visual, Auditory, Kinesthetic, Reading/Writing). Return the output in JSON with the following fields: 
1) 'overview': short summary of the learning goal, 
2) 'strategies': specific learning strategies based on {brain_type}, 
3) 'resources': recommended resources (books, free courses, tutorials, tools), 
4) 'timeline': include both (a) a phased roadmap (beginner, intermediate, advanced) and (b) a week-by-week breakdown, 
5) 'references': 3–5 free or widely available links to high-quality learning materials on the internet.

Additional context:
- Duration preference: {duration}
- Learning intensity: {intensity}
- Focus on {brain_type}-specific learning methods and resources
- Ensure all resources are accessible and practical

Please return valid JSON only, no additional text or markdown formatting."""

        return prompt
    
    def _call_openrouter_api(self, prompt: str) -> str:
        """Make API call to OpenRouter with Meta Llama model"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://neuronav.ai",  # Optional: your app name
            "X-Title": "NeuroNav Learning Assistant"  # Optional: your app name
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system", 
                    "content": "You are an expert learning advisor who creates personalized educational roadmaps based on learning styles. Always respond with valid JSON format."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000,
            "top_p": 0.9
        }
        
        response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
        
        result = response.json()
        
        if 'choices' not in result or len(result['choices']) == 0:
            raise Exception("Invalid response from OpenRouter API")
        
        return result['choices'][0]['message']['content']
    
    def _parse_ai_response(self, ai_response: str, topic: str, brain_type: str) -> Dict[str, Any]:
        """Parse AI response and structure it for the application"""
        
        try:
            # Try to parse the JSON response
            cleaned_response = ai_response.replace('`', '').replace("'", "").strip()
            ai_data = json.loads(cleaned_response)
            
            # Convert AI response to roadmap format expected by the application
            roadmap_data = {
                "topic": topic,
                "brain_type": brain_type,
                "overview": ai_data.get("overview", f"Personalized {topic} learning path for {brain_type} learners"),
                "strategies": ai_data.get("strategies", []),
                "timeline": ai_data.get("timeline", {}),
                "steps": self._convert_to_steps(ai_data),
                "estimated_completion_weeks": self._extract_duration(ai_data),
                "daily_time_minutes": self._extract_daily_time(ai_data),
                "ai_generated": True,
                "references": ai_data.get("references", [])
            }
            
            return roadmap_data
            
        except json.JSONDecodeError as err:
            # Fallback: if AI doesn't return valid JSON, create a structured response
            print(f"Error parsing AI response: {err}")
            return self._create_fallback_roadmap(ai_response, topic, brain_type)
    
    def _convert_to_steps(self, ai_data: Dict) -> list:
        """Convert AI timeline data to application step format"""
        steps = []
        
        timeline = ai_data.get("timeline", {})
        phases = timeline.get("phased_roadmap", timeline.get("phased roadmap", timeline.get("phases", {})))
        
        step_number = 1
        
        # Process beginner, intermediate, advanced phases in dict or list format
        if isinstance(phases, list):
            for phase in phases:
                phase_name = phase.get("phase") or phase.get("name") or "Phase"
                phase_goals = phase.get("goals", [])
                if isinstance(phase_goals, list):
                    for goal in phase_goals:
                        steps.append({
                            "step_number": step_number,
                            "title": f"{phase_name.title()}: {goal}",
                            "description": goal,
                            "resource_type": "ai_generated",
                            "estimated_time_minutes": 60,
                            "brain_type_optimized": True,
                            "phase": phase_name,
                            "duration": phase.get("duration")
                        })
                        step_number += 1
                elif isinstance(phase_goals, str):
                    steps.append({
                        "step_number": step_number,
                        "title": f"{phase_name.title()}: {phase_goals}",
                        "description": phase_goals,
                        "resource_type": "ai_generated",
                        "estimated_time_minutes": 60,
                        "brain_type_optimized": True,
                        "phase": phase_name,
                        "duration": phase.get("duration")
                    })
                    step_number += 1
        elif isinstance(phases, dict):
            for phase_name, phase_content in phases.items():
                if isinstance(phase_content, list):
                    for item in phase_content:
                        steps.append({
                            "step_number": step_number,
                            "title": f"{phase_name.title()}: {item}" if isinstance(item, str) else f"{phase_name.title()} Step {step_number}",
                            "description": item if isinstance(item, str) else f"Complete {phase_name} level activities",
                            "resource_type": "ai_generated",
                            "estimated_time_minutes": 60,
                            "brain_type_optimized": True,
                            "phase": phase_name
                        })
                        step_number += 1
        
        # If no phases found, create steps from resources
        if not steps:
            resources = ai_data.get("resources", [])
            for i, resource in enumerate(resources[:10]):  # Limit to 10 steps
                steps.append({
                    "step_number": i + 1,
                    "title": f"Step {i + 1}: {resource}" if isinstance(resource, str) else f"Learning Step {i + 1}",
                    "description": resource if isinstance(resource, str) else "AI-generated learning activity",
                    "resource_type": "ai_generated", 
                    "estimated_time_minutes": 60,
                    "brain_type_optimized": True
                })
        
        return steps
    
    def _extract_duration(self, ai_data: Dict) -> int:
        """Extract estimated completion weeks from AI response"""
        timeline = ai_data.get("timeline", {})
        
        # Look for week information in various formats
        if "weeks" in str(timeline).lower():
            # Try to extract number from timeline text
            import re
            week_match = re.search(r'(\d+)\s*weeks?', str(timeline), re.IGNORECASE)
            if week_match:
                return int(week_match.group(1))
        
        # Default fallback
        return 8
    
    def _extract_daily_time(self, ai_data: Dict) -> int:
        """Extract daily time commitment from AI response"""
        timeline = ai_data.get("timeline", {})
        
        # Look for time information
        if "minutes" in str(timeline).lower() or "hours" in str(timeline).lower():
            import re
            # Look for patterns like "30 minutes", "1 hour", etc.
            time_match = re.search(r'(\d+)\s*(?:minutes?|hrs?|hours?)', str(timeline), re.IGNORECASE)
            if time_match:
                time_val = int(time_match.group(1))
                if "hour" in time_match.group(0).lower():
                    return time_val * 60  # Convert hours to minutes
                return time_val
        
        # Default fallback
        return 60
    
    def _create_fallback_roadmap(self, ai_response: str, topic: str, brain_type: str) -> Dict[str, Any]:
        """Create a fallback roadmap if AI response parsing fails"""
        
        return {
            "topic": topic,
            "brain_type": brain_type,
            "overview": f"AI-generated learning path for {topic} optimized for {brain_type} learners",
            "strategies": [f"Utilize {brain_type}-specific learning methods", "Practice regularly", "Seek feedback"],
            "timeline": {"note": "Flexible timeline based on individual pace"},
            "steps": [
                {
                    "step_number": 1,
                    "title": f"Introduction to {topic}",
                    "description": f"Begin your {topic} learning journey with {brain_type}-optimized approaches",
                    "resource_type": "ai_generated",
                    "estimated_time_minutes": 60,
                    "brain_type_optimized": True
                }
            ],
            "estimated_completion_weeks": 6,
            "daily_time_minutes": 60,
            "ai_generated": True,
            "references": ["AI response could not be parsed properly"],
            "raw_ai_response": ai_response[:500]  # Store first 500 chars for debugging
        }