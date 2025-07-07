# chains.py
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain.schema.runnable import RunnableBranch, RunnableLambda
from pydantic import BaseModel, Field
from typing import Literal
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

# Step 1: Classification
class CommentType(BaseModel):
    category: Literal['spam', 'abusive', 'constructive', 'off-topic'] = Field(..., description="Type of the comment")

classification_prompt = PromptTemplate(
    template=open("prompts/classify_prompt.txt").read(),
    input_variables=["comment"],
    partial_variables={"format_instruction": PydanticOutputParser(pydantic_object=CommentType).get_format_instructions()}
)

classification_chain = classification_prompt | llm | PydanticOutputParser(pydantic_object=CommentType)

def load_prompt_template(file_path: str, moderator_name: str = "Community Team") -> PromptTemplate:
    with open(file_path, encoding='utf-8') as f:
        content = f.read()
    return PromptTemplate.from_template(content).partial(moderator_name=moderator_name)



# Load and prepare all category-specific prompt chains
spam_chain = load_prompt_template("prompts/spam_reply.txt") | llm | StrOutputParser()
abusive_chain = load_prompt_template("prompts/abusive_reply.txt") | llm | StrOutputParser()
constructive_chain = load_prompt_template("prompts/constructive_reply.txt") | llm | StrOutputParser()
offtopic_chain = load_prompt_template("prompts/offtopic_reply.txt") | llm | StrOutputParser()

# Create a dictionary to map comment categories to their reply chains
reply_chains = {
    "spam": spam_chain,
    "abusive": abusive_chain,
    "constructive": constructive_chain,
    "off-topic": offtopic_chain
}

# Branch logic: choose the right chain based on the classification result
reply_branch = RunnableBranch(
    *( (lambda x, cat=cat: x.category == cat, chain) for cat, chain in reply_chains.items() ),
    RunnableLambda(lambda _: "Could not classify comment.")  # fallback
)

# Final full moderation chain: classify → reply → return both
moderation_chain = classification_chain | (lambda x: {
    "category": x.category,
    "reply": reply_branch.invoke(x)
})

