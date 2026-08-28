import os

from langchain_mcp_adapters.client import MultiServerMCPClient

from utils.logger import setup_logger

logger = setup_logger()


async def load_mcp_tools() -> dict:
    """
    Загружает инструменты из MCP.
    """
    logger.info("Загрузка инструментов MCP")
    mcp_config = {
        "my_local_mcp": {
            "transport": "http",
            "url": os.getenv("MCP_HOST"),
            "headers": {"Authorization": f"Bearer {os.getenv('MCP_API_KEY')}"},
        }
    }

    client = MultiServerMCPClient(mcp_config)
    all_tools = await client.get_tools()
    logger.info(f"Загружено инструментов из MCP: {len(all_tools)}")
    return all_tools
