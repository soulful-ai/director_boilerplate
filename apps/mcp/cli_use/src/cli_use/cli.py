"""
Command-line interface for cli_use.
"""

import os
import click
import asyncio
import logging
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse, StreamingResponse
from typing import Dict, Any, Optional
import sys

from mcp.server.lowlevel import Server
from mcp.server.sse import SseServerTransport

from .server import server, executor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AsyncStdinReader:
    """Async wrapper for stdin."""

    async def receive(self) -> bytes:
        line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
        return line.encode()


class AsyncStdoutWriter:
    """Async wrapper for stdout."""

    async def send(self, data: bytes) -> None:
        text = data.decode()
        sys.stdout.write(text)
        sys.stdout.flush()
        await asyncio.sleep(0)  # Yield control back to the event loop


@click.group()
def cli():
    """CLI MCP Server CLI."""
    pass


@cli.command()
@click.option("--port", default=8003, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
def start(
    port: int,
    transport: str,
) -> int:
    """Start the CLI MCP server."""
    
    logger.info(f"Starting CLI MCP server with {transport} transport")

    if transport == "stdio":
        # Run the server with stdio transport
        logger.info("Starting CLI MCP server with stdio transport")
        return asyncio.run(_run_stdio(server))

    else:
        return asyncio.run(_run_sse(port))


async def _run_sse(port: int) -> int:
    """Run the server using SSE transport."""
    try:
        # Set up Starlette app for SSE transport using standard MCP SSE transport
        sse = SseServerTransport("/messages/")

        async def handle_sse(request):
            """Handle SSE connections using mcp.server.sse."""
            logger.info(f"New SSE connection from {request.client}")
            try:
                async with sse.connect_sse(
                    request.scope, request.receive, request._send
                ) as streams:
                    # Run the MCP server with the streams
                    await server.run(
                        streams[0], streams[1], server.create_initialization_options()
                    )
            except Exception as e:
                logger.error(f"Error in handle_sse: {str(e)}")
                raise
            finally:
                logger.info(f"SSE connection from {request.client} closed")

        async def health_check(request):
            """Health check endpoint."""
            try:
                return JSONResponse({"status": "healthy", "allowed_dir": executor.allowed_dir})
            except Exception as e:
                return JSONResponse(
                    {"status": "error", "message": str(e)}, status_code=500
                )

        # Define startup and shutdown events
        async def startup_event():
            """Run on server startup."""
            logger.info("Starting server...")
            logger.info(f"Server started on port {port} with SSE endpoint at /sse")

        async def shutdown_event():
            """Run on server shutdown."""
            logger.info("Shutting down server...")
            logger.info("Server shut down")

        # Create Starlette app with routes
        from starlette.routing import Mount
        
        routes = [
            Route("/sse", endpoint=handle_sse, methods=["GET"]),
            Mount("/messages/", app=sse.handle_post_message),
            Route("/health", endpoint=health_check, methods=["GET"]),
        ]

        starlette_app = Starlette(
            routes=routes,
            on_startup=[startup_event],
            on_shutdown=[shutdown_event],
            debug=True,
        )

        # Run with uvicorn
        logger.info(f"Starting CLI MCP server with SSE transport on port {port}")
        config = uvicorn.Config(starlette_app, host="0.0.0.0", port=port)
        uvicorn_server = uvicorn.Server(config)
        await uvicorn_server.serve()

        return 0
    except Exception as e:
        logger.error(f"Error running SSE server: {e}")
        return 1


async def _run_stdio(app: Server) -> int:
    """Run the server using stdio transport."""
    try:
        stdin_reader = AsyncStdinReader()
        stdout_writer = AsyncStdoutWriter()

        # Create initialization options
        initialization_options = {}

        # Run the server
        await app.run(
            read_stream=stdin_reader,
            write_stream=stdout_writer,
            initialization_options=initialization_options,
        )
        return 0
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Error running server: {e}")
        return 1


if __name__ == "__main__":
    cli()