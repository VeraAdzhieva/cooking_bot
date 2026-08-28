import json

from langchain_core.callbacks import BaseCallbackHandler


class MCPToolCallbackHandler(BaseCallbackHandler):
    """
    Перехватывает вызовы инструментов и логирует их.
    """

    def __init__(self, logger):
        self.logger = logger

    def on_tool_start(self, serialized, input_str, **kwargs):
        """Срабатывает, когда LLM решает вызвать инструмент."""
        tool_name = serialized.get("name", "unknown_tool")
        try:
            args_dict = json.loads(input_str)
            args_formatted = json.dumps(args_dict, ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            args_formatted = input_str

        self.logger.info(
            f"[MCP CALL] Инструмент: {tool_name}\n Аргументы:\n{args_formatted}"
        )

    def on_tool_end(self, output, **kwargs):
        """
        Срабатывает, когда MCP-сервер (Obsidian) вернул результат.
        """
        output_str = str(output)
        if len(output_str) > 400:
            output_str = (
                output_str[:400] + "\n... [ОБРЕЗАНО ДЛЯ ЛОГА, ПОЛНЫЙ ОТВЕТ УШЕЛ В LLM]"
            )

        self.logger.info(f"[MCP RESULT] Получен ответ от инструмента:\n{output_str}")
        self.logger.info("-" * 60)
