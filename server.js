#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListResourcesRequestSchema,
  ListToolsRequestSchema,
  ReadResourceRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { readFile } from 'fs/promises';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

// Get current directory
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load book data
let booksData = [];
const booksPath = join(__dirname, 'books.json');

async function loadBooks() {
  try {
    const data = await readFile(booksPath, 'utf-8');
    booksData = JSON.parse(data);
    console.error(`Loaded ${booksData.length} books`);
  } catch (error) {
    console.error('Error loading books:', error);
  }
}

// Create server
const server = new Server(
  {
    name: 'book-search',
    version: '1.0.0',
  },
  {
    capabilities: {
      resources: {},
      tools: {},
    },
  }
);

// Handle resource listing
server.setRequestHandler(ListResourcesRequestSchema, async () => {
  return {
    resources: booksData.map(book => ({
      uri: `book://${book.id}`,
      name: book.title,
      description: `Book: ${book.title}`,
      mimeType: 'application/json',
    })),
  };
});

// Handle resource reading
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const uri = request.params.uri;
  const match = uri.match(/^book:\/\/(.+)$/);
  
  if (!match) {
    throw new Error('Invalid book URI');
  }
  
  const bookId = match[1];
  const book = booksData.find(b => b.id === bookId);
  
  if (!book) {
    throw new Error('Book not found');
  }
  
  return {
    contents: [
      {
        uri,
        mimeType: 'application/json',
        text: JSON.stringify(book, null, 2),
      },
    ],
  };
});

// Handle tool listing
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'search_books',
        description: 'Search for books by looking for an exact match of your query in the book title or content. The search is case-insensitive substring matching.',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'The exact text to search for in book titles and content',
            },
          },
          required: ['query'],
        },
      },
      {
        name: 'list_all_books',
        description: 'List all available books in the library',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === 'search_books') {
    const query = request.params.arguments?.query?.toLowerCase() || '';
    
    // Simple substring search - let the LLM be intelligent about queries
    const results = booksData.filter(book => 
      book.title.toLowerCase().includes(query) || 
      book.content.toLowerCase().includes(query)
    );
    
    // Return both the URIs and a hint about what was found
    const response = {
      found: results.length,
      results: results.map(book => ({
        uri: `book://${book.id}`,
        title: book.title,
        snippet: extractSnippet(book.content, query)
      }))
    };
    
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(response, null, 2),
        },
      ],
    };
  }
  
  if (request.params.name === 'list_all_books') {
    const books = booksData.map(book => ({
      uri: `book://${book.id}`,
      title: book.title,
      description: book.content.substring(0, 100) + '...'
    }));
    
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(books, null, 2),
        },
      ],
    };
  }
  
  throw new Error(`Unknown tool: ${request.params.name}`);
});

// Helper function to extract a snippet around the search term
function extractSnippet(content, query) {
  const lowerContent = content.toLowerCase();
  const index = lowerContent.indexOf(query);
  
  if (index === -1) return '';
  
  const start = Math.max(0, index - 50);
  const end = Math.min(content.length, index + query.length + 50);
  
  return '...' + content.substring(start, end) + '...';
}

// Start server
async function main() {
  await loadBooks();
  
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Book search MCP server running');
}

main().catch(console.error);