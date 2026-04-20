"""
NeuroNav Roadmap Generator
AI-powered system for generating personalized learning paths based on brain types
"""

from datetime import datetime
from typing import List, Dict, Any
from pymongo import MongoClient
from bson import ObjectId
import os

# Import the new AI service
from ai_service import AIRoadmapGenerator

class RoadmapGenerator:
    """Generates personalized learning roadmaps based on brain type and preferences"""
    
    # Brain type preferences for resource types
    BRAIN_TYPE_PREFERENCES = {
        "Visual": {
            "preferred_types": ["video", "infographic", "diagram", "tutorial"],
            "weights": {"video": 0.4, "tutorial": 0.3, "article": 0.2, "course": 0.1}
        },
        "Auditory": {
            "preferred_types": ["podcast", "audio", "course", "video"],
            "weights": {"course": 0.4, "video": 0.3, "podcast": 0.2, "article": 0.1}
        },
        "ReadWrite": {
            "preferred_types": ["article", "book", "documentation", "tutorial"],
            "weights": {"article": 0.4, "book": 0.3, "documentation": 0.2, "tutorial": 0.1}
        },
        "Kinesthetic": {
            "preferred_types": ["tutorial", "project", "exercise", "course"],
            "weights": {"tutorial": 0.4, "project": 0.3, "course": 0.2, "exercise": 0.1}
        }
    }
    
    # Learning intensity to time mapping (in minutes)
    INTENSITY_TIME_MAPPING = {
        "beginner": {"daily": 30, "total_weeks": 8},
        "intermediate": {"daily": 60, "total_weeks": 6},
        "advanced": {"daily": 90, "total_weeks": 4}
    }
    
    def __init__(self):
        # Direct database connection
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/neuronav')
        client = MongoClient(mongo_uri)
        self.db = client.get_database()
        
        # Initialize AI service
        try:
            self.ai_generator = AIRoadmapGenerator()
            self.use_ai = True
        except Exception as e:
            print(f"AI service not available, falling back to rule-based: {e}")
            self.ai_generator = None
            self.use_ai = False
    
    def generate_roadmap(self, user_id: str, topic: str, brain_type: str, 
                        duration: str = "intermediate", intensity: str = "intermediate") -> Dict[str, Any]:
        """
        Generate personalized learning roadmap using AI or fallback to rule-based
        
        Args:
            user_id: User's ObjectId as string
            topic: Learning topic
            brain_type: User's identified brain type (Visual, Auditory, ReadWrite, Kinesthetic)
            duration: short, medium, long
            intensity: light, moderate, intensive
            
        Returns:
            Dict containing roadmap data
        """
        try:
            # Check for existing roadmap to prevent duplicates
            existing_roadmap = self._check_existing_roadmap(user_id, topic, brain_type)
           # if existing_roadmap:
               # print(f"Found existing roadmap for {topic} - {brain_type}, returning existing one")
                #return existing_roadmap
            
            # Use AI generation if available
            if self.use_ai and self.ai_generator:
                print(f"Generating AI roadmap for {topic} - {brain_type} learner")
                ai_roadmap = self.ai_generator.generate_roadmap(topic, brain_type, duration, intensity)
                
                # Add database fields and save
                roadmap_data = self._prepare_roadmap_for_db(ai_roadmap, user_id)
                self._save_roadmap_to_db(roadmap_data, user_id)
                
                return roadmap_data
            else:
                # Fallback to rule-based generation
                print(f"Using rule-based roadmap generation for {topic} - {brain_type} learner")
                return self._generate_rule_based_roadmap(user_id, topic, brain_type, duration, intensity)
                
        except Exception as e:
            print(f"Roadmap generation error: {e}")
            # Fallback to rule-based if AI fails
            return self._generate_rule_based_roadmap(user_id, topic, brain_type, duration, intensity)
    
    def _check_existing_roadmap(self, user_id: str, topic: str, brain_type: str) -> Dict[str, Any] | None:
        """Check if a roadmap already exists for this user/topic/brain_type combination"""
        if self.db is None:
            return None
        
        try:
            existing = self.db.roadmaps.find_one({
                'user_id': ObjectId(user_id),
                'topic': topic,
                'brain_type': brain_type
            })
            
            if existing:
                # Convert to the expected format
                return {
                    "user_id": user_id,
                    "topic": existing.get('topic'),
                    "brain_type": existing.get('brain_type'),
                    "overview": existing.get('overview', ''),
                    "strategies": existing.get('strategies', []),
                    "steps": existing.get('steps', []),
                    "estimated_completion_weeks": existing.get('estimated_completion_weeks', 6),
                    "daily_time_minutes": existing.get('daily_time_minutes', 60),
                    "ai_generated": existing.get('ai_generated', False),
                    "references": existing.get('references', []),
                    "roadmap_id": str(existing['_id'])
                }
            return None
        except Exception as e:
            print(f"Error checking existing roadmap: {e}")
            return None
    
    def _prepare_roadmap_for_db(self, ai_roadmap: Dict, user_id: str) -> Dict:
        """Prepare AI-generated roadmap for database storage"""
        return {
            "user_id": user_id,
            "topic": ai_roadmap["topic"],
            "brain_type": ai_roadmap["brain_type"],
            "overview": ai_roadmap.get("overview", ""),
            "strategies": ai_roadmap.get("strategies", []),
            "steps": ai_roadmap["steps"],
            "estimated_completion_weeks": ai_roadmap["estimated_completion_weeks"],
            "daily_time_minutes": ai_roadmap["daily_time_minutes"],
            "ai_generated": True,
            "references": ai_roadmap.get("references", [])
        }
    
    def _save_roadmap_to_db(self, roadmap_data: Dict, user_id: str) -> str:
        """Save roadmap to database and return roadmap_id"""
        if self.db is None:
            return ""
        
        # Save to database
        roadmap_doc = {
            "user_id": ObjectId(user_id),
            "topic": roadmap_data["topic"],
            "brain_type": roadmap_data["brain_type"],
            "overview": roadmap_data.get("overview", ""),
            "strategies": roadmap_data.get("strategies", []),
            "steps": roadmap_data["steps"],
            "estimated_completion_weeks": roadmap_data["estimated_completion_weeks"],
            "daily_time_minutes": roadmap_data["daily_time_minutes"],
            "ai_generated": roadmap_data.get("ai_generated", False),
            "references": roadmap_data.get("references", []),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = self.db.roadmaps.insert_one(roadmap_doc)
        roadmap_data["roadmap_id"] = str(result.inserted_id)
        
        return str(result.inserted_id)
    
    def _generate_rule_based_roadmap(self, user_id: str, topic: str, brain_type: str, 
                                   duration: str, intensity: str) -> Dict[str, Any]:
        """Original rule-based roadmap generation as fallback"""
        try:
            # Get resources based on topic and brain type
            resources = self._get_topic_resources(topic)
            if not resources:
                resources = self._get_general_resources()
            
            # Rank resources by brain type preferences
            ranked_resources = self._rank_resources_by_brain_type(resources, brain_type)
            
            # Generate learning steps
            steps = self._generate_learning_steps(ranked_resources, brain_type, intensity)
            
            # Create roadmap object
            roadmap_data = {
                "user_id": user_id,
                "topic": topic,
                "brain_type": brain_type,
                "duration": duration,
                "intensity": intensity,
                "steps": steps,
                "estimated_completion_weeks": self.INTENSITY_TIME_MAPPING.get(intensity, {}).get("total_weeks", 6),
                "daily_time_minutes": self.INTENSITY_TIME_MAPPING.get(intensity, {}).get("daily", 60),
                "ai_generated": False
            }
            
            # Save to database
            roadmap_doc = {
                "user_id": ObjectId(user_id),
                "topic": topic,
                "brain_type": brain_type,
                "steps": steps,
                "estimated_completion_weeks": self.INTENSITY_TIME_MAPPING.get(intensity, {}).get("total_weeks", 6),
                "daily_time_minutes": self.INTENSITY_TIME_MAPPING.get(intensity, {}).get("daily", 60),
                "ai_generated": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = self.db.roadmaps.insert_one(roadmap_doc)
            roadmap_data["roadmap_id"] = str(result.inserted_id)
            
            return roadmap_data
            
        except Exception as e:
            raise Exception(f"Roadmap generation failed: {str(e)}")
    
    def _get_topic_resources(self, topic: str) -> List[Dict]:
        """Get resources related to a specific topic"""
        if self.db is None:
            return self._create_fallback_resources(topic)
        
        # Search for resources with topic in tags or title
        resources = list(self.db.resources.find({
            "$or": [
                {"tags": {"$regex": topic, "$options": "i"}},
                {"title": {"$regex": topic, "$options": "i"}},
                {"description": {"$regex": topic, "$options": "i"}}
            ]
        }))
        
        # If no topic-specific resources found, create fallback content
        if not resources:
            return self._create_fallback_resources(topic)
        
        # Convert ObjectId to string for JSON serialization
        for resource in resources:
            resource["_id"] = str(resource["_id"])
        
        return resources
    
    def _create_fallback_resources(self, topic: str) -> List[Dict]:
        """Create topic-specific fallback resources when database has no matches"""
        topic_lower = topic.lower()
        
        # Topic-specific resource templates
        if "design" in topic_lower:
            return [
                {
                    "_id": "fallback_design_1",
                    "title": "Design Fundamentals",
                    "description": "Learn the basic principles of design including color theory, typography, and layout",
                    "type": "tutorial",
                    "url": "https://example.com/design-fundamentals",
                    "est_time": 120,
                    "tags": ["design", "fundamentals"]
                },
                {
                    "_id": "fallback_design_2", 
                    "title": "User Experience (UX) Design",
                    "description": "Understanding user research, wireframing, and prototyping",
                    "type": "course",
                    "url": "https://example.com/ux-design",
                    "est_time": 180,
                    "tags": ["design", "ux", "user-experience"]
                },
                {
                    "_id": "fallback_design_3",
                    "title": "Design Tools Mastery",
                    "description": "Learn industry-standard design tools like Figma, Adobe Creative Suite",
                    "type": "tutorial",
                    "url": "https://example.com/design-tools",
                    "est_time": 150,
                    "tags": ["design", "tools", "figma"]
                }
            ]
        elif "data science" in topic_lower or "data" in topic_lower:
            return [
                {
                    "_id": "fallback_ds_1",
                    "title": "Data Science Fundamentals",
                    "description": "Introduction to statistics, probability, and data analysis concepts",
                    "type": "course",
                    "url": "https://example.com/data-science-fundamentals",
                    "est_time": 240,
                    "tags": ["data-science", "statistics"]
                },
                {
                    "_id": "fallback_ds_2",
                    "title": "Python for Data Analysis",
                    "description": "Learn pandas, numpy, and matplotlib for data manipulation and visualization",
                    "type": "tutorial",
                    "url": "https://example.com/python-data-analysis",
                    "est_time": 180,
                    "tags": ["data-science", "python", "pandas"]
                }
            ]
        elif "python" in topic_lower:
            return [
                {
                    "_id": "fallback_py_1",
                    "title": "Python Programming Basics",
                    "description": "Learn Python syntax, variables, functions, and control structures",
                    "type": "tutorial",
                    "url": "https://example.com/python-basics",
                    "est_time": 120,
                    "tags": ["python", "programming", "basics"]
                },
                {
                    "_id": "fallback_py_2",
                    "title": "Object-Oriented Programming in Python",
                    "description": "Understanding classes, inheritance, and advanced Python concepts",
                    "type": "course",
                    "url": "https://example.com/python-oop",
                    "est_time": 150,
                    "tags": ["python", "oop", "programming"]
                }
            ]
        else:
            # Generic fallback for unknown topics
            return [
                {
                    "_id": "fallback_generic_1",
                    "title": f"Introduction to {topic}",
                    "description": f"Learn the fundamentals and core concepts of {topic}",
                    "type": "tutorial",
                    "url": f"https://example.com/{topic.lower().replace(' ', '-')}",
                    "est_time": 120,
                    "tags": [topic.lower()]
                },
                {
                    "_id": "fallback_generic_2",
                    "title": f"Advanced {topic} Concepts",
                    "description": f"Deep dive into advanced topics and practical applications of {topic}",
                    "type": "course", 
                    "url": f"https://example.com/{topic.lower().replace(' ', '-')}-advanced",
                    "est_time": 180,
                    "tags": [topic.lower(), "advanced"]
                }
            ]
    
    def _get_general_resources(self) -> List[Dict]:
        """Get general learning resources as fallback"""
        if self.db is None:
            return []
        
        resources = list(self.db.resources.find().limit(10))
        
        # Convert ObjectId to string
        for resource in resources:
            resource["_id"] = str(resource["_id"])
        
        return resources
    
    def _rank_resources_by_brain_type(self, resources: List[Dict], brain_type: str) -> List[Dict]:
        """Rank resources based on brain type preferences"""
        if brain_type not in self.BRAIN_TYPE_PREFERENCES:
            return resources
        
        preferences = self.BRAIN_TYPE_PREFERENCES[brain_type]
        weights = preferences["weights"]
        
        # Score each resource based on type preference
        for resource in resources:
            resource_type = resource.get("type", "article").lower()
            resource["brain_type_score"] = weights.get(resource_type, 0.1)
        
        # Sort by brain type score (descending)
        return sorted(resources, key=lambda x: x.get("brain_type_score", 0), reverse=True)
    
    def _generate_learning_steps(self, resources: List[Dict], brain_type: str, intensity: str) -> List[Dict]:
        """Generate structured learning steps from resources"""
        steps = []
        
        # Determine number of steps based on intensity
        max_steps = {"beginner": 6, "intermediate": 8, "advanced": 10}.get(intensity, 8)
        
        # Take top resources up to max_steps
        selected_resources = resources[:max_steps]
        
        for i, resource in enumerate(selected_resources):
            step = {
                "step_number": i + 1,
                "title": resource.get("title", f"Learning Step {i + 1}"),
                "description": self._generate_step_description(resource, brain_type),
                "resource_id": str(resource.get("_id", "")),  # Ensure _id is converted to string
                "resource_url": resource.get("url"),
                "resource_type": resource.get("type"),
                "estimated_time_minutes": resource.get("est_time", 60),
                "tags": resource.get("tags", []),
                "brain_type_optimized": True
            }
            steps.append(step)
        
        return steps
    
    def _generate_step_description(self, resource: Dict, brain_type: str) -> str:
        """Generate brain-type optimized description for a learning step"""
        base_description = resource.get("description", "")
        
        # Add brain-type specific learning tips
        brain_type_tips = {
            "Visual": "Focus on visual elements, diagrams, and interactive demonstrations.",
            "Auditory": "Listen carefully to explanations and consider discussing concepts with others.",
            "ReadWrite": "Take detailed notes and create written summaries of key concepts.",
            "Kinesthetic": "Practice hands-on exercises and apply concepts through real projects."
        }
        
        tip = brain_type_tips.get(brain_type, "")
        
        if base_description and tip:
            return f"{base_description} {tip}"
        elif tip:
            return tip
        else:
            return base_description or "Complete this learning step."


# Standalone function for external use
def generate_user_roadmap(user_id: str, topic: str, brain_type: str, 
                         duration: str = "intermediate", intensity: str = "intermediate") -> Dict[str, Any]:
    """
    Generate a roadmap for a user
    
    Args:
        user_id: User's ObjectId as string
        topic: Learning topic
        brain_type: User's assessed brain type
        duration: Learning duration preference  
        intensity: Learning intensity level
        
    Returns:
        Dictionary containing roadmap data
    """
    generator = RoadmapGenerator()
    return generator.generate_roadmap(user_id, topic, brain_type, duration, intensity)