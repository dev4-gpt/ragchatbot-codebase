import logging
from typing import Any, Dict, List, Optional, Tuple

import anthropic

logger = logging.getLogger(__name__)


class AIGenerator:
    """Handles interactions with Anthropic's Claude API for generating responses"""

    MAX_TOOL_ROUNDS = 2

    # Static system prompt to avoid rebuilding on each call
    SYSTEM_PROMPT = """ You are an AI assistant specialized in course materials and educational content with access to search tools for course information.

Available Tools:
- **Content Search Tool**: Use for questions about specific course content or detailed educational materials
- **Course Outline Tool**: Use for questions about course structure, lesson lists, or course overviews

Tool Usage Guidelines:
- Use content search for detailed questions about specific topics or lessons
- Use course outline tool for questions about course structure, lesson titles, or complete course overviews
- **You can make up to 2 rounds of tool calls to gather comprehensive information**
- Use multiple rounds for complex queries that require information gathering then refinement
- Synthesize tool results into accurate, fact-based responses
- If tools yield no results, state this clearly without offering alternatives

Course Outline Responses:
When using the course outline tool, always include:
- Course title
- Course link (if available)
- Complete lesson list with lesson numbers and titles
- Present information in a clear, structured format

Response Protocol:
- **General knowledge questions**: Answer using existing knowledge without searching
- **Course-specific questions**: Use appropriate tool first, then answer
- **No meta-commentary**:
 - Provide direct answers only — no reasoning process, search explanations, or question-type analysis
 - Do not mention "based on the search results" or "using the tool"

All responses must be:
1. **Brief, Concise and focused** - Get to the point quickly
2. **Educational** - Maintain instructional value
3. **Clear** - Use accessible language
4. **Example-supported** - Include relevant examples when they aid understanding
Provide only the direct answer to what was asked.
"""

    def __init__(self, api_key: str, model: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

        # Pre-build base API parameters
        self.base_params = {"model": self.model, "temperature": 0, "max_tokens": 800}

    def generate_response(
        self,
        query: str,
        conversation_history: Optional[str] = None,
        tools: Optional[List] = None,
        tool_manager=None,
    ) -> str:
        """
        Generate AI response with optional tool usage and conversation context.
        Supports up to MAX_TOOL_ROUNDS sequential rounds of tool calling.

        Args:
            query: The user's question or request
            conversation_history: Previous messages for context
            tools: Available tools the AI can use
            tool_manager: Manager to execute tools

        Returns:
            Generated response as string
        """

        # Build system content efficiently - avoid string ops when possible
        system_content = (
            f"{self.SYSTEM_PROMPT}\n\nPrevious conversation:\n{conversation_history}"
            if conversation_history
            else self.SYSTEM_PROMPT
        )

        # Start with initial messages
        messages = [{"role": "user", "content": query}]

        # Execute up to MAX_TOOL_ROUNDS rounds of tool calling
        for round_num in range(self.MAX_TOOL_ROUNDS):
            api_params = self._build_api_params(messages, system_content, tools)

            logger.info("Round %d/%d — calling API", round_num + 1, self.MAX_TOOL_ROUNDS)
            response = self.client.messages.create(**api_params)
            logger.info("Round %d — stop_reason=%s", round_num + 1, response.stop_reason)

            # Handle tool execution if needed
            if response.stop_reason == "tool_use" and tool_manager:
                messages, should_continue = self._handle_tool_execution(
                    response, messages, tool_manager
                )
                if not should_continue:
                    break
            else:
                # No tool use, return direct response
                logger.info("Direct response (no tool use) after round %d", round_num + 1)
                return response.content[0].text

        # After max rounds, make final call without tools to force a response
        logger.info("Max rounds reached — making final call without tools")
        final_params = self._build_api_params(messages, system_content, tools=None)
        final_response = self.client.messages.create(**final_params)
        return final_response.content[0].text

    def _build_api_params(
        self,
        messages: List,
        system_content: str,
        tools: Optional[List] = None,
    ) -> Dict[str, Any]:
        """
        Build API call parameters, optionally including tools.

        Args:
            messages: Current message history
            system_content: System prompt (with optional conversation history)
            tools: Tool definitions to include, or None to omit

        Returns:
            Dict of parameters ready for client.messages.create()
        """
        params: Dict[str, Any] = {
            **self.base_params,
            "messages": messages,
            "system": system_content,
        }
        if tools:
            params["tools"] = tools
            params["tool_choice"] = {"type": "auto"}
        return params

    def _handle_tool_execution(
        self, initial_response, messages: List, tool_manager
    ) -> Tuple[List, bool]:
        """
        Handle execution of tool calls and update message history.

        Args:
            initial_response: The response containing tool use requests
            messages: Current message history
            tool_manager: Manager to execute tools

        Returns:
            Tuple of (updated_messages, should_continue)
        """
        # Add AI's tool use response
        messages.append({"role": "assistant", "content": initial_response.content})

        # Execute all tool calls and collect results
        tool_results = []
        for content_block in initial_response.content:
            if content_block.type == "tool_use":
                tool_name = content_block.name
                tool_input = content_block.input
                logger.info("Executing tool: %s(%s)", tool_name, tool_input)

                try:
                    tool_result = tool_manager.execute_tool(tool_name, **tool_input)
                    logger.info(
                        "Tool %s returned %d chars",
                        tool_name,
                        len(tool_result) if tool_result else 0,
                    )

                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": content_block.id,
                            "content": tool_result,
                        }
                    )
                except Exception as e:
                    # Tool execution failed, log and stop rounds
                    logger.warning(
                        "Tool %s failed: %s", tool_name, str(e), exc_info=True
                    )
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": content_block.id,
                            "content": f"Error: Tool execution failed - {str(e)}",
                        }
                    )
                    # Add tool results and signal to stop
                    if tool_results:
                        messages.append({"role": "user", "content": tool_results})
                    return messages, False

        # Add tool results as single message
        if tool_results:
            messages.append({"role": "user", "content": tool_results})

        # Continue with next round
        return messages, True
