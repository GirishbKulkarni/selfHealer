import json
import os

# Import the agent classes from the core module
# This single import works regardless of whether agents.py uses LangChain or not.
from agents.agent_core import ExtractorAgent, HealerAgent

# --- Configuration ---
# Define paths relative to the script's location for robustness.
INPUT_DIR = "input_data"
OUTPUT_DIR = "output_data"
LOCATOR_STORE_FILE = os.path.join(INPUT_DIR, "locator_store.json")
UPDATED_DOM_FILE = os.path.join(INPUT_DIR, "DEMOQA.html")
HEALED_STORE_FILE = os.path.join(OUTPUT_DIR, "locator_store_healed.json")
INTERMEDIATE_FILE = os.path.join(OUTPUT_DIR, "extracted_elements.json")

def main():
    """
    Orchestrates the two-agent workflow for proactive healing.
    """
    print("--- Starting Proactive Multi-Agent Healing Process ---")
    
    # Ensure the output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Load initial input files from disk
    try:
        print(f"Reading old locators from: {LOCATOR_STORE_FILE}")
        with open(LOCATOR_STORE_FILE, 'r', encoding='utf-8') as f:
            old_locator_data = json.load(f)

        print(f"Reading updated DOM from: {UPDATED_DOM_FILE}")
        with open(UPDATED_DOM_FILE, 'r', encoding='utf-8') as f:
            html_content = f.read()
            
    except FileNotFoundError as e:
        print(f"\nERROR: Input file not found - {e}. Please ensure it exists in the 'input_data' directory.")
        print("Halting process.")
        return
    except json.JSONDecodeError as e:
        print(f"\nERROR: Could not parse {LOCATOR_STORE_FILE}. It is not valid JSON - {e}.")
        print("Halting process.")
        return

    # ==========================================================================
    #  STEP 1: Invoke Agent 1 (Extractor)
    # ==========================================================================
    print("\n>>> Invoking Agent 1: Extractor Agent <<<")
    extractor_agent = ExtractorAgent()
    extracted_elements = extractor_agent.run(html_content)

    if not extracted_elements:
        print("\nExtractor Agent failed to produce results. Halting process.")
        return

    # Save the intermediate output from Agent 1 for debugging and transparency
    with open(INTERMEDIATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(extracted_elements, f, indent=2)
    print(f"  [Orchestrator] Saved intermediate results to: {INTERMEDIATE_FILE}")

    # ==========================================================================
    #  STEP 2: Invoke Agent 2 (Healer/Mapper)
    # ==========================================================================
    print("\n>>> Invoking Agent 2: Healer & Mapper Agent <<<")
    healer_agent = HealerAgent()
    healed_store = healer_agent.run(old_locator_data, extracted_elements)

    if not healed_store:
        print("\nHealer Agent failed to produce results. Halting process.")
        return

    # ==========================================================================
    #  STEP 3: Save Final Output
    # ==========================================================================
    with open(HEALED_STORE_FILE, 'w', encoding='utf-8') as f:
        json.dump(healed_store, f, indent=2)

    print("\n--- Multi-Agent Healing Process Complete ---")
    print(f"Final healed locator store has been successfully saved to: {HEALED_STORE_FILE}")

if __name__ == "__main__":
    main()