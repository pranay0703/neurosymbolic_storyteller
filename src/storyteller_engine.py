"""
Neurosymbolic Storyteller Core Engine
"""

import re
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

@dataclass
class Character:
    name: str
    status: str = "alive"
    location: str = "unknown"
    traits: List[str] = None
    last_mentioned: int = 0

    def __post_init__(self):
        if self.traits is None:
            self.traits = []

@dataclass
class StoryViolation:
    rule_name: str
    severity: str
    description: str
    sentence_idx: Optional[int] = None
    suggestion: str = ""

class StoryState:
    def __init__(self):
        self.characters: Dict[str, Character] = {}
        self.events: List[str] = []
        self.world_facts: Dict[str, str] = {}
        self.locations: set = set()
        self.genre: str = "general"

    def add_character(self, name: str, **kwargs):
        if name in self.characters:
            char = self.characters[name]
            for key, value in kwargs.items():
                if hasattr(char, key):
                    setattr(char, key, value)
        else:
            self.characters[name] = Character(name=name, **kwargs)

    def to_dict(self) -> dict:
        return {
            'characters': {n: asdict(c) for n, c in self.characters.items()},
            'events': self.events,
            'world_facts': self.world_facts,
            'locations': list(self.locations),
            'genre': self.genre
        }

class StoryParser:
    def __init__(self):
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("Warning: spaCy model not found.")

    def parse_story(self, text: str, story_state: StoryState) -> StoryState:
        if self.nlp:
            return self._advanced_parse(text, story_state)
        return self._simple_parse(text, story_state)

    def _advanced_parse(self, text: str, story_state: StoryState) -> StoryState:
        doc = self.nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents]
        for idx, sentence in enumerate(sentences):
            sent_doc = self.nlp(sentence)
            for ent in sent_doc.ents:
                if ent.label_ == "PERSON":
                    name = ent.text.strip()
                    story_state.add_character(name, last_mentioned=idx)
                elif ent.label_ in ["GPE", "LOC"]:
                    story_state.locations.add(ent.text.strip())
            death_patterns = [
                r"(\w+)\s+(died|was killed|perished|passed away)",
                r"(\w+)\s+is\s+(dead|deceased)"
            ]
            for pattern in death_patterns:
                for match in re.finditer(pattern, sentence, re.IGNORECASE):
                    char_name = match.group(1)
                    if char_name in story_state.characters:
                        story_state.characters[char_name].status = "dead"
        return story_state

    def _simple_parse(self, text: str, story_state: StoryState) -> StoryState:
        name_pattern = r'\b[A-Z][a-z]+\b'
        names = set(re.findall(name_pattern, text))
        for name in names:
            if len(name) > 1 and name not in ['The', 'A', 'An', 'This', 'That']:
                story_state.add_character(name)
        return story_state

class SymbolicValidator:
    def __init__(self):
        self.rules = {
            'character_death': self._check_character_death,
            'temporal_consistency': self._check_temporal_consistency,
            'character_consistency': self._check_character_traits
        }

    def validate(self, text: str, story_state: StoryState) -> List[StoryViolation]:
        violations = []
        for rule_name, rule_func in self.rules.items():
            try:
                rule_violations = rule_func(text, story_state)
                violations.extend(rule_violations)
            except Exception as e:
                print(f"Error in rule {rule_name}: {e}")
        return violations

    def _check_character_death(self, text: str, story_state: StoryState) -> List[StoryViolation]:
        violations = []
        sentences = text.split('.')
        for idx, sentence in enumerate(sentences):
            for char_name, character in story_state.characters.items():
                if character.status == "dead":
                    active_patterns = [
                        f"{char_name} said",
                        f"{char_name} walked",
                        f"{char_name} ran",
                        f"{char_name} looked"
                    ]
                    for pattern in active_patterns:
                        if pattern.lower() in sentence.lower():
                            violations.append(StoryViolation(
                                rule_name="character_death",
                                severity="high",
                                description=f"Dead character '{char_name}' is performing actions",
                                sentence_idx=idx,
                                suggestion=f"Remove action by {char_name} or revive the character first"
                            ))
        return violations

    def _check_temporal_consistency(self, text: str, story_state: StoryState) -> List[StoryViolation]:
        violations = []
        contradictory_patterns = [
            (r"morning", r"evening.*morning"),
            (r"yesterday", r"today.*yesterday")
        ]
        for pos_pattern, neg_pattern in contradictory_patterns:
            if re.search(pos_pattern, text, re.IGNORECASE) and re.search(neg_pattern, text, re.IGNORECASE):
                violations.append(StoryViolation(
                    rule_name="temporal_consistency",
                    severity="medium",
                    description="Potentially confusing temporal sequence",
                    suggestion="Clarify the timeline of events"
                ))
        return violations

    def _check_character_traits(self, text: str, story_state: StoryState) -> List[StoryViolation]:
        violations = []
        trait_contradictions = [
            (r"(\w+) was brave", r"\1 was cowardly"),
            (r"(\w+) was tall", r"\1 was short")
        ]
        for pos_pattern, neg_pattern in trait_contradictions:
            if re.search(pos_pattern, text) and re.search(neg_pattern, text):
                violations.append(StoryViolation(
                    rule_name="character_consistency",
                    severity="medium",
                    description="Character trait contradiction detected",
                    suggestion="Ensure character descriptions are consistent"
                ))
        return violations

