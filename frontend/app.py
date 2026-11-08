import streamlit as st
import requests


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Quiz Builder",
    page_icon="🧠",
    layout="wide"
)


API_URL = "http://127.0.0.1:8000"


# =========================================================
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "token" not in st.session_state:
    st.session_state.token = None

if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "signin"

if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None


# =========================================================
# SIGN UP PAGE
# =========================================================

def signup_page():

    st.title("🧠 AI Quiz Builder")

    st.subheader("Create Your Account")

    name = st.text_input(
        "Full Name",
        key="signup_name"
    )

    email = st.text_input(
        "Email",
        key="signup_email"
    )

    password = st.text_input(
        "Password",
        type="password",
        key="signup_password"
    )

    confirm_password = st.text_input(
        "Confirm Password",
        type="password",
        key="signup_confirm"
    )

    if st.button(
        "Create Account",
        use_container_width=True
    ):

        if not name or not email or not password:
            st.error("Please fill all fields.")
            return

        if password != confirm_password:
            st.error("Passwords do not match.")
            return

        try:

            response = requests.post(
                f"{API_URL}/signup",
                json={
                    "name": name,
                    "email": email,
                    "password": password
                },
                timeout=10
            )

            if response.status_code == 200:

                st.success(
                    "Account created successfully!"
                )

                # After signup, go to SIGN IN
                st.session_state.page = "signin"

                st.rerun()

            else:

                try:
                    message = response.json()["detail"]
                except Exception:
                    message = "Signup failed."

                st.error(message)

        except requests.exceptions.RequestException:

            st.error(
                "Cannot connect to backend. "
                "Make sure FastAPI is running."
            )

    st.write("")

    if st.button(
        "Already have an account? Sign In",
        use_container_width=True
    ):

        st.session_state.page = "signin"
        st.rerun()


# =========================================================
# SIGN IN PAGE
# =========================================================

def signin_page():

    st.title("🧠 AI Quiz Builder")

    st.subheader("Sign In")

    email = st.text_input(
        "Email",
        key="signin_email"
    )

    password = st.text_input(
        "Password",
        type="password",
        key="signin_password"
    )

    if st.button(
        "Sign In",
        use_container_width=True
    ):

        if not email or not password:

            st.error(
                "Please enter email and password."
            )

            return

        try:

            response = requests.post(
                f"{API_URL}/signin",
                json={
                    "email": email,
                    "password": password
                },
                timeout=10
            )

            if response.status_code == 200:

                data = response.json()

                # Save authentication information
                st.session_state.token = (
                    data["access_token"]
                )

                st.session_state.user = (
                    data["user"]
                )

                # User is now authenticated
                st.session_state.logged_in = True

                # Open Quiz Builder automatically
                st.session_state.page = "quiz"

                st.rerun()

            else:

                try:
                    message = response.json()["detail"]
                except Exception:
                    message = "Invalid email or password."

                st.error(message)

        except requests.exceptions.RequestException:

            st.error(
                "Cannot connect to backend. "
                "Make sure FastAPI is running."
            )

    st.write("")

    if st.button(
        "Don't have an account? Sign Up",
        use_container_width=True
    ):

        st.session_state.page = "signup"
        st.rerun()


# =========================================================
# QUIZ BUILDER MAIN PAGE
# =========================================================

