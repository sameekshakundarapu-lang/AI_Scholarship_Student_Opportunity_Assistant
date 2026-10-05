import streamlit as st
import pandas as pd
import ollama


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Scholarship & Student Opportunity Assistant",
    page_icon="🎓",
    layout="wide"
)


# ============================================================
# LOAD OPPORTUNITIES
# ============================================================

@st.cache_data
def load_opportunities():
    return pd.read_csv("data/opportunities.csv")


opportunities = load_opportunities()


# ============================================================
# SESSION STATE
# ============================================================

if "student" not in st.session_state:
    st.session_state.student = None

if "recommendations" not in st.session_state:
    st.session_state.recommendations = []

if "ai_explanations" not in st.session_state:
    st.session_state.ai_explanations = {}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def calculate_match_score(student, opportunity):

    score = 0

    # --------------------------------------------------------
    # CGPA - 20 points
    # --------------------------------------------------------

    if student["cgpa"] >= float(opportunity["min_cgpa"]):
        score += 20

    # --------------------------------------------------------
    # FAMILY INCOME - 20 points
    # --------------------------------------------------------

    if student["income"] <= float(opportunity["max_income"]):
        score += 20

    # --------------------------------------------------------
    # BRANCH - 20 points
    # --------------------------------------------------------

    eligible_branches = str(
        opportunity["branches"]
    ).split("|")

    if (
        "All" in eligible_branches
        or student["branch"] in eligible_branches
    ):
        score += 20

    # --------------------------------------------------------
    # YEAR - 15 points
    # --------------------------------------------------------

    eligible_years = str(
        opportunity["years"]
    ).split("|")

    if (
        "All" in eligible_years
        or student["year"] in eligible_years
    ):
        score += 15

    # --------------------------------------------------------
    # CATEGORY - 15 points
    # --------------------------------------------------------

    eligible_categories = str(
        opportunity["categories"]
    ).split("|")

    if (
        "All" in eligible_categories
        or student["category"] in eligible_categories
    ):
        score += 15

    # --------------------------------------------------------
    # STATE - 10 points
    # --------------------------------------------------------

    if (
        str(opportunity["state"]).strip() == "All"
        or str(opportunity["state"]).strip()
        == student["state"]
    ):
        score += 10

    return score


def get_match_label(score):

    if score >= 90:
        return "🟢 Excellent Match"

    elif score >= 75:
        return "🟢 Strong Match"

    elif score >= 60:
        return "🟡 Moderate Match"

    else:
        return "🔴 Low Match"


def get_opportunity_icon(opportunity_type):

    opportunity_type = str(
        opportunity_type
    ).strip().lower()

    if opportunity_type == "scholarship":
        return "🎓"

    elif opportunity_type == "internship":
        return "💼"

    elif opportunity_type in [
        "competition",
        "hackathon"
    ]:
        return "🏆"

    elif opportunity_type == "fellowship":
        return "🌟"

    return "📌"


