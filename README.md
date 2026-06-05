<div align="center">
  <img src="https://img.icons8.com/color/96/000000/exam.png" alt="VedaAI Logo" width="80"/>
  <h1>📝 VedaAI - AI Assessment Creator</h1>
  <p><strong>Create professional, AI-generated assessment papers in seconds.</strong></p>
  
  [![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://vedaai-c25q9ngezka7bsbf6mtqdt.streamlit.app/)
  [![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
  [![Groq](https://img.shields.io/badge/AI-Groq%20Llama%203-orange.svg)](https://groq.com/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

  <br />
  <a href="https://vedaai-c25q9ngezka7bsbf6mtqdt.streamlit.app/"><strong>Explore the Live App »</strong></a>
  <br />
</div>

<hr />

## ✨ Overview

VedaAI is a powerful, teacher-facing assessment creation tool. Built with Streamlit and powered by the cutting-edge **Groq AI (Llama 3)**, it allows educators to effortlessly generate customized question papers based on specific subjects, topics, grade levels, and difficulty metrics.

Forget spending hours drafting questions or searching through question banks. Simply provide your requirements (or upload reference materials) and let VedaAI do the heavy lifting! This platform is designed specifically to reduce administrative burden on teachers, allowing them to focus more on what matters: teaching.

## 🚀 Live Demo

**Experience VedaAI here:** [https://vedaai-c25q9ngezka7bsbf6mtqdt.streamlit.app/](https://vedaai-c25q9ngezka7bsbf6mtqdt.streamlit.app/)

## 🎯 Key Features

- ⚡ **Lightning Fast Generation:** Powered by Groq's blazing fast inference engine, receive full exam papers in under a minute.
- 🎨 **Beautiful UI:** A clean, modern "Exam Paper" view with dynamic difficulty badges (🟢 Easy, 🟡 Moderate, 🔴 Hard).
- ⚙️ **Highly Customizable:** Select Grade (6-12), Subjects, Topics, Question Types (MCQ, Short/Long Answer, True/False, Fill in the Blanks), and Total Marks.
- 📄 **PDF Export:** Automatic, perfectly formatted PDF generation using ReportLab, ready for immediate printing or digital distribution.
- 📚 **Context Aware:** Upload your own reference materials (`.txt` or `.pdf` files) to ground the AI's question generation to your exact curriculum.
- 📱 **Fully Responsive:** Works seamlessly on both desktop and mobile devices.

## 🧠 How It Works

1. **Input Parameters:** The educator inputs the target demographic (Grade, Subject, Topic) and assessment parameters (Total Marks, Time Allowed, Difficulty).
2. **Contextual Grounding (Optional):** The educator can optionally upload class notes, textbook chapters, or syllabus documents. VedaAI extracts the text and uses it as the foundational knowledge base.
3. **AI Generation:** The request is sent to Groq's powerful Llama 3 models using a highly structured prompt to ensure pedagogical accuracy and format adherence.
4. **Instant Formatting:** The AI returns a structured JSON which Streamlit instantly renders into a beautiful, printable user interface.
5. **Download & Distribute:** With a single click, the assessment is compiled into a professional PDF document.

## 💡 Use Cases

- **Weekly Quizzes:** Quickly generate 10-mark quizzes to test reading comprehension on the latest chapter.
- **Mid-Term Examinations:** Create comprehensive, 100-mark papers with a balanced mix of MCQs and long-form questions.
- **Practice Worksheets:** Generate unlimited variations of practice questions for students struggling with a specific topic (e.g., Algebra or Thermodynamics).
- **Substitute Teacher Plans:** Have high-quality, relevant assignments ready for substitute teachers in minutes.

## 🛠️ Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/)
- **Backend/Logic:** Pure Python
- **AI Engine:** [Groq Cloud (Llama 3 Models)](https://groq.com/)
- **PDF Generation:** [ReportLab](https://www.reportlab.com/) & [PyPDF2](https://pypdf2.readthedocs.io/en/3.0.0/)

## 💻 Local Setup & Installation

If you want to run this project locally, follow these steps:

1. **Clone the repository**
   ```bash
   git clone https://github.com/Himanivashisht03/vedaai.git
   cd vedaai
   ```

2. **Install the dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your API Key**
   - Create a `.streamlit` folder in the root directory.
   - Create a `secrets.toml` file inside the `.streamlit` folder.
   - Add your Groq API Key:
     ```toml
     GROQ_API_KEY = "gsk_your_api_key_here"
     ```

4. **Run the Application**
   ```bash
   streamlit run app.py
   ```

## ☁️ Deployment Instructions

To deploy your own instance on Streamlit Cloud:

1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Sign in with your GitHub account.
3. Click **"New app"**.
4. Select the repository (e.g., `Himanivashisht03/vedaai`) and the `main` branch.
5. Set the Main file path to `app.py`.
6. Click **"Advanced settings"** and add your secret:
   ```toml
   GROQ_API_KEY = "gsk_your_api_key_here"
   ```
7. Click **Deploy!**

## 🗺️ Future Roadmap

- [ ] Add support for generating Answer Keys and Rubrics alongside the question paper.
- [ ] Multi-language support for regional educational boards.
- [ ] Export to Microsoft Word (.docx) format.
- [ ] Integration with Google Classroom for direct assignment posting.

---
<div align="center">
  <i>Built with ❤️ for Educators</i>
</div>
