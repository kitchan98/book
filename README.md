# Book Search MCP Server

A Model Context Protocol (MCP) server that provides book search capabilities to Large Language Models (LLMs) like Claude. The server allows LLMs to search through a library of books and retrieve content to answer questions based on actual book content.

## Features

- **MCP Server**: Implements the Model Context Protocol for LLM tool access
- **Book Search**: Search through book titles and content
- **Content Retrieval**: Fetch complete book content for analysis
- **Web Interface**: Flask-based web UI for interactive chat
- **Real Responses**: Generates answers based on actual book content (no mock responses)

## Project Structure

```
book/
├── server.py          # MCP server implementation with book search tools
├── books.json         # Book database with 4 complete books
├── mcp_client.py      # MCP client with BookAdvisor for response generation  
├── app.py             # Flask web application
├── templates/
│   └── index.html     # Web UI for the chatbot
├── requirements.txt   # Python dependencies
├── run.sh            # Startup script for the web application
└── README.md         # This file
```

## Book Library

The system includes 4 books with full content:
1. **Steve Jobs by Walter Isaacson** - Biography of Apple's co-founder
2. **The Innovators by Walter Isaacson** - History of the digital revolution
3. **Thinking, Fast and Slow by Daniel Kahneman** - Psychology of decision-making
4. **Sapiens by Yuval Noah Harari** - History of humankind

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd book
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Web Application

The easiest way to use the system is through the web interface:

```bash
./run.sh
```

Then open http://localhost:5000 in your browser.

### Running the MCP Server Standalone

```bash
mcp dev server.py
```

### Example Queries

- "When was Steve Jobs born?"
- "What would Steve Jobs do about launching a new product?"
- "Tell me about the cognitive revolution from Sapiens"
- "Explain System 1 and System 2 thinking"

## How It Works

1. **User Query**: User asks a question through the web interface
2. **LLM Processing**: The LLM (Claude/GPT-4) interprets the natural language query
3. **Tool Discovery**: LLM discovers available tools (`search_books` and `list_all_books`)
4. **Intelligent Query Formation**: LLM decides what to search for based on the question
5. **Search Execution**: Server performs simple substring matching (case-insensitive)
6. **Result Analysis**: LLM receives results with snippets showing where matches were found
7. **Query Refinement**: If no results, LLM reformulates the search query
8. **Content Retrieval**: LLM uses book URIs to fetch full content via resources
9. **Response Generation**: LLM reads the book content and generates a contextual response

## Design Philosophy

Following MCP's first principles:
- **LLMs are intelligent**: The LLM decides what to search for, not the tool
- **Tools are simple**: Search does exact substring matching, no "smart" keyword extraction
- **Clear tool descriptions**: Tools explain exactly what they do so LLMs can use them effectively
- **Resources provide data**: Books are resources that can be accessed by URI
- **Iterative refinement**: LLMs learn from failed searches and try different queries

## Technical Details

### MCP Server (server.py)

The server provides two main capabilities:
- `search_books(query)`: Searches for books containing the query in title or content
- `get_book(book_id)`: Retrieves complete book data by ID

### MCP Client (mcp_client.py)

The client demonstrates proper MCP usage:
- No keyword extraction or preprocessing
- Lets the LLM decide what to search for
- Relies on LLM's natural language understanding
- Generates responses from actual book content

### Key Features

- **Full-text search**: Searches both titles and content
- **No mock responses**: All answers come from real book data
- **LLM-driven search**: The LLM decides search terms, not keyword extraction
- **Context-aware responses**: Answers are based on actual book passages

## API Reference

### Tools

#### `search_books`
- **Description:** Search for books by looking for an exact match of your query in the book title or content
- **Parameters:**
  - `query` (string): The exact text to search for (case-insensitive substring matching)
- **Returns:** JSON object with:
  - `found`: Number of books found
  - `results`: Array of objects containing:
    - `uri`: Book resource URI
    - `title`: Book title
    - `snippet`: Text snippet showing where the match was found

#### `list_all_books`
- **Description:** List all available books in the library
- **Parameters:** None
- **Returns:** Array of all books with title and description

### Resources

#### `book://{book_id}`
- **Description:** Retrieves a specific book by its ID
- **Returns:** JSON object with book data (`id`, `title`, `content`)

## Claude Desktop Integration

To use with Claude Desktop, you have two options:

### Option 1: Node.js Server (Recommended)

First install dependencies:
```bash
cd /Users/chankit/book
npm install
```

Then add to your Claude Desktop MCP settings:
```json
{
  "mcpServers": {
    "book-search": {
      "command": "node",
      "args": ["/Users/chankit/book/server.js"]
    }
  }
}
```

**Important**: After updating the configuration, restart Claude Desktop to ensure it uses the new server.

### Option 2: Python Server

Add to your Claude Desktop MCP settings:
```json
{
  "mcpServers": {
    "book-search": {
      "command": "mcp",
      "args": ["dev", "/Users/chankit/book/server.py"]
    }
  }
}
```

## Troubleshooting

If you encounter module import errors:
```bash
pip install --upgrade mcp
```

For "python not found" errors on macOS:
```bash
alias python=python3
```

## Usage Guide for LLMs

When using this MCP server, LLMs should:

1. **Start with `list_all_books`** if unsure what's available
2. **Use specific search terms** that are likely to appear in the content
3. **Try multiple searches** if the first doesn't return results:
   - Instead of "Steve Jobs birth date born", try:
     - "February 24, 1955" (the actual date)
     - "born" (simpler term)
     - "Steve Jobs was born" (exact phrase)
4. **Read the snippets** to understand context before fetching full content
5. **Access resources directly** using the URIs returned by search

## Recent Updates

- Redesigned based on MCP first principles
- Added `list_all_books` tool for discovery
- Enhanced search results with snippets
- Improved tool descriptions for better LLM understanding
- Fixed search functionality to search book content, not just titles
- Removed all mock/predefined responses  
- Cleaned up redundant files