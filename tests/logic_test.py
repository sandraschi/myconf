import sys
import os

# Add apps/agent to path to import logic
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "apps", "agent"))

from logic import ReductionistLogic


def test_saliency_detection():
    logic = ReductionistLogic()

    # Test high salience (jargon heavy)
    high_entropy = "We need to manifest a holistic paradigm shift for alignment and synergy."
    dilution = logic.analyze_saliency(high_entropy)
    print(f"High Entropy Test: {dilution}")
    assert dilution >= 0.7

    # Test low salience (technical/materialist)
    low_entropy = "The CPU temperature is 45 degrees Celsius."
    dilution = logic.analyze_saliency(low_entropy)
    print(f"Low Entropy Test: {dilution}")
    assert dilution == 0.0


if __name__ == "__main__":
    try:
        test_saliency_detection()
        print("✅ ReductionistLogic tests passed.")
    except AssertionError as e:
        print("❌ ReductionistLogic tests failed.")
        sys.exit(1)
