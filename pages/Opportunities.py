import streamlit as st
import pandas as pd
import ollama


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Personalized Recommendations",
    page_icon="🌟",
    layout="wide"
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_opportunities():

    return pd.read_csv(
        "data/opportunities.csv"
    )


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_match_label(score):

    if score >= 90:
        return "🟢 Excellent Match"

    elif score >= 75:
        return "🟢 Strong Match"

    elif score >= 60:
        return "🟡 Moderate Match"

    return "🔴 Low Match"


def get_opportunity_icon(opportunity_type):

    opportunity_type = str(
        opportunity_type
    ).strip().lower()

    if opportunity_type == "scholarship":
        return "🎓"

    if opportunity_type == "internship":
        return "💼"

    if opportunity_type in [
        "competition",
        "hackathon"
    ]:
        return "🏆"

    if opportunity_type == "fellowship":
        return "🌟"

    return "📌"


def get_ai_explanation(student, opportunity):

    prompt = f"""
Explain in 1 short sentence why this opportunity matches this student.

Student:
Branch: {student['branch']}
Year: {student['year']}
CGPA: {student['cgpa']}
Skills: {student['skills']}
Interests: {student['interests']}

Opportunity:
Name: {opportunity['name']}
Type: {opportunity['type']}
Requirements: {opportunity['requirements']}

Use only the information given. Do not invent eligibility.
"""

    try:

        response = ollama.chat(
            model="llama3.2",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "num_predict": 50,
                "temperature": 0.2
            }
        )

        return response["message"]["content"]

    except Exception:

        return (
            "AI explanation could not be generated."
        )


# ============================================================
# CHECK SESSION DATA
# ============================================================

if (
    "student" not in st.session_state
    or st.session_state.student is None
):

    st.warning(
        "Please complete your student profile first."
    )

    if st.button(
        "👩‍🎓 Go to Student Profile"
    ):

        st.switch_page(
            "Profile.py"
        )

    st.stop()


student = st.session_state.student

recommendations = st.session_state.get(
    "recommendations",
    []
)


# ============================================================
# NO RESULTS
# ============================================================

if not recommendations:

    st.info(
        "No matching opportunities were found."
    )

    if st.button(
        "⬅️ Edit Student Profile"
    ):

        st.switch_page(
            "Profile.py"
        )

    st.stop()


# ============================================================
# PROFILE SUMMARY
# ============================================================

st.success(
    f"Hello {student['name']}! "
    "Here are your personalized opportunities."
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Education",
        student["education"]
    )

with col2:

    st.metric(
        "Year",
        student["year"]
    )

with col3:

    st.metric(
        "CGPA",
        student["cgpa"]
    )

with col4:

    st.metric(
        "Looking For",
        student["opportunity_preference"]
    )


st.divider()


# ============================================================
# RESULTS
# ============================================================

st.header(
    "🔎 Recommended Opportunities"
)

st.write(
    f"Showing the top {min(4, len(recommendations))} "
    "opportunities based on your profile."
)


for index, item in enumerate(
    recommendations[:4]
):

    opportunity = item["opportunity"]

    score = item["score"]

    opportunity_name = str(
        opportunity["name"]
    )

    opportunity_type = str(
        opportunity["type"]
    )

    icon = get_opportunity_icon(
        opportunity_type
    )

    with st.container(
        border=True
    ):

        st.subheader(
            f"{icon} {opportunity_name}"
        )

        st.write(
            f"**Type:** {opportunity_type}"
        )

        st.write(
            f"**Provider:** "
            f"{opportunity['provider']}"
        )

        # ----------------------------------------------------
        # SCORE
        # ----------------------------------------------------

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Match Score",
                f"{score}%"
            )

        with col2:

            st.write(
                "**Match Level**"
            )

            st.write(
                get_match_label(score)
            )

        # ----------------------------------------------------
        # DESCRIPTION
        # ----------------------------------------------------

        st.write(
            f"**Description:** "
            f"{opportunity['description']}"
        )

        # ----------------------------------------------------
        # REQUIREMENTS
        # ----------------------------------------------------

        st.markdown(
            "### 📋 Requirements"
        )

        requirements = str(
            opportunity["requirements"]
        )

        for requirement in requirements.split(";"):

            requirement = requirement.strip()

            if requirement:

                st.write(
                    f"• {requirement}"
                )

        # ----------------------------------------------------
        # AI EXPLANATION
        # ----------------------------------------------------

        st.markdown(
            "### 🤖 AI Explanation"
        )

        if opportunity_name in (
            st.session_state.ai_explanations
        ):

            st.info(
                st.session_state.ai_explanations[
                    opportunity_name
                ]
            )

        else:

            if st.button(
                "🤖 Get AI Explanation",
                key=f"ai_button_{index}"
            ):

                with st.spinner(
                    "AI is analyzing this opportunity..."
                ):

                    explanation = (
                        get_ai_explanation(
                            student,
                            opportunity
                        )
                    )

                st.session_state.ai_explanations[
                    opportunity_name
                ] = explanation

                st.rerun()

        # ----------------------------------------------------
        # DETAILS
        # ----------------------------------------------------

        col1, col2, col3 = st.columns(3)

        with col1:

            st.write(
                f"**Minimum CGPA:** "
                f"{opportunity['min_cgpa']}"
            )

        with col2:

            st.write(
                f"**Amount / Prize:** "
                f"₹{opportunity['amount']:,}"
            )

        with col3:

            st.write(
                f"**Deadline:** "
                f"{opportunity['deadline']}"
            )

        # ----------------------------------------------------
        # LINK
        # ----------------------------------------------------

        st.link_button(
            "🔗 View Opportunity",
            opportunity["link"]
        )


# ============================================================
# BACK BUTTON
# ============================================================

st.divider()

if st.button(
    "⬅️ Edit Student Profile"
):
 
    st.switch_page(
        "Profile.py"
    )