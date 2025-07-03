from agents.uiObserver import ElementExtractor, selfHealer
import json
import os

INPUT_DIR = "inpurData"
OUTPUT_DIR = "output"

locator_store_file = os.path.join(INPUT_DIR, "locator_store.json")
updatedDOMFile = os.path.join(INPUT_DIR, "htmlPages/DEMOQA.html")

healedStoreFile = os.path.join(OUTPUT_DIR, "healed_locator_store.json")
intermediateStoreFile = os.path.join(OUTPUT_DIR, "intermediate_locator_store.json")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try: 
        with open(locator_store_file, "r", encoding="utf-8") as f:
            oldlocator_store = json.load(f)
            print("Old json is successfully loaded")
        with open(updatedDOMFile, "r", encoding="utf-8") as f:
            updated_dom = f.read()
            print("Updated DOM is successfully loaded")

    except Exception as e:
        print(f"Error loading the files: {e}")
        return []
    
    element_extractor = ElementExtractor()
    extracted_elements = element_extractor.run(updated_dom)
    if not extracted_elements:
        print("No elements were extracted from the updated DOM.")
        return []

    with open(intermediateStoreFile, "w", encoding="utf-8") as f:
        json.dump(extracted_elements, f, indent=2)
    
    print("Intermediate locator store is successfully saved.")


    self_healer = selfHealer()
    healed_locator_data = self_healer.run(oldlocator_store, extracted_elements)
    if not healed_locator_data:
        print("No healed locator data was generated.")
        return []
    
    with open(healedStoreFile, "w", encoding="utf-8") as f:
        json.dump(healed_locator_data, f, indent=2)
        print("Healed locator store is successfully saved.")

if __name__ == "__main__":
    main()