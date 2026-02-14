#!/usr/bin/env python3
"""
Test script for CourseOutlineTool functionality.
Tests the course outline tool in isolation to verify it works correctly.
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from vector_store import VectorStore
from search_tools import CourseOutlineTool, ToolManager
from config import config

def test_outline_tool():
    """Test the CourseOutlineTool with various scenarios"""

    print("=" * 80)
    print("COURSE OUTLINE TOOL TEST")
    print("=" * 80)

    # Initialize components
    print("\n1. Initializing VectorStore...")
    vector_store = VectorStore(
        config.CHROMA_PATH,
        config.EMBEDDING_MODEL,
        config.MAX_RESULTS
    )

    # Check available courses
    print("\n2. Checking available courses in catalog...")
    try:
        all_courses = vector_store.course_catalog.get()
        if all_courses and all_courses.get("ids"):
            course_ids = all_courses["ids"]
            print(f"   Found {len(course_ids)} courses:")
            for i, course_id in enumerate(course_ids, 1):
                print(f"   {i}. {course_id}")
        else:
            print("   ⚠️  No courses found in catalog!")
            return
    except Exception as e:
        print(f"   ❌ Error getting courses: {e}")
        return

    # Initialize the outline tool
    print("\n3. Initializing CourseOutlineTool...")
    outline_tool = CourseOutlineTool(vector_store)
    print("   ✓ Tool initialized")

    # Test 1: Get definition
    print("\n4. Testing tool definition...")
    tool_def = outline_tool.get_tool_definition()
    print(f"   Tool Name: {tool_def['name']}")
    print(f"   Description: {tool_def['description']}")
    print(f"   Required Parameters: {tool_def['input_schema']['required']}")

    # Test 2: Direct execution with first course
    print("\n5. Testing direct execution with first course...")
    first_course = course_ids[0]
    print(f"   Querying: '{first_course}'")
    result = outline_tool.execute(course_name=first_course)
    print("\n   Result:")
    print("   " + "\n   ".join(result.split("\n")))

    # Test 3: Partial match
    print("\n6. Testing partial course name match...")
    # Extract first word from course name for partial match
    partial_name = first_course.split()[0] if first_course else "Introduction"
    print(f"   Querying with partial name: '{partial_name}'")
    result = outline_tool.execute(course_name=partial_name)
    print("\n   Result:")
    print("   " + "\n   ".join(result.split("\n")))

    # Test 4: Tool Manager integration
    print("\n7. Testing ToolManager integration...")
    tool_manager = ToolManager()
    tool_manager.register_tool(outline_tool)
    print(f"   Registered tools: {[t['name'] for t in tool_manager.get_tool_definitions()]}")

    result = tool_manager.execute_tool(
        tool_name="get_course_outline",
        course_name=first_course
    )
    print(f"   Tool execution via manager: {'✓ Success' if result else '❌ Failed'}")

    # Test 5: Non-existent course
    print("\n8. Testing with non-existent course...")
    result = outline_tool.execute(course_name="NonExistentCourse12345")
    print(f"   Result: {result}")

    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_outline_tool()
