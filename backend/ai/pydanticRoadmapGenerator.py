import pydanticOpenRouterClient
import roadmapResponse as roadmapResponse


class PydanticRoadmapGenerator:
        def __init__(self):
            self.client = pydanticOpenRouterClient.PydanticOpenRouterClient()

        def generate_roadmap(self, topic: str, brain_type: str, level: str) -> roadmapResponse.RoadmapResponse:

            user_prompt = f"""
Generate a personalized learning roadmap for the topic: {topic},
tailored to a {brain_type} learner.

User Level: {level}

Level Guidelines:
- beginner → fundamentals, simple explanations
- intermediate → practical projects, deeper concepts
- advanced → system design, optimization

IMPORTANT:
- Return ONLY the selected level: {level}
- Do NOT include other levels

Requirements:
1. Overview (based on {level})
2. Strategies (based on {brain_type})
3. Resources (suitable for {level})
4. Timeline:
   - level: {level}
   - phase_content: roadmap ONLY for {level}
   - weekly_breakdown: 6–8 weeks
5. References (3–5 URLs)

Constraints:
- Keep content practical
- Match difficulty to {level}
"""

            return self.client.generate(user_prompt, roadmapResponse.RoadmapResponse)