# API Test Queries for Course Outline Tool

Once you start the server, you can test the Course Outline Tool through these methods:

## Method 1: Web Interface (Recommended)

1. Start the server:
   ```bash
   cd backend && uv run uvicorn app:app --reload --port 8000
   ```

2. Open browser to: http://localhost:8000

3. Try these test queries in the chat:
   - "What are the lessons in the MCP course?"
   - "Show me the outline for Advanced Retrieval"
   - "List all lessons in the Computer Use course"
   - "What topics are covered in Prompt Compression?"

## Method 2: cURL (API Direct)

### Test Query 1: MCP Course Outline
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the lessons in the MCP course?",
    "session_id": "test-session-1"
  }'
```

### Test Query 2: Advanced Retrieval Course
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me the complete outline for Advanced Retrieval for AI with Chroma",
    "session_id": "test-session-2"
  }'
```

### Test Query 3: Computer Use Course
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the structure of the Building Towards Computer Use course?",
    "session_id": "test-session-3"
  }'
```

### Test Query 4: Partial Match
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What lessons are in the Prompt Compression course?",
    "session_id": "test-session-4"
  }'
```

## Expected Response Format

The AI should return a response that includes:
- Course title
- Course link (URL to deeplearning.ai)
- Total number of lessons
- Complete list of lessons with numbers and titles

**Example Expected Response:**
```
The MCP course has 11 lessons:

**Course:** MCP: Build Rich-Context AI Apps with Anthropic
**Link:** https://www.deeplearning.ai/short-courses/mcp-build-rich-context-ai-apps-with-anthropic/

**Lessons:**
Lesson 0: Introduction
Lesson 1: Why MCP
Lesson 2: MCP Architecture
Lesson 3: Chatbot Example
Lesson 4: Creating An MCP Server
Lesson 5: Creating An MCP Client
Lesson 6: Connecting The MCP Chatbot To Reference Servers
Lesson 7: Adding Prompt And Resource Features
Lesson 8: Configuring Servers For Claude Desktop
Lesson 9: Creating And Deploying Remote Servers
Lesson 10: Conclusion
```

## Debugging: Check Tool Usage

If you want to verify the AI is actually using the `get_course_outline` tool:

1. Check the backend logs for tool execution messages
2. Look for JSON with `"type": "tool_use"` in the response
3. The tool name should be `"get_course_outline"`

## Available Courses

The system currently has 4 courses loaded:
1. **Advanced Retrieval for AI with Chroma** (7 lessons)
2. **Prompt Compression and Query Optimization**
3. **Building Towards Computer Use with Anthropic** (9 lessons)
4. **MCP: Build Rich-Context AI Apps with Anthropic** (11 lessons)

You can query any of these courses using full or partial names.

## Comparing with Content Search

To verify the tool is correctly selected:

**Outline Query** (should use `get_course_outline` tool):
- "What lessons are in the MCP course?"
- "Show me the course structure"
- "List all topics in Advanced Retrieval"

**Content Query** (should use `search_course_content` tool):
- "How do embeddings work in retrieval?"
- "Explain cross-encoder re-ranking"
- "What is prompt caching used for?"

The AI should automatically select the appropriate tool based on the query type.
