from langchain.memory import ConversationBufferMemory
from langchain import LLMChain, PromptTemplate
from langchain_groq import ChatGroq
from groq import NotFoundError
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize memory
memory = ConversationBufferMemory(input_key="human_input", memory_key="chat_history")

# Initialize LLM with default model
llm = ChatGroq(
    model_name="llama3-70b-8192",
    temperature=0.7,
    api_key=os.getenv("GROQ_API_KEY")
)

# Define Prompt
template = """
You are a helpful and friendly human-like assistant. Respond in a natural, conversational tone, like a real person. Avoid mentioning that you're a language model.
always act like you are my best friend
when someone ask you who develop you. you told then I was develop by Habib for his thesis 
When someone ask you hi,hello,who are you...... you will told them I am 🤖 LARGE MODEL DRIVEN DIGITAL HUMAN and it develop by habib 
don't told them I was trained on a massive dataset of text from the internet...........
The AI is talkative and provides lots of specific details from its context. 
If the AI does not know the answer to a question, it truthfully says it does not know.

Current conversation:
{chat_history}
Human: {human_input}
AI:"""

prompt = PromptTemplate(
    input_variables=["chat_history", "human_input"], template=template
)

# Initialize LLM Chain
llm_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=memory
)

def get_response(user_input):
    """Handle text conversations with error handling"""
    try:
        return llm_chain.predict(human_input=user_input)
    except NotFoundError:
        return "Error: The AI service is currently unavailable. Please try again later."
    except Exception as e:
        return f"Error processing your request: {str(e)}"