from app.analytics.query_engine import run_analytical_query
from app.analytics.chart_engine import generate_charts, generate_charts_for_question
from app.ai.insight_engine import generate_dataset_insights
from app.rag.rag_query_engine import rag_query
from app.ingestion.csv_loader import get_current_df

# NEW — IMPORT THE BRAIN
from app.ai.copilot_brain import analyze_question
from app.analytics.chart_engine import generate_dynamic_chart


# =====================================
# AI DATA COPILOT
# =====================================

def run_copilot(question: str):

    df = get_current_df()

    if df is None:
        return {
            "status": "error",
            "message": "No dataset loaded."
        }

    # ================================
    # BRAIN ANALYSIS
    # ================================

    brain = analyze_question(question)

    intent = brain.get("intent")
    metric = brain.get("metric")
    group_by = brain.get("group_by")
    chart_type = brain.get("chart")

    response = {
        "question": question,
        "answer": None,
        "analysis": None,
        "charts": None,
        "insights": None,
        "suggestions": [
            "Show sales by region",
            "Which category has highest profit",
            "Show sales trend over time",
            "Show profit distribution"
        ]
    }

    try:

        # =================================
        # INSIGHT QUESTIONS
        # =================================

        if intent == "insight":

            insights = generate_dataset_insights(df)

            if insights:
                response["answer"] = "Here are key insights from the dataset."
                response["insights"] = insights

            return {
                "status": "success",
                "copilot_response": response
            }

        # =================================
        # TREND QUESTIONS
        # =================================

        if intent == "trend":

            charts = generate_charts_for_question(question)

            if charts:
                response["answer"] = "Here is the trend analysis."
                response["charts"] = charts

            return {
                "status": "success",
                "copilot_response": response
            }

        # =================================
        # ANALYTICAL QUESTIONS
        # =================================

        if intent in ["max", "min", "average", "sum"]:

            analytical = run_analytical_query(question)

            if analytical:

                response["answer"] = analytical.get("answer")
                response["analysis"] = analytical.get("analysis")

                # Try intelligent chart first
                dynamic_chart = generate_dynamic_chart(question)

                if dynamic_chart:
                    response["charts"] = [dynamic_chart]

                else:

                    charts = generate_charts_for_question(question)

                    if charts:
                        response["charts"] = charts

            return {
                "status": "success",
                "copilot_response": response
            }

        # =================================
        # CHART REQUESTS
        # =================================

        if intent == "chart":

            # Try intelligent dynamic chart
            dynamic_chart = generate_dynamic_chart(question)

            if dynamic_chart:

                response["answer"] = "Here is the requested visualization."
                response["analysis"] = (
                    "This visualization highlights the relationship between the selected variables. "
                    "It helps identify patterns, trends, and potential insights within the dataset."
                )
                response["charts"] = [dynamic_chart]

            else:

                charts = generate_charts_for_question(question)

                if charts:

                    response["answer"] = "Here is the requested visualization."
                    response["analysis"] = (
                        "This chart summarizes the key relationship between the requested variables "
                        "based on the available dataset."
                    )
                    response["charts"] = charts

                else:

                    fallback = generate_charts()

                    if fallback:
                        response["answer"] = "Showing available dataset visualizations."
                        response["analysis"] = (
                            "No exact match was found for the request, so SentinelAI generated "
                            "some useful visualizations from the dataset to help explore patterns."
                        )
                        response["charts"] = fallback[:2]

            return {
                "status": "success",
                "copilot_response": response
            }
        # =================================
        # RAG QUESTIONS
        # =================================

        rag_result = rag_query(question)

        if rag_result and rag_result.get("answer"):
            response["answer"] = rag_result["answer"]

        return {
            "status": "success",
            "copilot_response": response
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }