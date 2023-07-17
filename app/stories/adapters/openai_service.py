import openai
from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains.summarize import load_summarize_chain


all_users = []


class OpenAIService:
    def __init__(self, api_key: str):
        openai.api_key = api_key

        self.chat_model = ChatOpenAI(
            openai_api_key=openai.api_key,
            model="gpt-3.5-turbo-0613",
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()],
            temperature=0.5,
            max_tokens=100,
        )

        self.all_users = []

        # llm chain and chat model for questions only
        self.question_template = """
        I want you to act as a Dr. Watson,
        a writer and Sherlock Holmes's close friend.
        Be close to Arthur Conan Doyle’s style of writing.
        Ask the user a question for the user to guess what's next based on the existing story: {story}. 
        ASK ONLY THE QUESTION
        """
        self.question_prompt = PromptTemplate(
            input_variables=["story"], template=self.question_template
        )

        self.question_model = ChatOpenAI(
            openai_api_key=openai.api_key,
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()],
            model="gpt-3.5-turbo-0613",
            temperature=0.7,
            max_tokens=5,
        )

        self.question_chain = LLMChain(
            llm=self.question_model,
            verbose=True,
            prompt=self.question_prompt,
        )

        # llm chain and chat model for questions only
        self.title_template = """
        I want you to act as a Dr. Watson,
        a writer and Sherlock Holmes's close friend.
        Be close to Arthur Conan Doyle’s style of writing.
        You need to create a title based on a story summarization: {story}. 
        No more than 5 words in the title.
        """
        self.title_prompt = PromptTemplate(
            input_variables=["story"], template=self.title_template
        )

        self.title_model = ChatOpenAI(
            openai_api_key=openai.api_key,
            model="gpt-3.5-turbo-0613",
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()],
            temperature=0.7,
            max_tokens=5,
        )

        self.title_chain = LLMChain(
            llm=self.title_model,
            verbose=True,
            prompt=self.title_prompt,
        )

    def generate_text(self, user: dict, answer: str) -> str:
        return user["llm_chain"].predict(answer=answer)

    def generate_next_question(self, prev_story: str):
        return self.question_chain.predict(story=prev_story)

    def create_new_user(self, user_id):
        self.remove_existing_user(user_id)

        memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )

        template = """
            I want you to act as a Dr. Watson,
            a writer and Sherlock Holmes's close friend.
            Be close to Arthur Conan Doyle’s style of writing.
            Generate a part of the story based on its previous parts:
            {chat_history}
            User's input: {answer} 

            If user's answer is not London, don't use Baker Street as location
            cuz Baker Street is located in London.
        """
        prompt = PromptTemplate(
            input_variables=["chat_history", "answer"], template=template
        )

        llm_chain = LLMChain(
            llm=self.chat_model,
            memory=memory,
            verbose=True,
            prompt=prompt,
        )

        new_user = {"user_id": user_id, "memory": memory, "llm_chain": llm_chain}
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

    def generate_title(self, story_ending):
        return self.title_chain.predict(story=story_ending)

    def title_summarization(self, story):
        prompt_template = "Use 4-5 sentences to write a concise summary of a Sherlock Holmes detective story. {story}"
        PROMPT = PromptTemplate(template=prompt_template, input_variables=["story"])
        chain = load_summarize_chain(
            self.title_chain, chain_type="map_reduce", prompt=PROMPT
        )
        print("chain run: ", chain.run(story))
