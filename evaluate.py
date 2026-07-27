from agents.router import get_chunks
from test_set import TEST_CASES

def decide_route(top_score):
    if top_score < 0.72:
        return "tool_agent"
    return "sub_agent"

def run_evaluation():
    correct_routes = 0
    correct_relevance = 0
    total_relevance_checks = 0

    for case in TEST_CASES:
        chunks = get_chunks(case["question"])

        if chunks:
            top_score = chunks[0]["similarity"]
        else:
            top_score = 0

        print("  (actual score:", top_score, ")")

        actual_route = decide_route(top_score)
        expected_route = case["expected_route"]

        print("Question:", case["question"])
        print("Expected route:", expected_route)
        print("Actual route:", actual_route)

        if actual_route == expected_route:
            correct_routes += 1
            print("Routing: CORRECT")
        else:
            print("Routing: WRONG")

        if expected_route == "sub_agent" and actual_route == "sub_agent":
            total_relevance_checks += 1
            top_text = chunks[0]["chunk_text"].lower()
            found = False
            for word in case["expected_keywords"]:
                if word.lower() in top_text:
                    found = True
            if found:
                correct_relevance += 1
                print("Relevance: FOUND")
            else:
                print("Relevance: NOT FOUND")

        print("---")

    print("")
    print("Routing accuracy:", correct_routes, "/", len(TEST_CASES))
    print("Relevance accuracy:", correct_relevance, "/", total_relevance_checks)

run_evaluation()