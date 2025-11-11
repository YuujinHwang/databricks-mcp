"""
SQL Statement Execution API Handler
Handles SQL statement execution operations on Databricks SQL warehouses
https://docs.databricks.com/api/workspace/statementexecution
"""
import logging
from typing import Any
from mcp.types import Tool

logger = logging.getLogger(__name__)


class SQLHandler:
    """Handler for Databricks SQL Statement Execution API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        """Return list of SQL execution tools"""
        return [
            Tool(
                name="execute_statement",
                description="Execute a SQL statement on a SQL warehouse and return results",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "warehouse_id": {
                            "type": "string",
                            "description": "The SQL warehouse ID to execute the statement on",
                        },
                        "statement": {
                            "type": "string",
                            "description": "The SQL statement to execute",
                        },
                        "catalog": {
                            "type": "string",
                            "description": "The catalog to use (optional)",
                        },
                        "schema": {
                            "type": "string",
                            "description": "The schema to use (optional)",
                        },
                        "wait_timeout": {
                            "type": "string",
                            "description": "Time to wait for results (e.g., '30s'). Use '0s' for async execution. Default is '10s'",
                        },
                        "row_limit": {
                            "type": "integer",
                            "description": "Maximum number of rows to return",
                        },
                    },
                    "required": ["warehouse_id", "statement"],
                },
            ),
            Tool(
                name="get_statement",
                description="Get the status and results of a SQL statement execution",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "statement_id": {
                            "type": "string",
                            "description": "The statement ID returned from execute_statement",
                        }
                    },
                    "required": ["statement_id"],
                },
            ),
            Tool(
                name="cancel_statement_execution",
                description="Cancel an executing SQL statement",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "statement_id": {
                            "type": "string",
                            "description": "The statement ID to cancel",
                        }
                    },
                    "required": ["statement_id"],
                },
            ),
            Tool(
                name="execute_statements_batch",
                description="Execute multiple SQL statements sequentially in a single operation (batch execution)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "warehouse_id": {
                            "type": "string",
                            "description": "The SQL warehouse ID to execute statements on",
                        },
                        "statements": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Array of SQL statements to execute sequentially",
                        },
                        "catalog": {
                            "type": "string",
                            "description": "The catalog to use (optional)",
                        },
                        "schema": {
                            "type": "string",
                            "description": "The schema to use (optional)",
                        },
                        "wait_timeout": {
                            "type": "string",
                            "description": "Time to wait for results per statement (e.g., '30s'). Default is '10s'",
                        },
                        "row_limit": {
                            "type": "integer",
                            "description": "Maximum number of rows to return per statement",
                        },
                    },
                    "required": ["warehouse_id", "statements"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, workspace_client, run_operation) -> Any:
        """
        Handle SQL execution tool calls

        Args:
            name: Tool name
            arguments: Tool arguments
            workspace_client: Databricks workspace client instance
            run_operation: Function to wrap operations with retry logic

        Returns:
            Operation result
        """
        if name == "execute_statement":
            from databricks.sdk.service.sql import ExecuteStatementRequestParams

            params = ExecuteStatementRequestParams(
                statement=arguments["statement"],
                warehouse_id=arguments["warehouse_id"],
                catalog=arguments.get("catalog"),
                schema=arguments.get("schema"),
                wait_timeout=arguments.get("wait_timeout", "10s"),
            )

            if "row_limit" in arguments:
                params.row_limit = arguments["row_limit"]

            response = workspace_client.statement_execution.execute_statement(**params.as_dict())

            # Format response
            result = {
                "statement_id": response.statement_id,
                "status": str(response.status.state) if response.status else None,
            }

            # Include result data if available
            if response.result:
                data_array = response.result.data_array if response.result.data_array else None

                # Check if we need to fetch additional chunks
                if response.manifest and response.manifest.total_chunk_count and response.manifest.total_chunk_count > 1:
                    # Fetch all chunks to get complete results
                    all_data = list(data_array) if data_array else []

                    for chunk_index in range(1, response.manifest.total_chunk_count):
                        chunk_response = workspace_client.statement_execution.get_statement_result_chunk_n(
                            statement_id=response.statement_id,
                            chunk_index=chunk_index
                        )
                        if chunk_response.data_array:
                            all_data.extend(chunk_response.data_array)

                    data_array = all_data
                    logger.info(f"Fetched {response.manifest.total_chunk_count} chunks with {len(all_data)} total rows")

                result["result"] = {
                    "row_count": response.result.row_count,
                    "data_array": data_array,
                    "truncated": response.result.truncated,
                }
                if response.manifest:
                    result["manifest"] = {
                        "schema": response.manifest.schema.as_dict() if response.manifest.schema else None,
                        "total_row_count": response.manifest.total_row_count,
                        "total_chunk_count": response.manifest.total_chunk_count,
                        "chunks_fetched": response.manifest.total_chunk_count if response.manifest.total_chunk_count else 1,
                    }

            return result

        elif name == "get_statement":
            response = workspace_client.statement_execution.get_statement(statement_id=arguments["statement_id"])

            result = {
                "statement_id": response.statement_id,
                "status": str(response.status.state) if response.status else None,
            }

            if response.result:
                data_array = response.result.data_array if response.result.data_array else None

                # Check if we need to fetch additional chunks
                if response.manifest and response.manifest.total_chunk_count and response.manifest.total_chunk_count > 1:
                    # Fetch all chunks to get complete results
                    all_data = list(data_array) if data_array else []

                    for chunk_index in range(1, response.manifest.total_chunk_count):
                        chunk_response = workspace_client.statement_execution.get_statement_result_chunk_n(
                            statement_id=response.statement_id,
                            chunk_index=chunk_index
                        )
                        if chunk_response.data_array:
                            all_data.extend(chunk_response.data_array)

                    data_array = all_data
                    logger.info(f"Fetched {response.manifest.total_chunk_count} chunks with {len(all_data)} total rows")

                result["result"] = {
                    "row_count": response.result.row_count,
                    "data_array": data_array,
                    "truncated": response.result.truncated,
                }
                if response.manifest:
                    result["manifest"] = {
                        "schema": response.manifest.schema.as_dict() if response.manifest.schema else None,
                        "total_row_count": response.manifest.total_row_count,
                        "total_chunk_count": response.manifest.total_chunk_count,
                        "chunks_fetched": response.manifest.total_chunk_count if response.manifest.total_chunk_count else 1,
                    }

            return result

        elif name == "cancel_statement_execution":
            workspace_client.statement_execution.cancel_execution(statement_id=arguments["statement_id"])
            return {"status": "cancelled", "statement_id": arguments["statement_id"]}

        elif name == "execute_statements_batch":
            from databricks.sdk.service.sql import ExecuteStatementRequestParams

            warehouse_id = arguments["warehouse_id"]
            statements = arguments["statements"]
            catalog = arguments.get("catalog")
            schema = arguments.get("schema")
            wait_timeout = arguments.get("wait_timeout", "10s")
            row_limit = arguments.get("row_limit")

            # Execute statements sequentially (they may have dependencies)
            results = []
            for idx, statement in enumerate(statements):
                try:
                    params = ExecuteStatementRequestParams(
                        statement=statement,
                        warehouse_id=warehouse_id,
                        catalog=catalog,
                        schema=schema,
                        wait_timeout=wait_timeout,
                    )

                    if row_limit:
                        params.row_limit = row_limit

                    response = workspace_client.statement_execution.execute_statement(**params.as_dict())

                    # Format response
                    statement_result = {
                        "statement_index": idx,
                        "statement": statement,
                        "statement_id": response.statement_id,
                        "status": str(response.status.state) if response.status else None,
                    }

                    # Include result data if available
                    if response.result:
                        statement_result["result"] = {
                            "row_count": response.result.row_count,
                            "data_array": response.result.data_array[:100] if response.result.data_array else None,
                            "truncated": response.result.truncated,
                        }
                        if response.manifest:
                            statement_result["manifest"] = {
                                "schema": response.manifest.schema.as_dict() if response.manifest.schema else None,
                                "total_row_count": response.manifest.total_row_count,
                            }

                    results.append({"status": "success", **statement_result})

                except Exception as e:
                    results.append({
                        "statement_index": idx,
                        "statement": statement,
                        "status": "failed",
                        "error": str(e)
                    })
                    # Continue executing remaining statements even if one fails

            return {
                "warehouse_id": warehouse_id,
                "total": len(statements),
                "successful": len([r for r in results if r["status"] == "success"]),
                "failed": len([r for r in results if r["status"] == "failed"]),
                "results": results
            }

        return None
