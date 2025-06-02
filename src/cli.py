"""
Command Line Interface for Neurosymbolic Storyteller
"""

import argparse
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from storyteller_engine import StorytellerEngine

def main():
    parser = argparse.ArgumentParser(description='Neurosymbolic Storyteller')
    parser.add_argument('--prompt', '-p', type=str, required=True, help='Story prompt')
    parser.add_argument('--iterations', '-i', type=int, default=3, help='Max iterations')
    parser.add_argument('--model', '-m', type=str, default='llama2:7b-chat', help='Model name')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    print("🤖 Neurosymbolic Storyteller")
    print("=" * 50)
    print(f"Prompt: {args.prompt}")
    print(f"Max iterations: {args.iterations}")
    print(f"Model: {args.model}")
    print("=" * 50)

    engine = StorytellerEngine(model_name=args.model, max_iterations=args.iterations)
    try:
        results = engine.generate_and_improve(args.prompt)

        print("\n📖 FINAL STORY:")
        print("-" * 40)
        print(results['final_story'])

        print(f"\n📊 SUMMARY:")
        print(f"Total iterations: {len(results['iterations'])}")
        print(f"Violations fixed: {results['total_violations_fixed']}")

        if args.verbose and results['iterations']:
            print(f"\n🔍 DETAILED ITERATIONS:")
            for i, iteration in enumerate(results['iterations']):
                print(f"\nIteration {i+1}:")
                print(f" Violations: {iteration['violation_count']}")
                for v in iteration['violations']:
                    print(f" - {v.description}")
    finally:
        engine.close()

if __name__ == "__main__":
    main()
