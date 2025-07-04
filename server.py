import json
from mcp.server.fastmcp import FastMCP

# Create an MCP server instance
mcp = FastMCP("BookSearchServer")

# Load book data from the JSON file
with open("books.json", "r") as f:
    books_data = json.load(f)

# Define a resource for a book
@mcp.resource("book://{book_id}")
def get_book(book_id: str) -> str:
    """Retrieves a book by its ID."""
    for book in books_data:
        if book["id"] == book_id:
            return json.dumps(book)
    return "{}"

# Define a tool that the LLM can use to search for books
@mcp.tool()
def search_books(query: str) -> str:
    """Searches the book library for a specific query in titles and content."""
    results = []
    query_lower = query.lower()
    for book in books_data:
        # Search in both title and content
        if query_lower in book["title"].lower() or query_lower in book["content"].lower():
            # Construct the URI for the book resource
            results.append(f"book://{book['id']}")
    return json.dumps(results)

if __name__ == "__main__":
    mcp.run()
