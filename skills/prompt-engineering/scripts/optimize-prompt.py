#!/usr/bin/env python3
"""
Prompt optimization harness: evaluate prompt variants against a test suite,
compare metrics, and keep the best performer.

Demo harness — ships with a mock LLM client so it runs offline; wire a real
client (any object with a `complete(prompt) -> str` method) for actual use.
Uses only the standard library.

Notes:
- Word counts approximate size; use the provider tokenizer or usage metadata
  for real token numbers.
- Variations follow the skill's calibration guidance: no "think step by step"
  scaffolding is generated, because it degrades reasoning models. For classic /
  non-reasoning models, add chain-of-thought variants manually (see
  references/chain-of-thought-basics.md).
"""

import json
import statistics
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor


@dataclass
class TestCase:
    input: Dict[str, Any]
    expected_output: str
    metadata: Optional[Dict[str, Any]] = None


def percentile(values: List[float], pct: float) -> float:
    """Linear-interpolated percentile (pct in [0, 100])."""
    if not values:
        return 0.0
    ordered = sorted(values)
    k = (len(ordered) - 1) * pct / 100.0
    lower = int(k)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (k - lower)


class PromptOptimizer:
    def __init__(self, llm_client, test_suite: List[TestCase]):
        self.client = llm_client
        self.test_suite = test_suite
        self.results_history = []
        self.executor = ThreadPoolExecutor()

    def shutdown(self):
        """Shutdown the thread pool executor."""
        self.executor.shutdown(wait=True)

    def evaluate_prompt(self, prompt_template: str, test_cases: Optional[List[TestCase]] = None) -> Dict[str, float]:
        """Evaluate a prompt template against test cases in parallel."""
        if test_cases is None:
            test_cases = self.test_suite

        def process_test_case(test_case):
            start_time = time.time()
            prompt = prompt_template.format(**test_case.input)
            response = self.client.complete(prompt)
            latency = time.time() - start_time

            return {
                'latency': latency,
                'word_count': len(prompt.split()) + len(response.split()),
                'success_rate': 1 if response else 0,
                'accuracy': self.calculate_accuracy(response, test_case.expected_output),
            }

        results = list(self.executor.map(process_test_case, test_cases))

        latencies = [r['latency'] for r in results]
        return {
            'avg_accuracy': statistics.mean(r['accuracy'] for r in results),
            'avg_latency': statistics.mean(latencies),
            'p95_latency': percentile(latencies, 95),
            'avg_words': statistics.mean(r['word_count'] for r in results),
            'success_rate': statistics.mean(r['success_rate'] for r in results),
        }

    def calculate_accuracy(self, response: str, expected: str) -> float:
        """Exact match, falling back to word overlap.

        A rough default grader: fine for label-style outputs, weak for
        free-form text. Replace with a schema validator, assertions, or a
        rubric/LLM-judge grader for real workloads (see
        references/prompt-optimization-workflow.md).
        """
        if response.strip().lower() == expected.strip().lower():
            return 1.0

        response_words = set(response.lower().split())
        expected_words = set(expected.lower().split())

        if not expected_words:
            return 0.0

        overlap = len(response_words & expected_words)
        return overlap / len(expected_words)

    def optimize(self, base_prompt: str, max_iterations: int = 5) -> Dict[str, Any]:
        """Iteratively optimize a prompt."""
        current_prompt = base_prompt
        best_prompt = base_prompt
        best_score = 0
        current_metrics = None

        for iteration in range(max_iterations):
            print(f"\nIteration {iteration + 1}/{max_iterations}")

            # Reuse metrics carried over from the previous iteration's winner.
            if current_metrics:
                metrics = current_metrics
            else:
                metrics = self.evaluate_prompt(current_prompt)

            print(f"Accuracy: {metrics['avg_accuracy']:.2f}, Latency: {metrics['avg_latency']:.2f}s")

            self.results_history.append({
                'iteration': iteration,
                'prompt': current_prompt,
                'metrics': metrics
            })

            if metrics['avg_accuracy'] > best_score:
                best_score = metrics['avg_accuracy']
                best_prompt = current_prompt

            if metrics['avg_accuracy'] > 0.95:
                print("Achieved target accuracy!")
                break

            variations = self.generate_variations(current_prompt, metrics)

            best_variation = current_prompt
            best_variation_score = metrics['avg_accuracy']
            best_variation_metrics = metrics

            for variation in variations:
                var_metrics = self.evaluate_prompt(variation)
                if var_metrics['avg_accuracy'] > best_variation_score:
                    best_variation_score = var_metrics['avg_accuracy']
                    best_variation = variation
                    best_variation_metrics = var_metrics

            current_prompt = best_variation
            current_metrics = best_variation_metrics

        return {
            'best_prompt': best_prompt,
            'best_score': best_score,
            'history': self.results_history
        }

    def generate_variations(self, prompt: str, current_metrics: Dict) -> List[str]:
        """Generate prompt variations to test.

        One instruction changes per variation, in line with the skill's
        iterate-in-small-deltas rule.
        """
        variations = []

        # Variation 1: explicit output-format instruction
        variations.append(prompt + "\n\nProvide your answer in a clear, concise format.")

        # Variation 2: explicit scope statement
        variations.append(prompt + "\n\nAnswer only what is asked; do not add unrequested information.")

        # Variation 3: self-check against constraints
        variations.append(prompt + "\n\nVerify your answer against the requirements before responding.")

        # Variation 4: more concise wording
        concise = self.make_concise(prompt)
        if concise != prompt:
            variations.append(concise)

        # Variation 5: add an example (if none present)
        if "example" not in prompt.lower():
            variations.append(self.add_examples(prompt))

        return variations[:3]  # Test at most 3 per iteration

    def make_concise(self, prompt: str) -> str:
        """Remove redundant words to make prompt more concise."""
        replacements = [
            ("in order to", "to"),
            ("due to the fact that", "because"),
            ("at this point in time", "now"),
            ("in the event that", "if"),
        ]

        result = prompt
        for old, new in replacements:
            result = result.replace(old, new)

        return result

    def add_examples(self, prompt: str) -> str:
        """Add example section to prompt."""
        return f"""{prompt}

Example:
Input: Sample input
Output: Sample output
"""

    def compare_prompts(self, prompt_a: str, prompt_b: str) -> Dict[str, Any]:
        """A/B test two prompts."""
        print("Testing Prompt A...")
        metrics_a = self.evaluate_prompt(prompt_a)

        print("Testing Prompt B...")
        metrics_b = self.evaluate_prompt(prompt_b)

        return {
            'prompt_a_metrics': metrics_a,
            'prompt_b_metrics': metrics_b,
            'winner': 'A' if metrics_a['avg_accuracy'] > metrics_b['avg_accuracy'] else 'B',
            'improvement': abs(metrics_a['avg_accuracy'] - metrics_b['avg_accuracy'])
        }

    def export_results(self, filename: str):
        """Export optimization results to JSON."""
        with open(filename, 'w') as f:
            json.dump(self.results_history, f, indent=2)


def main():
    # Example usage
    test_suite = [
        TestCase(
            input={'text': 'This movie was amazing!'},
            expected_output='Positive'
        ),
        TestCase(
            input={'text': 'Worst purchase ever.'},
            expected_output='Negative'
        ),
        TestCase(
            input={'text': 'It was okay, nothing special.'},
            expected_output='Neutral'
        )
    ]

    # Mock LLM client for demonstration
    class MockLLMClient:
        def complete(self, prompt):
            # Simulate LLM response
            if 'amazing' in prompt:
                return 'Positive'
            elif 'worst' in prompt.lower():
                return 'Negative'
            else:
                return 'Neutral'

    optimizer = PromptOptimizer(MockLLMClient(), test_suite)

    try:
        base_prompt = "Classify the sentiment of: {text}\nSentiment:"

        results = optimizer.optimize(base_prompt)

        print("\n" + "="*50)
        print("Optimization Complete!")
        print(f"Best Accuracy: {results['best_score']:.2f}")
        print(f"Best Prompt:\n{results['best_prompt']}")

        optimizer.export_results('optimization_results.json')
    finally:
        optimizer.shutdown()


if __name__ == '__main__':
    main()
