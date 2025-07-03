import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from . import uiObserverPrompts
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import JsonOutputParser


load_dotenv()
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise EnvironmentError("GOOGLE_API_KEY not found in environment variables.")


class ElementExtractor:
    def __init__(self):
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-Pro", temperature=0)
        promptTemplate = ChatPromptTemplate.from_messages(
                [SystemMessagePromptTemplate.from_template(uiObserverPrompts.EXTRACTOR_AGENT_SYSTEM_PROMPT), 
                HumanMessagePromptTemplate.from_template("Analyze the following HTML DOM structure and identify all significant, interactive,and uniquely identifiable elements. \n\n {html_content}")])
        outputParser = JsonOutputParser()

        self.chain = promptTemplate | llm | outputParser

    def run(self, html_content:str) -> list:
        try:
            extracted_elements = self.chain.invoke({"html_content": html_content})
            print("Successfully extracted elements from the HTML content.")
            return extracted_elements
        except Exception as e:
            print(f"Error extracting elements from the HTML content: {e}")
            return []


class selfHealer:
    def __init__(self):
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-Pro", temperature=0)
        promptTemplate = ChatPromptTemplate.from_messages
        ( 
            [SystemMessagePromptTemplate.from_template(uiObserverPrompts.SELF_HEALER_SYSTEM_PROMPT),
             HumanMessagePromptTemplate.from_template("""
            Please perform healing and mapping task on the following data.
            **Old Locator Store:**
            ```json
            {old_locator_data}
            ```
            **Newly Extracted Elements:**
            ```json
            {newly_extracted_elements}
            ```
            Generate the final, healed locator store as a single JSON object.
            """)
        ])
        outputParser = JsonOutputParser()

        self.chain = promptTemplate | llm | outputParser

    def run(self, old_locator_data:dict, newly_extracted_elements:list) -> dict:
        try:
            old_locator_data_str = json.dumps(old_locator_data, indent=2)
            newly_extracted_elements_str = json.dumps(newly_extracted_elements, indent=2)
            
            healed_locator_data = self.chain.invoke({
                "old_locator_data": old_locator_data_str,
                "newly_extracted_elements": newly_extracted_elements_str })

            print("Successfully healed the locator store.")
            return healed_locator_data
        except Exception as e:
            print(f"Error healing the locator store: {e}")
            return {}