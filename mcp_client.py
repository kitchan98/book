#!/usr/bin/env python3
"""
MCP Client Implementation - Proper LLM Integration Approach

This implementation shows how MCP should work:
1. The LLM has access to MCP tools
2. The LLM decides what to search for using its language understanding
3. No keyword extraction or pattern matching needed
"""

import json
import subprocess
import asyncio
from typing import List, Dict, Optional
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPBookClient:
    """Client for interacting with the MCP Book Search Server."""
    
    def __init__(self):
        self.process = None
        self.request_id = 0
        
    async def start(self):
        """Start the MCP server process."""
        logger.info("Starting MCP server...")
        self.process = await asyncio.create_subprocess_exec(
            'python', 'server.py',
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Initialize the connection
        await self._initialize()
        logger.info("MCP server initialized successfully")
        
    async def stop(self):
        """Stop the MCP server process."""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            logger.info("MCP server stopped")
    
    async def _send_request(self, method: str, params: Dict = None) -> Dict:
        """Send a JSON-RPC request to the server."""
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {}
        }
        
        # Send request
        request_str = json.dumps(request) + '\n'
        self.process.stdin.write(request_str.encode())
        await self.process.stdin.drain()
        
        # Read response
        response_data = await self.process.stdout.readline()
        response = json.loads(response_data.decode())
        
        if "error" in response:
            raise Exception(f"MCP Error: {response['error']}")
            
        return response.get("result", {})
    
    async def _send_notification(self, method: str, params: Dict = None):
        """Send a JSON-RPC notification (no response expected)."""
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        }
        notification_str = json.dumps(notification) + '\n'
        self.process.stdin.write(notification_str.encode())
        await self.process.stdin.drain()
    
    async def _initialize(self):
        """Initialize the MCP connection."""
        # Send initialize request
        await self._send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "book-advisor-client",
                "version": "1.0.0"
            }
        })
        
        # Send initialized notification
        await self._send_notification("notifications/initialized", {})
    
    async def list_tools(self) -> List[Dict]:
        """List available tools from the MCP server."""
        result = await self._send_request("tools/list", {})
        return result.get("tools", [])
    
    async def search_books(self, query: str) -> List[str]:
        """Search for books using the MCP server."""
        logger.info(f"Searching for books with query: {query}")
        
        result = await self._send_request("tools/call", {
            "name": "search_books",
            "arguments": {"query": query}
        })
        
        # Extract book URIs from the response
        if "content" in result and result["content"]:
            uris = json.loads(result["content"][0]["text"])
            logger.info(f"Found {len(uris)} books")
            return uris
        return []
    
    async def get_book_content(self, uri: str) -> Dict:
        """Fetch book content from the MCP server."""
        logger.info(f"Fetching book content for: {uri}")
        
        result = await self._send_request("resources/read", {
            "uri": uri
        })
        
        # Extract book data from the response
        if "contents" in result and result["contents"]:
            book_data = json.loads(result["contents"][0]["text"])
            return book_data
        return {}


