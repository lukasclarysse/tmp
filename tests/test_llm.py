from llm.ollama import OllamaProvider


provider = OllamaProvider()

schema = {
    "type": "object",
    "properties": {
        "corrected_text": {
            "type": "string"
        },
        "explanation": {
            "type": "string"
        }
    },
    "required": [
        "corrected_text",
        "explanation"
    ],
    "additionalProperties": False
}

prompt = """
You are a proofreading assistant.

Correct the grammar of the following sentence.

Original sentence:
"He go to school yesterday."

Return the corrected sentence and briefly explain the correction.
"""

try:
    result = provider.generate(prompt, schema)

    print("\nLLM RESPONSE:")
    print(result)

except Exception as e:
    print(f"\nERROR: {e}")