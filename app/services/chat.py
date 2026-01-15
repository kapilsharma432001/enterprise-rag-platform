from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.config import settings

llm = ChatOpenAI(
    model = "gpt-4o",
    temperature = 0, # set to 0 for maximum factual acuuracy (less creative)
    openai_api_key = settings.OPENAI_API_KEY,
)

async def generate_rag_response(query: str, context_chunks: list):
    """
    1. Format the retrieved context chunks into a single text block.
    2. Send the prompt to the LLM
    """

    # 1. join the content of the retrived docs
    # We also track the sources to return them later
    context_text = '\n\n---\n\n'.join([doc['content'] for doc in context_chunks])

    # 2. Define the system prompt (the rules)
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", """You are an expert enterprise assistant. 
        Strictly answer the user's question based ONLY on the following context. 
        If the answer is not in the context, say 'I do not have enough information to answer that.'
        Do not make up facts.
        
        Context:
        {context}
        """),
        ("user", "{question}")
    ])

    # 3. Create the chain
    chain = prompt_template | llm | StrOutputParser()

    # 4. Invoke the chain
    answer = await chain.ainvoke({
        "context": context_text,
        "question": query
    })

    return answer