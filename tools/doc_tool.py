# Wraps your existing document search (agents/router.py's get_chunks) as
# a tool the orchestrator can choose to call — same status as the ERP
# functions. This is the change that removes the hardcoded score check:
# instead of router.py deciding automatically, the orchestrator now
# decides whether document search is even worth calling.

from agents.router import get_chunks


def search_docs(query, count=5,document_filter=None):
    try:
        chunks = get_chunks(query, chunk_count=count,document_filter=document_filter)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"found": False, "message": f"Document search failed: {e}"}

    if not chunks:
        return {"found": False, "message": "No matching content found in the documents."}

    return {"found": True, "chunks": chunks}



