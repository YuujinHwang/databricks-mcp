"""
Genie (AI/BI) API Handler
Handles Genie conversation and message operations
https://docs.databricks.com/api/workspace/genie
"""
from typing import Any
from mcp.types import Tool


class GenieHandler:
    """Handler for Databricks Genie (AI/BI) API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        """Return list of Genie tools"""
        return [
            Tool(
                name="start_genie_conversation",
                description="Start a new conversation in a Genie space",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "space_id": {
                            "type": "string",
                            "description": "The Genie space ID",
                        }
                    },
                    "required": ["space_id"],
                },
            ),
            Tool(
                name="create_genie_message",
                description="Create a message in a Genie conversation (ask Genie a question)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "space_id": {
                            "type": "string",
                            "description": "The Genie space ID",
                        },
                        "conversation_id": {
                            "type": "string",
                            "description": "The conversation ID",
                        },
                        "content": {
                            "type": "string",
                            "description": "The message content (your question to Genie)",
                        },
                    },
                    "required": ["space_id", "conversation_id", "content"],
                },
            ),
            Tool(
                name="get_genie_message",
                description="Get details of a specific message in a Genie conversation",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "space_id": {"type": "string", "description": "The Genie space ID"},
                        "conversation_id": {"type": "string", "description": "The conversation ID"},
                        "message_id": {"type": "string", "description": "The message ID"},
                    },
                    "required": ["space_id", "conversation_id", "message_id"],
                },
            ),
            Tool(
                name="get_genie_message_query_result",
                description="Get SQL query result from a Genie message that executed a query",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "space_id": {"type": "string", "description": "The Genie space ID"},
                        "conversation_id": {"type": "string", "description": "The conversation ID"},
                        "message_id": {"type": "string", "description": "The message ID"},
                        "attachment_id": {
                            "type": "string",
                            "description": "The attachment ID (query attachment)",
                        },
                    },
                    "required": ["space_id", "conversation_id", "message_id", "attachment_id"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, workspace_client, run_operation) -> Any:
        """
        Handle Genie tool calls

        Args:
            name: Tool name
            arguments: Tool arguments
            workspace_client: Databricks workspace client instance
            run_operation: Function to wrap operations with retry logic

        Returns:
            Operation result
        """
        if name == "start_genie_conversation":
            conversation = workspace_client.genie.start_conversation(space_id=arguments["space_id"])
            return {
                "conversation_id": conversation.conversation_id,
                "space_id": arguments["space_id"],
            }

        elif name == "create_genie_message":
            from databricks.sdk.service.dashboards import MessageContent

            message = workspace_client.genie.create_message(
                space_id=arguments["space_id"],
                conversation_id=arguments["conversation_id"],
                content=MessageContent(query=arguments["content"]),
            )

            result = {
                "message_id": message.id,
                "conversation_id": arguments["conversation_id"],
                "status": str(message.status),
            }

            # Include attachments if available
            if message.attachments:
                result["attachments"] = [
                    {
                        "id": att.id,
                        "type": str(att.type) if hasattr(att, 'type') else None,
                    }
                    for att in message.attachments
                ]

            return result

        elif name == "get_genie_message":
            message = workspace_client.genie.get_message(
                space_id=arguments["space_id"],
                conversation_id=arguments["conversation_id"],
                message_id=arguments["message_id"],
            )
            return message.as_dict()

        elif name == "get_genie_message_query_result":
            query_result = workspace_client.genie.get_message_query_result(
                space_id=arguments["space_id"],
                conversation_id=arguments["conversation_id"],
                message_id=arguments["message_id"],
                attachment_id=arguments["attachment_id"],
            )
            return query_result.as_dict()

        return None
