from llm.ollama import OllamaProvider
from agents.proofreading import ProofreadingAgent


# Initialize the provider
provider = OllamaProvider()

# Initialize the agent
agent = ProofreadingAgent(provider)


test_sentences = [
    "He go to school yesterday.",
    "I has a apple.",
    "The weather is beautiful today.",
    "She don't like coffee.",
    "This sentence is already correct."
]

for text in test_sentences:

    print("\n" + "=" * 50)
    print("ORIGINAL:", text)

    result = agent.process(text)

    print("CORRECTED:", result["corrected_text"])
    print("CHANGES:", result["changes"])