import pydanticRoadmapGenerator


if __name__ == "__main__":
    generator = pydanticRoadmapGenerator.PydanticRoadmapGenerator()

    result = generator.generate_roadmap("Python", "Visual", "Advanced")

    print("\n📘 OVERVIEW:")
    print(result.overview)

    print("\n🎯 STRATEGIES:")
    for i, s in enumerate(result.strategies, 1):
        print(f"{i}. {s}")

    print("\n📚 RESOURCES:")
    for i, r in enumerate(result.resources, 1):
        print(f"{i}. {r}")

    print("\n🧠 SELECTED LEVEL:")
    print(result.timeline.level.upper())

    print("\n🗺️ PHASE DETAILS:")
    print(result.timeline.phase_content)

    print("\n📅 WEEKLY PLAN:")
    for week in result.timeline.weekly_breakdown:
        print(f"Week {week.week}: {week.plan}")

    print("\n🔗 REFERENCES:")
    for ref in result.references:
        print(f"- {ref}")