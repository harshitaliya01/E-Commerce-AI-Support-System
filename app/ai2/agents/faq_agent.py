from langchain_core.tools import tool

from app.rag.generator import generate_rag_response
from app.core.logging import get_logger

logger = get_logger(__name__)


@tool
async def handle_faq(question:str):

    """ 
    FAQ and company policies
    """ 

    response=await generate_rag_response(
        question
    )
    logger.info(
        f"FAQ response: {response}"
    )
    return response