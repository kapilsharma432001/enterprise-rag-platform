# The Math: Recipprocal Rank Fusion (RRF) algorithm is a method used to combine multiple ranked lists into a single ranked list.
# Here we will combine our list f vector search and then keyword search results.
# k is a constant that determines the weight of the ranks. A common choice for k is 60.

from typing import List, Dict

def reciprocal_rank_fusion(
        keyword_results: List[Dict],
        vector_search: List[Dict],
        k: int = 60
) -> List[Dict]:
    
    """
    RRF formula: score = sum(1 / (k + rank))
    where rank is the position of the document in each list (starting from 1).

    We caculate this score for every document in both lists and add them up.
    """

    scores = {}

    def add_to_scores(results: List[Dict]):
        
        for rank, doc in enumerate(results):
            doc_id = doc['id']
            if doc_id not in scores:
                scores[doc_id] = {
                    "doc": doc,
                    "score": 0.0
                }
            # The lower the rank (0 is best), the higher the score
            scores[doc_id]["score"] += 1 / (k + rank + 1)  # rank + 1 because rank starts from 0
        
        # Process both the lists
    add_to_scores(keyword_results)
    add_to_scores(vector_search)

    # Sort documents by their RRF score in descending order
    sorted_docs = sorted(scores.values(), key = lambda x: x["score"], reverse = True)

    # Return a list of documents with their scores
    return [item["doc"] for item in sorted_docs]
    