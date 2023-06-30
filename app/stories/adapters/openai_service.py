import openai
from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

class OpenAIService:
    def __init__(self, api_key: str):
        openai.api_key = api_key

        memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )

         # llm chain and chat model for questions only
        self.template = """I want you to act as a Dr. Watson,
                a writer and Sherlock Holmes's close friend. Always write from Dr.Watson's perspective.
                Be close to Arthur Conan Doyle’s style of writing.
                My request is to generate a story according to the user's questions and answers. 
                {chat_history}
                User's input: {answer} """
        
        self.prompt = PromptTemplate(
            input_variables=["chat_history", "answer"], template=self.template
        )

        self.model = ChatOpenAI(
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()],
            openai_api_key=openai.api_key,
            model="gpt-3.5-turbo-0613",
            temperature=0.7,
            max_tokens=900,
        )

        self.llm_chain = LLMChain(
            llm=self.model,
            verbose=True,
            memory=memory,
            prompt=self.prompt,
        )
    

    def generate_text(self, answer: str) -> str:
        return self.llm_chain.predict(answer=answer)
