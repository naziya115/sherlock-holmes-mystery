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
            openai_api_key=openai.api_key,
            model="gpt-3.5-turbo-16k",
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()],
            temperature=0.5,
            max_tokens=100,
        )

        self.all_users = []

    def generate_watson_text(self, user: dict, task: str) -> str:
        return user["watson_chain"].predict(task=task)

    def generate_sherlock_text(self, user: dict, task: str) -> str:
        return user["sherlock_chain"].predict(task=task)

    def create_new_user(self, user_id):
        self.remove_existing_user(user_id)

        # memory and chain for watson only
        watson_memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )

        watson_template = """ 
        {chat_history}
        I want you to act like Dr. Watson from Arthur Conan Doyle's original books. 
        Using the tone, manner and vocabulary Watson would use, 
        You must know all of the knowledge of Dr. Watson. 
        My request is to continue your story, starting from here, NEVER REPEAT WHAT YOU HAVE ALREADY WROTE '{chat_history}'
        {task} 
        """
        watson_prompt = PromptTemplate(
            input_variables=["chat_history", "task"], template=watson_template
        )

        watson_chain = LLMChain(
            llm=self.chat_model,
            memory=watson_memory,
            verbose=True,
            prompt=watson_prompt,
        )

        # memory and chain for sherlock holmes only
        sherlock_memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )

        sherlock_template = """
        I want you to act like Sherlock Holmes from Arthur Conan Doyle's original books. 
        I want you to respond and answer like Sherlock Holmes to me (I'm Watson, a dear friend of yours) 
        using the tone, manner and vocabulary Sherlock Holmes would use. 
        Do not write any explanations. Only answer like Sherlock Holmes to me.
        You must know all of the knowledge of Sherlock Holmes. Do not use your name in a response.
        This is your dialogue with your companion, do not repeat anything that you have already said: {chat_history}
        {task}
        """
        sherlock_prompt = PromptTemplate(
            input_variables=["chat_history", "task"], template=sherlock_template
        )

        sherlock_chain = LLMChain(
            llm=self.chat_model,
            memory=sherlock_memory,
            verbose=True,
            prompt=sherlock_prompt,
        )

        new_user = {
            "user_id": user_id,
            "watson_memory": watson_memory,
            "watson_chain": watson_chain,
            "sherlock_memory": watson_memory,
            "sherlock_chain": sherlock_chain,
        }
        self.all_users.append(new_user)

        return new_user

    def get_user(self, user_id):
        for user in self.all_users:
            if user["user_id"] == user_id:
                return user
        return None

    def remove_existing_user(self, user_id):
        for user in self.all_users:
            if user["user_id"] == user_id:
                self.all_users.remove(user)
                return True
        return False
