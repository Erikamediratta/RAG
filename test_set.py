
TEST_CASES = [
    {
        "question": "What is retrieval-augmented generation?",
        "expected_route": "sub_agent",
        "expected_keywords": ["retrieve", "generate"],
    },
    {
        "question": "What is agent-based RAG?",
        "expected_route": "sub_agent",
        "expected_keywords": ["agent"],
    },
    {
        "question": "What is dense passage retrieval?",
        "expected_route": "sub_agent",
        "expected_keywords": ["dense", "passage", "retriev"],
    },
    {
        "question": "What are the main components of a RAG system?",
        "expected_route": "sub_agent",
        "expected_keywords": ["retrieve", "generate", "component"],
    },
    {
        "question": "What is the capital of France?",
        "expected_route": "tool_agent",
        "expected_keywords": [],
    },
    {
        "question": "What's 15 times 12?",
        "expected_route": "tool_agent",
        "expected_keywords": [],
    },
    {
        "question": "What is Model Context Protocol?",
        "expected_route": "tool_agent",
        "expected_keywords": [],
    },
    {
        "question": "Recommend a good pizza topping",
        "expected_route": "tool_agent",
        "expected_keywords": [],
    },
]