from llm.mock import MockLLM
from agents.proofreading import ProofreadingAgent


mock = MockLLM([
    {
        "corrected_text": "He went to school yesterday.",
        "changes": [
            {
                "original": "go",
                "replacement": "went",
                "explanation": "The verb should be in the past tense.",
                "category": "grammar"
            }
        ]
    }
])

agent = ProofreadingAgent(mock)

result = agent.process(
    "He go to school yesterday."
)

print(result)