def get_ai_explanation(student, opportunity):

    prompt = f"""
You are an AI Scholarship and Student Opportunity Assistant.

Student Profile:
Education: {student['education']}
Branch: {student['branch']}
Year: {student['year']}
CGPA: {student['cgpa']}
Family Income: ₹{student['income']}
Category: {student['category']}
State: {student['state']}
Skills: {student['skills']}
Interests: {student['interests']}
Opportunity Preference: {student['opportunity_preference']}

Opportunity:
Name: {opportunity['name']}
Type: {opportunity['type']}
Provider: {opportunity['provider']}
Description: {opportunity['description']}
Requirements: {opportunity['requirements']}
Minimum CGPA: {opportunity['min_cgpa']}

Explain in exactly 2 short and simple sentences why this
opportunity may be suitable for the student.

Use ONLY the information provided above.
Do not invent eligibility requirements.
Do not claim that the student is definitely eligible.
"""

    try:

        response = ollama.chat(
            model="llama3.2",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["message"]["content"]

    except Exception:

        return (
            "AI explanation could not be generated. "
            "Please make sure Ollama is running and "
            "the llama3.2 model is available."
        )


# ============================================================
# PAGE 1 — STUDENT PROFILE
# ============================================================

# ============================================================
# PAGE 1 — STUDENT PROFILE
# ============================================================

def profile_page():

    st.title(
        "🎓 AI Scholarship & Student Opportunity Assistant"
    )

    st.write(
        "Find scholarships, internships, hackathons, "
        "competitions, fellowships and other opportunities "
        "personalized to your profile."
    )

    st.divider()


    # --------------------------------------------------------
    # GET SAVED PROFILE VALUES
    # --------------------------------------------------------

    saved_student = st.session_state.get("student")

    if saved_student:

        default_name = saved_student.get(
            "name",
            ""
        )

        default_education = saved_student.get(
            "education",
            "B.Tech"
        )

        default_branch = saved_student.get(
            "branch",
            ""
        )

        default_year = saved_student.get(
            "year",
            "1st Year"
        )

        default_cgpa = float(
            saved_student.get(
                "cgpa",
                0.0
            )
        )

        default_income = int(
            saved_student.get(
                "income",
                0
            )
        )

        default_category = saved_student.get(
            "category",
            "General"
        )

        default_state = saved_student.get(
            "state",
            "Telangana"
        )

        default_preference = saved_student.get(
            "opportunity_preference",
            "Any Opportunity"
        )

        default_skills = saved_student.get(
            "skills",
            ""
        )

        default_interests = saved_student.get(
            "interests",
            ""
        )

    else:

        default_name = ""

        default_education = "B.Tech"

        default_branch = ""

        default_year = "1st Year"

        default_cgpa = 0.0

        default_income = 0

        default_category = "General"

        default_state = "Telangana"

        default_preference = "Any Opportunity"

        default_skills = ""

        default_interests = ""


    # --------------------------------------------------------
    # PROFILE
    # --------------------------------------------------------

    st.header("👩‍🎓 Student Profile")

    col1, col2 = st.columns(2)

    with col1:

        name = st.text_input(
            "Full Name",
            value=default_name,
            placeholder="Enter your name"
        )

        education_options = [
            "B.Tech",
            "B.E",
            "B.Sc",
            "BCA",
            "M.Tech",
            "MCA",
            "Other"
        ]

        education = st.selectbox(
            "Education Level",
            education_options,
            index=(
                education_options.index(
                    default_education
                )
                if default_education in education_options
                else 0
            )
        )

        branch = st.text_input(
            "Branch / Specialization",
            value=default_branch,
            placeholder="Example: Data Science"
        )

        year_options = [
            "1st Year",
            "2nd Year",
            "3rd Year",
            "4th Year",
            "Postgraduate"
        ]

        year = st.selectbox(
            "Year of Study",
            year_options,
            index=(
                year_options.index(
                    default_year
                )
                if default_year in year_options
                else 0
            )
        )

    with col2:

        cgpa = st.number_input(
            "CGPA",
            min_value=0.0,
            max_value=10.0,
            value=default_cgpa,
            step=0.1
        )

        income = st.number_input(
            "Annual Family Income (₹)",
            min_value=0,
            value=default_income,
            step=10000
        )

        category_options = [
            "General",
            "OBC",
            "SC",
            "ST",
            "EWS",
            "Other"
        ]

        category = st.selectbox(
            "Category",
            category_options,
            index=(
                category_options.index(
                    default_category
                )
                if default_category in category_options
                else 0
            )
        )

        state_options = [
            "Andhra Pradesh",
            "Telangana",
            "Karnataka",
            "Tamil Nadu",
            "Kerala",
            "Maharashtra",
            "Delhi",
            "Other"
        ]

        state = st.selectbox(
            "State",
            state_options,
            index=(
                state_options.index(
                    default_state
                )
                if default_state in state_options
                else 0
            )
        )


    st.divider()


    # --------------------------------------------------------
    # OPPORTUNITY PREFERENCE
    # --------------------------------------------------------

    st.header("🎯 Opportunity Preference")

    preference_options = [
        "Any Opportunity",
        "Scholarship",
        "Internship",
        "Hackathon / Competition",
        "Fellowship"
    ]

    opportunity_preference = st.selectbox(
        "What type of opportunity are you looking for?",
        preference_options,
        index=(
            preference_options.index(
                default_preference
            )
            if default_preference in preference_options
            else 0
        )
    )


    # --------------------------------------------------------
    # SKILLS AND INTERESTS
    # --------------------------------------------------------

    st.header("💡 Skills & Interests")

    col1, col2 = st.columns(2)

    with col1:

        skills = st.text_input(
            "Skills",
            value=default_skills,
            placeholder="Example: Python, SQL, Machine Learning"
        )

    with col2:

        interests = st.text_input(
            "Areas of Interest",
            value=default_interests,
            placeholder="Example: AI, Data Science, Web Development"
        )


    st.divider()


    # --------------------------------------------------------
    # FIND OPPORTUNITIES BUTTON
    # --------------------------------------------------------

    st.markdown("""
    <style>
    div.stButton > button[kind="primary"] {
        background-color: #7C3AED;
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
    }

    div.stButton > button[kind="primary"]:hover {
        background-color: #6D28D9;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)


    if st.button(
        "🤖 Find My Personalized Opportunities",
        use_container_width=True,
        type="primary"
    ):

        # Basic validation

        if not name.strip():

            st.warning(
                "Please enter your name."
            )

            return

        if not branch.strip():

            st.warning(
                "Please enter your branch / specialization."
            )

            return

        if cgpa <= 0:

            st.warning(
                "Please enter your CGPA."
            )

            return


        # ----------------------------------------------------
        # CREATE STUDENT PROFILE
        # ----------------------------------------------------

        student = {

            "name": name,

            "education": education,

            "branch": branch.strip(),

            "year": year,

            "cgpa": cgpa,

            "income": income,

            "category": category,

            "state": state,

            "skills": skills,

            "interests": interests,

            "opportunity_preference":
                opportunity_preference
        }


        recommendations = []


        # ----------------------------------------------------
        # FILTER AND SCORE OPPORTUNITIES
        # ----------------------------------------------------

        for _, opportunity in opportunities.iterrows():

            opportunity_type = str(
                opportunity["type"]
            ).strip().lower()


            # Any Opportunity

            if opportunity_preference == "Any Opportunity":

                pass


            # Hackathon / Competition

            elif opportunity_preference == "Hackathon / Competition":

                if opportunity_type not in [
                    "competition",
                    "hackathon"
                ]:

                    continue


            # Other types

            elif opportunity_type != (
                opportunity_preference.lower()
            ):

                continue


            # Calculate match score

            score = calculate_match_score(
                student,
                opportunity
            )


            recommendations.append(
                {
                    "opportunity": opportunity,
                    "score": score
                }
            )


        # ----------------------------------------------------
        # SORT BY SCORE
        # ----------------------------------------------------

        recommendations.sort(
            key=lambda x: x["score"],
            reverse=True
        )


        # ----------------------------------------------------
        # SAVE TO SESSION
        # ----------------------------------------------------

        st.session_state.student = student

        st.session_state.recommendations = recommendations

        st.session_state.ai_explanations = {}


        # ----------------------------------------------------
        # NAVIGATE TO OPPORTUNITIES PAGE
        # ----------------------------------------------------

        st.switch_page(
            "pages/Opportunities.py"
        )


# ============================================================
# PAGE 2 — RECOMMENDATIONS
# ============================================================

def recommendations_page():

    st.title(
        "🌟 Personalized Recommendations"
    )

    # --------------------------------------------------------
    # CHECK PROFILE
    # --------------------------------------------------------

    if (
        st.session_state.student is None
        or not st.session_state.recommendations
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

        return

    student = st.session_state.student

    recommendations = (
        st.session_state.recommendations
    )

    # --------------------------------------------------------
    # PROFILE SUMMARY
    # --------------------------------------------------------

    st.success(
        f"Hello {student['name']}! "
        f"Here are opportunities personalized for you."
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

    # --------------------------------------------------------
    # NUMBER OF RESULTS
    # --------------------------------------------------------

    st.subheader(
        f"🔎 {len(recommendations)} Matching Opportunities"
    )

    # --------------------------------------------------------
    # DISPLAY TOP 4
    # --------------------------------------------------------

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

            # ------------------------------------------------
            # TITLE
            # ------------------------------------------------

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

            # ------------------------------------------------
            # MATCH SCORE
            # ------------------------------------------------

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

            # ------------------------------------------------
            # DESCRIPTION
            # ------------------------------------------------

            st.write(
                f"**Description:** "
                f"{opportunity['description']}"
            )

            # ------------------------------------------------
            # REQUIREMENTS
            # ------------------------------------------------

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

            # ------------------------------------------------
            # AI EXPLANATION
            # ------------------------------------------------

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

            # ------------------------------------------------
            # OPPORTUNITY DETAILS
            # ------------------------------------------------

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

            # ------------------------------------------------
            # LINK
            # ------------------------------------------------

            st.link_button(
                "🔗 View Opportunity",
                opportunity["link"]
            )

    st.divider()

    # --------------------------------------------------------
    # BACK BUTTON
    # --------------------------------------------------------

    if st.button(
        "⬅️ Edit Student Profile"
    ):

        st.switch_page(
            "Profile.py"
        )


# ============================================================
# PAGE ROUTING
# ============================================================

# The main app.py is the profile page.
profile_page()