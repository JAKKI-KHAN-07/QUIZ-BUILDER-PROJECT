# Quiz Builder 

An AI-powered Quiz Builder application that automatically generates quizzes based on user-provided topics, difficulty levels, and the number of questions. The application uses Generative AI to create relevant questions and helps students improve their knowledge through interactive assessments.

## 🚀 Features

- **User Authentication:** Sign up and sign in functionality.
- **AI-Powered Quiz Generation:** Automatically generates quizzes using Google's Gemini AI.
- **Customizable Quizzes:** Select a topic, difficulty level, and number of questions.
- **Multiple Difficulty Levels:** Easy, Medium, and Hard.
- **PDF/TXT Support:** Upload text or PDF files to generate quizzes (if enabled in your application).
- **Database Integration:** Stores user information and application data.
- **User-Friendly Interface:** Simple and interactive application interface.

## 🛠️ Technologies Used

### Frontend
- Python / Streamlit
- HTML, CSS 

### Backend
- Python
- FastAPI
- REST API

### Database
- SQLite

### AI Integration
- Google Gemini API

### Tools
- Visual Studio Code
- Git and GitHub
- 

## 📁 Project Structure

Quiz-Builder/
│
├── backend/
│   ├── main.py
│   ├── quiz_generator.py
│   └── other backend files
│
├── frontend/
│   └── frontend source files
│
├── requirements.txt
├── README.md
├── .gitignore
└── .env.example


##  Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/AI-Quiz-Builder.git
```

### 2. Navigate to the Project Directory

```bash
cd AI-Quiz-Builder
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

**Windows:**

```bash
venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure Environment Variables

Create a `.env` file in the appropriate directory and add your required configuration:

```env
GEMINI_API_KEY=your_gemini_api_key
JWT_SECRET=your_secret_key
```

Replace the placeholder values with your actual credentials.

## ▶️ Running the Application

### Start the Backend

From the project's root directory:

```bash
uvicorn backend.main:app --reload
```

Backend API:

```text
http://127.0.0.1:8000
```

API Documentation:

```text
http://127.0.0.1:8000/docs
```

### Start the Frontend

Run the frontend using the appropriate command for your application.

For Streamlit:

```bash
streamlit run frontend/app.py
```

Update the frontend path and command according to your actual project files.

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| GEMINI_API_KEY | Google Gemini API key |
| JWT_SECRET | Secret key for JWT authentication |

## 🎯 Project Objective

The main objective of AI Quiz Builder is to simplify quiz creation through Artificial Intelligence. It provides an efficient way for students and educators to generate customized quizzes based on different topics and difficulty levels, making learning more interactive, personalized, and effective.

## 🔮 Future Scope

- Support for additional AI models.
- More question formats, including true/false and fill-in-the-blanks.
- Quiz history and performance tracking.
- Leaderboards and score analytics.
- Personalized learning recommendations.
- Export quizzes in PDF format.

## 👨‍💻 Developer

**Jakki Khan**

B.Tech – Computer Science and Engineering

Swami Keshvanand Institute of Technology (SKIT), Jaipur

## 📜 License

This project is developed for educational and academic purposes.
