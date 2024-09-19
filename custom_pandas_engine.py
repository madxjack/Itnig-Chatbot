from llama_index.core.query_pipeline import QueryPipeline as QP, Link, InputComponent
from llama_index.experimental.query_engine.pandas import PandasInstructionParser
from llama_index.llms.groq import Groq
from llama_index.core import PromptTemplate
import pandas as pd
import os
import dotenv

dotenv.load_dotenv()

def create_custom_pandas_engine(df, column_descriptions):
    instruction_str = """
    1. Convert the query to executable Python code using Pandas.
    2. The final line of code should be a Python expression that can be called with the `eval()` function.
    3. The code should represent a solution to the query.
    4. PRINT ONLY THE EXPRESSION.
    5. Do not quote the expression.
    """

    # Generate detailed column information
    column_info = "\n".join([f"{col}: {desc}" for col, desc in column_descriptions.items()])

    pandas_prompt_str = """
    You are working with a pandas dataframe in Python.
    The name of the dataframe is `df`.
    Here's detailed information about each column in the DataFrame:
    {column_info}

    Follow these instructions:
    {instruction_str}
    Query: {query_str}

    Expression:
    """

    response_synthesis_prompt_str = """
    Given an input question, return a user friendly response to answer the query. Must be a natural language response.
    Query: {query_str}

    Pandas Instructions (optional):
    {pandas_instructions}

    Pandas Output: {pandas_output}

    Response: 
    """

    pandas_prompt = PromptTemplate(pandas_prompt_str).partial_format(
        instruction_str=instruction_str, 
        column_info=column_info
    )

    pandas_output_parser = PandasInstructionParser(df)

    response_synthesis_prompt = PromptTemplate(response_synthesis_prompt_str).partial_format(
        column_info=column_info
    )
    llm = Groq(model="llama-3.1-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))

    # Build the query pipeline
    qp = QP(
        modules={
            "input": InputComponent(),
            "pandas_prompt": pandas_prompt,
            "llm1": llm,
            "pandas_output_parser": pandas_output_parser,
            "response_synthesis_prompt": response_synthesis_prompt,
            "llm2": llm,
        },
        verbose=True,
    )
    qp.add_chain(["input", "pandas_prompt", "llm1", "pandas_output_parser"])
    qp.add_links([
        Link("input", "response_synthesis_prompt", dest_key="query_str"),
        Link("llm1", "response_synthesis_prompt", dest_key="pandas_instructions"),
        Link("pandas_output_parser", "response_synthesis_prompt", dest_key="pandas_output"),
    ])
    qp.add_link("response_synthesis_prompt", "llm2")

    return qp

# Function to run a query using the custom engine
def run_query(engine, query):
    # Configurar Pandas para mostrar todo el contenido de las celdas
    pd.set_option('display.max_colwidth', None)
    
    response = engine.run(query_str=query)
    
    # Extraer el contenido del mensaje de la respuesta
    if hasattr(response, 'message') and hasattr(response.message, 'content'):
        full_response = response.message.content
    elif isinstance(response, pd.Series):
        full_response = response.iloc[0] if len(response) > 0 else "No se encontró información."
    else:
        full_response = str(response)
    
    print("Respuesta completa:", full_response)
    
    # Restablecer la configuración de Pandas a su valor predeterminado
    pd.reset_option('display.max_colwidth')
    
    return full_response
