from dotenv import load_dotenv

load_dotenv()

from agents.supervisor import graph


question = input("You: ")


result = graph.invoke({
    "question": question,
    "route": "",
    "answer": ""
})


print("\nAssistant:")
print(result["answer"])