
import time

from llm.ollama import OllamaProvider
from agents.proofreading import ProofreadingAgent


provider = OllamaProvider(
    model="qwen2.5:3b",
    base_url="http://localhost:11434",
    timeout=300
)

agent = ProofreadingAgent(provider)

text = """
Last weekend I went to the park with my friends and we was
having a really good time. The weather were sunny and warm,
so we decided to play football and eat some snacks.
We stayed there for many hours and didn't wanted to go home.
"""

print("Starting proofreading agent test...")

start = time.time()

try:
    result = agent.process(text)

    elapsed = time.time() - start

    print(f"\nCompleted in {elapsed:.2f} seconds")

    print("\nCORRECTED TEXT:")
    print(result["corrected_text"])

    print("\nSUGGESTED CHANGES:")
    for change in result["changes"]:
        print(change)

except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")

finally:
    print(f"\nTotal execution time: {time.time() - start:.2f} seconds")
