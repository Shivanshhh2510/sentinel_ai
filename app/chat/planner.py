# app/chat/planner.py

def plan_query(question: str, intent: dict, columns: list):
    """
    Returns:
        {
            "action": "proceed" | "clarify" | "reject",
            "message": optional str
        }
    """

    q = question.lower()

    metric = intent.get("metric")
    group_by = intent.get("group_by")

    # ---------------------------------------
    # 1. Detect vague business phrases
    # ---------------------------------------

    vague_phrases = [
        "best customer",
        "top customer",
        "best performer",
        "who is best",
        "who is winning"
    ]

    for phrase in vague_phrases:
        if phrase in q:
            return {
                "action": "clarify",
                "message": (
                    "Your dataset does not explicitly define 'customer'.\n"
                    "Try asking about:\n"
                    "• top region by revenue\n"
                    "• highest revenue product category\n"
                    "• region with maximum sales"
                )
            }

    # ---------------------------------------
    # 2. Validate metric exists
    # ---------------------------------------

    if metric and metric not in columns:
        return {
            "action": "reject",
            "message": f"Column '{metric}' does not exist in dataset."
        }

    # ---------------------------------------
    # 3. Validate group_by exists
    # ---------------------------------------

    if group_by and group_by not in columns:
        return {
            "action": "reject",
            "message": f"Column '{group_by}' does not exist in dataset."
        }

    # ---------------------------------------
    # Default → proceed
    # ---------------------------------------

    return {"action": "proceed"}