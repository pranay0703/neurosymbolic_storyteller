"""
Example prompts and expected behaviors
"""

EXAMPLE_PROMPTS = [
    {
        "prompt": "Write a short story about Alice and Bob going to a store. Alice dies in an accident. Later, Alice buys some milk.",
        "expected_violations": ["character_death"],
        "description": "Tests dead character performing actions"
    },
    {
        "prompt": "Create a story where John is very brave in the first paragraph, but John is cowardly in the second paragraph.",
        "expected_violations": ["character_consistency"],
        "description": "Tests character trait consistency"
    },
    {
        "prompt": "Write a story that starts in the morning, then moves to evening, then back to morning of the same day.",
        "expected_violations": ["temporal_consistency"],
        "description": "Tests temporal logic"
    },
    {
        "prompt": "Tell a simple story about a person walking in a park and meeting a friend.",
        "expected_violations": [],
        "description": "Simple story with no expected violations"
    }
]

def run_examples():
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

    from storyteller_engine import StorytellerEngine

    engine = StorytellerEngine(max_iterations=2)
    try:
        for i, example in enumerate(EXAMPLE_PROMPTS):
            print(f"\n{'='*60}")
            print(f"EXAMPLE {i+1}: {example['description']}")
            print(f"Expected violations: {example['expected_violations']}")
            print(f"{'='*60}")
            print(f"Prompt: {example['prompt']}")
            print("-" * 40)

            results = engine.generate_and_improve(example['prompt'])

            print("Final Story:")
            print(results['final_story'])

            if results['iterations']:
                first_iteration = results['iterations'][0]
                print(f"\nViolations found: {first_iteration['violation_count']}")
                for v in first_iteration['violations']:
                    print(f" - {v.rule_name}: {v.description}")

    finally:
        engine.close()

if __name__ == "__main__":
    run_examples()