class NeuralGenerator:
    def __init__(self, model_name: str = "llama2:7b-chat"):
        self.model_name = model_name
        self.ollama_available = OLLAMA_AVAILABLE

    def generate_story(self, prompt: str, max_tokens: int = 1000) -> str:
        if self.ollama_available:
            try:
                response = ollama.chat(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    options={"num_predict": max_tokens, "temperature": 0.7}
                )
                return response['message']['content']
            except Exception as e:
                print(f"Ollama error: {e}")
                return self._mock_generation(prompt)
        else:
            return self._mock_generation(prompt)

    def improve_story(self, original_story: str, violations: List[StoryViolation]) -> str:
        if not violations:
            return original_story
        feedback = self._format_feedback(violations)
        prompt = f"""Please improve the following story by addressing these issues:

{feedback}

Original Story:
{original_story}

Improved Story (keep the same general plot but fix the issues):"""
        return self.generate_story(prompt, max_tokens=1200)

    def _format_feedback(self, violations: List[StoryViolation]) -> str:
        feedback_lines = []
        for v in violations:
            feedback_lines.append(f"- {v.description}")
            if v.suggestion:
                feedback_lines.append(f"  Suggestion: {v.suggestion}")
        return "\n".join(feedback_lines)

    def _mock_generation(self, prompt: str) -> str:
        return '''Sarah walked through the dark forest, her flashlight cutting through the shadows.
She had been searching for her missing brother Tom for hours. Suddenly, she heard a voice calling her name.
"Sarah!" It was Tom's voice, coming from somewhere ahead. She ran toward the sound, pushing through branches.
Finally, she found Tom sitting by a small stream, looking confused but unharmed.
"I got lost," Tom said simply. "But I knew you'd find me."
Sarah hugged her brother tightly, relieved that their adventure had a happy ending.'''

class StorytellerEngine:
    def __init__(self, model_name: str = "llama2:7b-chat", max_iterations: int = 3):
        self.generator = NeuralGenerator(model_name)
        self.validator = SymbolicValidator()
        self.parser = StoryParser()
        self.max_iterations = max_iterations
        self._init_database()

    def _init_database(self):
        self.conn = sqlite3.connect('../data/stories.db')
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt TEXT,
                iteration INTEGER,
                story_text TEXT,
                violations TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def generate_and_improve(self, prompt: str) -> dict:
        results = {
            'prompt': prompt,
            'iterations': [],
            'final_story': '',
            'total_violations_fixed': 0
        }
        current_story = self.generator.generate_story(prompt)
        story_state = StoryState()

        for iteration in range(self.max_iterations):
            print(f"\n--- Iteration {iteration + 1} ---")
            story_state = self.parser.parse_story(current_story, story_state)
            violations = self.validator.validate(current_story, story_state)

            iteration_data = {
                'iteration': iteration + 1,
                'story': current_story,
                'violations': violations,
                'violation_count': len(violations),
                'story_state': story_state.to_dict()
            }
            results['iterations'].append(iteration_data)
            self._store_iteration(prompt, iteration + 1, current_story, violations)

            print(f"Found {len(violations)} violations")
            for v in violations:
                print(f" - {v.description}")

            if not violations or iteration == self.max_iterations - 1:
                break

            print("Generating improved version...")
            current_story = self.generator.improve_story(current_story, violations)

        results['final_story'] = current_story
        if results['iterations']:
            first_count = results['iterations'][0]['violation_count']
            last_count = results['iterations'][-1]['violation_count']
            results['total_violations_fixed'] = first_count - last_count

        return results

    def _store_iteration(self, prompt: str, iteration: int, story: str, violations: List[StoryViolation]):
        cursor = self.conn.cursor()
        violations_json = json.dumps([asdict(v) for v in violations])
        cursor.execute('''
            INSERT INTO stories (prompt, iteration, story_text, violations)
            VALUES (?, ?, ?, ?)
        ''', (prompt, iteration, story, violations_json))
        self.conn.commit()

    def close(self):
        if hasattr(self, 'conn'):
            self.conn.close()
