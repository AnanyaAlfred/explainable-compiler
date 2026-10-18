import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from explainability.recorder import ExplanationRecorder

def test_recorder():
    recorder = ExplanationRecorder(output_path="explainability/report.json")
    
    # Simulate logging a compiler optimization pass
    recorder.log_event(
        pass_name="Constant Folding",
        what="Folded arithmetic addition '10 + 20' into static value '30'.",
        where="Line 2, Block 0",
        why="Eliminate unnecessary runtime arithmetic overhead.",
        how="AST static visitor evaluation.",
        effect="Reduced instruction count by 1."
    )
    
    recorder.save_report()
    print("Explanation report generated successfully!")

if __name__ == "__main__":
    test_recorder()