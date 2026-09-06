"""Registry of every tool the AI chat agent can call (Phase 6R). Each tool wraps an
existing service function — see `app/services/chat_agent.py` for the orchestration
loop that offers these to the configured `LLMProvider` and executes whichever one it
picks.
"""
from app.services.agent_tools import (
    apply_template_tool,
    create_project_tool,
    generate_video_tool,
    prepare_publish_tool,
    render_project_tool,
    select_media_tool,
)
from app.services.agent_tools.base import AgentTool

TOOLS: dict[str, AgentTool] = {
    tool.spec.name: tool
    for tool in (
        select_media_tool.TOOL,
        generate_video_tool.TOOL,
        create_project_tool.TOOL,
        render_project_tool.TOOL,
        prepare_publish_tool.TOOL,
        apply_template_tool.TOOL,
    )
}