class BookAdvisor:
    """
    Book advisor that demonstrates proper MCP usage.
    
    In a real implementation:
    1. This would be integrated with an LLM (Claude, GPT-4, etc.)
    2. The LLM would have direct access to MCP tools
    3. The LLM would decide what to search for based on understanding
    4. No keyword extraction or pattern matching would be needed
    """
    
    def __init__(self, mcp_client: MCPBookClient):
        self.client = mcp_client
        
    async def get_advice_with_llm(self, question: str, llm_client=None) -> str:
        """
        Get advice using an LLM with MCP tools.
        
        This is how it SHOULD work:
        1. Pass the question to the LLM
        2. Give the LLM access to MCP tools
        3. Let the LLM decide how to use the tools
        4. Get a natural response based on LLM's understanding
        """
        
        if llm_client is None:
            # Fallback to demonstration mode
            return await self._demonstrate_llm_flow(question)
        
        # In a real implementation with an LLM:
        tools = await self.client.list_tools()
        
        # The LLM would have access to:
        # - search_books(query): Search for relevant books
        # - get_book(uri): Retrieve book content
        
        # The LLM would:
        # 1. Understand the question
        # 2. Decide what searches would be helpful
        # 3. Call search_books with appropriate queries
        # 4. Read the book content
        # 5. Generate a response based on understanding
        
        # Example with Claude API (pseudo-code):
        """
        response = await llm_client.messages.create(
            messages=[{"role": "user", "content": question}],
            tools=tools,
            system="You have access to a book library. Use the tools to search for relevant content and provide helpful advice based on what you find."
        )
        """
        
        return "LLM integration would generate response here"
    
    async def _demonstrate_llm_flow(self, question: str) -> str:
        """Demonstrate how an LLM would use MCP tools."""
        
        response = f"""🤖 Demonstrating Proper MCP + LLM Flow:

**Your Question:** {question}

**What an LLM would do:**

1. **Understand the Question**
   The LLM analyzes your question using its language model, understanding:
   - The intent behind your question
   - Key concepts and entities mentioned
   - What type of information would be helpful

2. **Decide on Search Strategy**
   Based on its understanding, the LLM would choose to search for:
"""
        
        # Simulate LLM reasoning
        if "steve jobs" in question.lower():
            searches = ["Steve Jobs", "Apple history", "Jobs philosophy"]
            response += f"   - Books about Steve Jobs and his philosophy\n"
        elif "decision" in question.lower() or "think" in question.lower():
            searches = ["Kahneman", "decision making", "cognitive psychology"]
            response += f"   - Books about decision-making and cognitive psychology\n"
        elif "innovation" in question.lower():
            searches = ["innovation", "creative process", "breakthrough ideas"]
            response += f"   - Books about innovation and creative processes\n"
        else:
            searches = ["relevant topics based on semantic understanding"]
            response += f"   - Books relevant to the concepts in your question\n"
        
        response += f"""
3. **Execute Searches**
   The LLM would call search_books() with queries it chose based on understanding.
   NOT keyword extraction - semantic understanding!

4. **Analyze Book Content**
   The LLM would read the actual book content and understand:
   - Relevant passages that address your question
   - Context and nuance in the text
   - How different sources relate to your question

5. **Generate Natural Response**
   The LLM would synthesize insights from the books, providing:
   - Specific examples and quotes
   - Contextual understanding
   - Nuanced advice based on the content

**Key Difference:** The LLM understands language at every step.
No pattern matching, no keyword extraction - just natural language understanding!
"""
        
        # Show what tools are available
        tools = await self.client.list_tools()
        if tools:
            response += f"\n**Available MCP Tools:**\n"
            for tool in tools:
                response += f"- {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}\n"
        
        return response
    
    async def get_advice(self, question: str) -> str:
        """
        Fallback method for when LLM is not available.
        This shows what the system does WITHOUT proper LLM integration.
        """
        
        return f"""⚠️ Running without LLM Integration

This is a demonstration of what happens WITHOUT proper LLM integration.
To use MCP correctly, you need an LLM that can:

1. Understand your question: "{question}"
2. Decide what to search for using its language understanding
3. Call MCP tools based on semantic comprehension
4. Generate responses from actual understanding of book content

**To enable proper MCP usage:**
- Use Claude Desktop with MCP support
- Or integrate with OpenAI/Anthropic APIs
- Or use any LLM that supports tool calling

The whole point of MCP is to give LLMs access to external tools
while preserving their natural language understanding capabilities!

Without an LLM, we would have to fall back to keyword extraction,
which defeats the purpose of MCP.
"""


# For backward compatibility
class SyncBookAdvisor:
    """Synchronous wrapper for the BookAdvisor."""
    
    def __init__(self):
        self.client = MCPBookClient()
        self.advisor = BookAdvisor(self.client)
        self._loop = None
    
    def start(self):
        """Start the MCP client."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self.client.start())
    
    def stop(self):
        """Stop the MCP client."""
        if self._loop:
            self._loop.run_until_complete(self.client.stop())
            self._loop.close()
    
    def get_advice(self, question: str) -> str:
        """Get advice synchronously."""
        if not self._loop:
            raise RuntimeError("Client not started. Call start() first.")
        return self._loop.run_until_complete(self.advisor.get_advice(question))


# Example usage showing proper MCP philosophy
if __name__ == "__main__":
    async def demonstrate():
        client = MCPBookClient()
        advisor = BookAdvisor(client)
        
        try:
            await client.start()
            
            print("🎯 MCP Philosophy: LLMs + Tools")
            print("=" * 50)
            print("\nMCP enables LLMs to use external tools while maintaining")
            print("their natural language understanding capabilities.\n")
            
            # Test questions
            questions = [
                "What did Steve Jobs think about failure?",
                "How can I make better decisions?",
                "What drives innovation in technology?",
            ]
            
            for question in questions:
                print(f"\n{'='*60}")
                print(f"Question: {question}")
                print(f"{'='*60}")
                
                # Show how it should work with LLM
                response = await advisor.get_advice_with_llm(question)
                print(response)
                
                # Also show the fallback
                print("\n--- Without LLM Integration ---")
                fallback = await advisor.get_advice(question)
                print(fallback[:200] + "...")
                
        finally:
            await client.stop()
    
    asyncio.run(demonstrate())