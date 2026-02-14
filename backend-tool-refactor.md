Refactor @backend/ai_generator.py To support sequential tool calling where Claude can make up to two tool calls in separate API rounds. 

Current behavior:
- Claude makes one tool call -> Tools are removed from API parameters -> Final response. 
- If Claude wants another tool call after seeing results, it can't and gets an empty response. 

desired behavior:
- each tool call should be a separate API request where Claude can reason about previous results.
- Support for complex queries, acquiring multiple searches for comparisons, multi-part questions or when information from different courses and lessons is needed.

Example flow:
1. User- Search for a course that discusses the same topic as lesson 4 of Course X. 
2. Claude- Get course outline for Course X. Gets title of lesson 4. 
3. Claude- uses the title to search for a course that discusses the same topic, then returns the course information. 
4. Claude- provides the complete answer. 

Requirements :
1. Maximum two sequential rounds per user query 
2. Terminate when 
    A. Two rounds completed 
    B. Claude's response has no tool use blocks 
    C. Tool call fails 
3. Preserve conversation context between rounds 
4. Handle tool execution errors gracefully

Notes:
1. update the system prompt in @backend/ai_generator.py
2. update the test at @backend/tests/test_ai_generator.py 
3. write tests that verify the external behavior (API calls made, tools executed, results returned) rather than internal state details.

Use two parallel subagents to brainstorm possible paths. Do not implement any code.