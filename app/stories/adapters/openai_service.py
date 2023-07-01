import openai
from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler


all_users = []

class OpenAIService:
    def __init__(self, api_key: str):
        openai.api_key = api_key

        self.chat_model = ChatOpenAI(
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()],
            openai_api_key=openai.api_key,
            model="gpt-3.5-turbo-0613",
            temperature=0.7,
            max_tokens=900,
        )

        self.all_users = []


    

    def generate_text(self, user: dict, answer: str) -> str:

        return user["llm_chain"].predict(answer=answer)

    def create_new_user(self, user_id):
        memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )

        template = """
            I want you to act as a Dr. Watson,
            a writer and Sherlock Holmes's close friend.
            Be close to Arthur Conan Doyle’s style of writing.
            Generate story based on the previous parts of the story:
            {chat_history}
            User input: {answer} 
        """
        prompt = PromptTemplate(
            input_variables=["chat_history", "answer"], template=template
        )

        llm_chain = LLMChain(
            llm=self.chat_model, memory=memory, verbose=True, prompt=prompt
        )
        
        new_user = {
            "user_id": user_id,
            "memory": memory,
            "llm_chain": llm_chain
        }
        self.all_users.append(new_user)

        return new_user
    
    def get_user(self, user_id):
        for user in self.all_users:
            if user["user_id"] == user_id:
                return user
        return None