def quiz_page():

    user = st.session_state.user

    # -----------------------------------------------------
    # SIDEBAR
    # -----------------------------------------------------

    with st.sidebar:

        st.write("### 👤 Account")

        st.write(
            f"Welcome, **{user['name']}**"
        )

        st.write(user["email"])

        st.divider()

        if st.button(
            "Logout",
            use_container_width=True
        ):

            st.session_state.logged_in = False
            st.session_state.token = None
            st.session_state.user = None
            st.session_state.page = "signin"
            st.session_state.quiz_data = None

            st.rerun()

    # -----------------------------------------------------
    # MAIN QUIZ BUILDER
    # -----------------------------------------------------

    st.title("🧠 AI Quiz Builder")

    st.success(
        f"Welcome {user['name']}!"
    )

    st.write(
        "Generate intelligent quizzes using AI."
    )

    st.divider()

    # =====================================================
    # CHOOSE MODE
    # =====================================================

    option = st.radio(
        "Choose Mode",
        [
            "Generate From Topic",
            "Generate From File"
        ]
    )

    # =====================================================
    # TOPIC MODE
    # =====================================================

    if option == "Generate From Topic":

        topic = st.text_input(
            "Enter Topic"
        )

        difficulty = st.selectbox(
            "Difficulty",
            [
                "Easy",
                "Medium",
                "Hard"
            ]
        )

        num_questions = st.slider(
            "Number of Questions",
            1,
            20,
            5
        )

        if st.button(
            "Generate Quiz"
        ):

            if not topic:

                st.warning(
                    "Please enter a topic."
                )

            else:

                payload = {
                    "topic": topic,
                    "difficulty": difficulty,
                    "num_questions": num_questions
                }

                try:

                    response = requests.post(
                        f"{API_URL}/generate-quiz",
                        json=payload,
                        timeout=120
                    )

                    if response.status_code == 200:

                        st.session_state.quiz_data = (
                            response.json()
                        )

                        st.rerun()

                    else:

                        st.error(
                            f"Backend Error: "
                            f"{response.status_code}"
                        )

                        st.code(
                            response.text
                        )

                except requests.exceptions.RequestException as e:

                    st.error(
                        f"Cannot connect to backend: {e}"
                    )

    # =====================================================
    # FILE MODE
    # =====================================================

    else:

        uploaded_file = st.file_uploader(
            "Upload PDF or TXT",
            type=["pdf", "txt"]
        )

        difficulty = st.selectbox(
            "Difficulty",
            [
                "Easy",
                "Medium",
                "Hard"
            ],
            key="file_difficulty"
        )

        num_questions = st.slider(
            "Number of Questions",
            1,
            20,
            5,
            key="file_questions"
        )

        if uploaded_file and st.button(
            "Generate Quiz From File"
        ):

            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue()
                )
            }

            try:

                response = requests.post(
                    f"{API_URL}/upload-quiz",
                    files=files,
                    data={
                        "difficulty": difficulty,
                        "num_questions": num_questions
                    },
                    timeout=120
                )

                if response.status_code == 200:

                    st.session_state.quiz_data = (
                        response.json()
                    )

                    st.rerun()

                else:

                    st.error(
                        f"Backend Error: "
                        f"{response.status_code}"
                    )

                    st.code(
                        response.text
                    )

            except requests.exceptions.RequestException as e:

                st.error(
                    f"Cannot connect to backend: {e}"
                )

    # =====================================================
    # SHOW QUIZ
    # =====================================================

    if (
        st.session_state.quiz_data
        and "quiz" in st.session_state.quiz_data
    ):

        data = st.session_state.quiz_data

        user_answers = []

        st.divider()

        st.header("Quiz")

        for i, q in enumerate(
            data["quiz"],
            start=1
        ):

            st.subheader(
                f"Question {i}"
            )

            selected = st.radio(
                q["question"],
                q["options"],
                index=None,
                key=f"question_{i}"
            )

            user_answers.append(
                (
                    selected,
                    q["answer"]
                )
            )

        if st.button(
            "Submit Quiz"
        ):

            score = 0

            st.divider()

            st.header("Results")

            for i, (
                selected,
                correct
            ) in enumerate(
                user_answers,
                start=1
            ):

                if selected == correct:

                    score += 1

                    st.success(
                        f"Question {i}: Correct"
                    )

                else:

                    st.error(
                        f"Question {i}: Wrong"
                    )

                    st.info(
                        f"Correct Answer: {correct}"
                    )

            if user_answers:

                percentage = (
                    score /
                    len(user_answers)
                ) * 100

                st.header(
                    f"Final Score: "
                    f"{score}/{len(user_answers)}"
                )

                st.progress(
                    int(percentage)
                )

                st.write(
                    f"Percentage: "
                    f"{percentage:.2f}%"
                )


# =========================================================
# PAGE ROUTING
# =========================================================

if st.session_state.logged_in:

    # ONLY authenticated users see Quiz Builder
    quiz_page()

else:

    # Unauthenticated users ONLY see Sign In/Sign Up
    if st.session_state.page == "signup":

        signup_page()

    else:

        signin_page()