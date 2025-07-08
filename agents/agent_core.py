# core/agents.py
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Import prompts from the prompts module
from . import prompts


# LangChain components
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

# --- Gemini Model Configuration ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file.")
genai.configure(api_key=GOOGLE_API_KEY)

# ==============================================================================
#  AGENT 1: EXTRACTOR AGENT
# ==============================================================================

class ExtractorAgent:
    """
    Analyzes an HTML document to extract significant elements using a LangChain chain.
    """
    def __init__(self):
        # 1. Define the LLM
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0)

        # 2. Define the Prompt Template
        prompt_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(prompts.EXTRACTOR_AGENT_SYSTEM_PROMPT),
            HumanMessagePromptTemplate.from_template(
                "Analyze the following HTML document and generate the JSON array of locators according to your instructions.\n\n```html\n{html_content}\n```"
            )
        ])

        # 3. Define the Output Parser
        output_parser = JsonOutputParser()

        # 4. Create the Chain using LangChain Expression Language (LCEL)
        self.chain = prompt_template | llm | output_parser

    def run(self, html_content: str) -> list:
        """
        Takes HTML content as input and returns a list of extracted elements.
        """
        print("  [ExtractorAgent] Analyzing HTML to extract elements...")
        try:
            extracted_elements = self.chain.invoke({"html_content": html_content})
            print(f"  [ExtractorAgent] Successfully extracted {len(extracted_elements)} elements.")
            return extracted_elements
        except OutputParserException as e:
            print(f"  [ExtractorAgent] ERROR: LangChain failed to parse LLM response. {e}")
            return []
        except Exception as e:
            print(f"  [ExtractorAgent] An unexpected error occurred: {e}")
            return []
        
# ==============================================================================
#  AGENT 2: HEALER & MAPPER AGENT (LangChain Implementation)
# ==============================================================================

class HealerAgent:
    """
    Takes the old locator store and new elements, then maps and heals them using a LangChain chain.
    """
    def __init__(self):
        # 1. Define the LLM
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0)

        # 2. Define the Prompt Template
        prompt_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(prompts.HEALER_AGENT_SYSTEM_PROMPT),
            HumanMessagePromptTemplate.from_template("""
            Please perform your healing and mapping task on the following data.

            **Old Locator Store:**
            ```json
            {old_locator_data}
            {newly_extracted_elements}
            Generate the final, healed locator store as a single JSON object.
            """)
            ])
        
        # 3. Define the Output Parser
        output_parser = JsonOutputParser()

        # 4. Create the Chain
        self.chain = prompt_template | llm | output_parser

    def run(self, old_locator_data: dict, newly_extracted_elements: list) -> dict:
        """
        Takes the old store and new elements, returns the healed store.
        """
        print("  [HealerAgent] Mapping old locators to new elements and healing...")
        try:
            # Convert dicts/lists to JSON strings for the prompt
            old_locator_str = json.dumps(old_locator_data, indent=2)
            new_elements_str = json.dumps(newly_extracted_elements, indent=2)

            healed_store = self.chain.invoke({
                "old_locator_data": old_locator_str,
                "newly_extracted_elements": new_elements_str
            })
            print("  [HealerAgent] Successfully generated the healed locator store.")
            return healed_store
        except OutputParserException as e:
            print(f"  [HealerAgent] ERROR: LangChain failed to parse LLM response. {e}")
            return {}
        except Exception as e:
            print(f"  [HealerAgent] An unexpected error occurred: {e}")
            return {}
                