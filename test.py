from langchain_mistralai import ChatMistralAI

llm = ChatMistralAI(
    api_key="",
    model="devstral-latest",
    temperature=0.1,
)

response = llm.invoke("Say hello")
print(response.content)