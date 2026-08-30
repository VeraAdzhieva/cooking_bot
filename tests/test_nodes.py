from unittest.mock import MagicMock, patch

from agents.nodes import RouterDecision, create_router_node


def test_create_router_node_success() -> None:
    """
    Проверяет успешный сценарий router_node.
    """
    mock_llm = MagicMock()
    mock_router_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_router_llm

    mock_router_llm.invoke.return_value = RouterDecision(
        intent=["recipes", "planner"], reason="Пользователь просит рецепт и план"
    )

    with patch("agents.nodes.load_prompt", return_value="system prompt"):
        router_node = create_router_node(mock_llm)
        state = {
            "messages": [{"role": "user", "content": "спланируй меню и дай рецепт"}]
        }
        result = router_node(state)

        assert result == {"next_nodes": ["recipes", "planner"]}
        mock_llm.with_structured_output.assert_called_once_with(RouterDecision)


def test_create_router_node_reject() -> None:
    """
    Проверяет сценарий отклонения запроса пользователя.
    """
    mock_llm = MagicMock()
    mock_router_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_router_llm

    mock_router_llm.invoke.return_value = RouterDecision(
        intent=["reject"], reason="Не относится к кулинарии"
    )

    with patch("agents.nodes.load_prompt", return_value="system prompt"):
        router_node = create_router_node(mock_llm)
        state = {"messages": [{"role": "user", "content": "как починить машину"}]}
        result = router_node(state)

        assert result == {"next_nodes": ["reject"]}
