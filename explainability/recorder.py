import json
import os

class ExplanationRecorder:
    def __init__(self, output_path="explainability/report.json"):
        self.output_path = output_path
        self.events = []

    def log_event(self, pass_name: str, what: str, where: str, why: str, how: str, effect: str):
        """Record a single optimization pass explanation."""
        event = {
            "pass_name": pass_name,
            "what": what,
            "where": where,
            "why": why,
            "how": how,
            "effect": effect
        }
        self.events.append(event)

    def save_report(self):
        """Saves all logged events to a structured JSON report file."""
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(self.events, f, indent=4)
        print(f"Explainability report successfully saved to {self.output_path}")