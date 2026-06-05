import streamlit as st
import anthropic
import json
import time
import io
import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

# Page config
st.set_page_config(page_title="VedaAI Assessment Creator", page_icon="📝", layout="wide")

def apply_custom_css():
    st.markdown("""
        <style>
        .stApp { background-color: #fafafa; }
        .main .block-container { max-width: 900px; padding-top: 2rem; padding-bottom: 2rem; }
        .difficulty-easy { background-color: #d1fae5; color: #065f46; padding: 4px 8px; border-radius: 12px; font-size: 0.8em; font-weight: bold; }
        .difficulty-moderate { background-color: #fef3c7; color: #92400e; padding: 4px 8px; border-radius: 12px; font-size: 0.8em; font-weight: bold; }
        .difficulty-hard { background-color: #fee2e2; color: #991b1b; padding: 4px 8px; border-radius: 12px; font-size: 0.8em; font-weight: bold; }
        .difficulty-mixed { background-color: #e0e7ff; color: #3730a3; padding: 4px 8px; border-radius: 12px; font-size: 0.8em; font-weight: bold; }
        .section-card { border: 1px solid #e5e7eb; border-radius: 8px; padding: 24px; margin-bottom: 24px; background-color: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .q-row { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; }
        .q-text { font-weight: 500; color: #1f2937; }
        .q-meta { display: flex; gap: 12px; align-items: center; white-space: nowrap; }
        .q-marks { font-weight: 600; color: #4b5563; }
        .q-options { margin-left: 24px; margin-top: 8px; margin-bottom: 16px; color: #4b5563; }
        .q-option-item { margin-bottom: 4px; }
        .paper-header { text-align: center; border-bottom: 2px solid #e5e7eb; padding-bottom: 16px; margin-bottom: 24px; background-color: white; padding: 24px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .paper-title { font-size: 24px; font-weight: bold; color: #111827; margin-bottom: 16px; }
        .paper-meta { display: flex; justify-content: space-between; color: #4b5563; font-size: 14px; margin-bottom: 16px; }
        .student-info { display: flex; justify-content: space-between; margin-top: 16px; font-size: 14px; color: #374151; }
        </style>
    """, unsafe_allow_html=True)

# State initialization
if 'page' not in st.session_state:
    st.session_state.page = 'create'
if 'generated_paper' not in st.session_state:
    st.session_state.generated_paper = None

def extract_text_from_file(uploaded_file) -> str:
    if uploaded_file is None:
        return ""
    try:
        if uploaded_file.name.endswith(".txt"):
            return uploaded_file.getvalue().decode("utf-8")
        elif uploaded_file.name.endswith(".pdf"):
            reader = PyPDF2.PdfReader(uploaded_file)
            return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    except Exception as e:
        st.warning(f"Failed to extract text from file: {e}")
    return ""

def generate_pdf(paper_data: dict) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='CenterTitle', parent=styles['Heading1'], alignment=TA_CENTER, spaceAfter=12)
    meta_style = ParagraphStyle(name='Meta', parent=styles['Normal'], alignment=TA_CENTER, spaceAfter=20)
    section_title_style = ParagraphStyle(name='SectionTitle', parent=styles['Heading2'], spaceBefore=15, spaceAfter=5)
    instruction_style = ParagraphStyle(name='Instruction', parent=styles['Italic'], spaceAfter=15)
    question_style = ParagraphStyle(name='Question', parent=styles['Normal'], spaceAfter=5, leading=14)
    option_style = ParagraphStyle(name='Option', parent=styles['Normal'], leftIndent=20, spaceAfter=2, leading=12)
    
    story = []
    
    # Header
    story.append(Paragraph(f"<b>{paper_data.get('title', 'Assessment Paper')}</b>", title_style))
    
    meta_text = (f"<b>Subject:</b> {paper_data.get('subject', '')} &nbsp;&nbsp;&nbsp;&nbsp; "
                 f"<b>Grade:</b> {paper_data.get('grade', '')} &nbsp;&nbsp;&nbsp;&nbsp; "
                 f"<b>Total Marks:</b> {paper_data.get('totalMarks', '')} &nbsp;&nbsp;&nbsp;&nbsp; "
                 f"<b>Time:</b> {paper_data.get('timeAllowed', '')}")
    story.append(Paragraph(meta_text, meta_style))
    
    # Student Info
    student_info = ("Name: ____________________________________ &nbsp;&nbsp;&nbsp;&nbsp; "
                    "Roll No: _______________ &nbsp;&nbsp;&nbsp;&nbsp; "
                    "Section: _______________")
    story.append(Paragraph(student_info, styles['Normal']))
    story.append(Spacer(1, 30))
    
    # Sections
    for section in paper_data.get('sections', []):
        story.append(Paragraph(f"<b>Section {section.get('sectionLabel', '')}: {section.get('sectionTitle', '')}</b>", section_title_style))
        if section.get('instruction'):
            story.append(Paragraph(section.get('instruction', ''), instruction_style))
            
        for q in section.get('questions', []):
            q_text = f"<b>Q{q.get('questionNumber', '')}.</b> {q.get('text', '')}"
            marks = q.get('marks', '')
            if marks:
                q_text += f" <b>[{marks}]</b>"
                
            story.append(Paragraph(q_text, question_style))
            
            for opt in q.get('options', []):
                story.append(Paragraph(opt, option_style))
                
            story.append(Spacer(1, 10))
            
    doc.build(story)
    buffer.seek(0)
    return buffer

def call_ai(prompt: str, retries=1) -> dict:
    if "ANTHROPIC_API_KEY" not in st.secrets:
        raise ValueError("ANTHROPIC_API_KEY not found in Streamlit secrets.")
        
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    
    for attempt in range(retries + 1):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.content[0].text.strip()
            
            # Clean possible markdown formatting
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
                
            return json.loads(content)
        except Exception as e:
            if attempt == retries:
                # Safe fallback if the specific model isn't available
                try:
                    response = client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=4000,
                        temperature=0.7,
                        messages=[{"role": "user", "content": prompt + "\nEnsure you respond with ONLY pure JSON. No markdown."}]
                    )
                    content = response.content[0].text.strip()
                    if content.startswith("```json"):
                        content = content[7:]
                    if content.endswith("```"):
                        content = content[:-3]
                    return json.loads(content)
                except Exception as final_e:
                    raise Exception(f"AI Generation failed: {str(final_e)}")
            time.sleep(1)

def render_create_page():
    st.title("📝 VedaAI Assessment Creator")
    st.markdown("Create professional AI-generated assessment papers in seconds.")
    
    with st.form("assessment_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            subject = st.text_input("Subject *", placeholder="e.g. Science, Mathematics")
            grade = st.selectbox("Grade Level *", [f"Grade {i}" for i in range(6, 13)])
            total_marks = st.number_input("Total Marks *", min_value=1, value=50)
            time_allowed = st.selectbox("Time Allowed *", ["30 min", "1 hour", "2 hours", "3 hours"])
            
        with col2:
            topic = st.text_input("Topic *", placeholder="e.g. Thermodynamics, Algebra")
            difficulty = st.selectbox("Difficulty *", ["Mixed", "Easy", "Medium", "Hard"])
            num_questions = st.slider("Number of Questions *", min_value=1, max_value=50, value=10)
            question_types = st.multiselect("Question Types *", 
                ["MCQ", "Short Answer", "Long Answer", "True/False", "Fill in the Blank"],
                default=["MCQ", "Short Answer"])
                
        additional_instructions = st.text_area("Additional Instructions (Optional)", placeholder="Any specific requirements?")
        uploaded_file = st.file_uploader("Upload Reference Material (Optional)", type=["pdf", "txt"])
        
        submitted = st.form_submit_button("Generate Assessment ✨", type="primary", use_container_width=True)
        
        if submitted:
            if not subject or not topic or not question_types:
                st.error("Please fill in all required fields marked with (*).")
                return
                
            with st.spinner("🧠 VedaAI is crafting your assessment... Please wait."):
                progress_bar = st.progress(0)
                
                progress_bar.progress(10, text="Reading reference material...")
                ref_text = extract_text_from_file(uploaded_file)
                
                progress_bar.progress(30, text="Prompting Claude AI...")
                
                prompt = f"""You are an expert AI teacher. Generate an assessment with the following specifications:
                - Subject: {subject}
                - Topic: {topic}
                - Grade: {grade}
                - Number of Questions: {num_questions}
                - Total Marks: {total_marks}
                - Difficulty: {difficulty}
                - Question Types: {', '.join(question_types)}
                - Time Allowed: {time_allowed}
                - Additional Instructions: {additional_instructions}
                
                Reference Material (if any):
                {ref_text}
                
                Return ONLY a valid JSON object matching this exact schema. Do not include any markdown formatting like ```json, just the raw JSON text:
                {{
                  "title": "Assessment Title",
                  "subject": "{subject}", 
                  "grade": "{grade}",
                  "totalMarks": {total_marks},
                  "timeAllowed": "{time_allowed}",
                  "sections": [
                    {{
                      "sectionLabel": "A",
                      "sectionTitle": "Multiple Choice Questions",
                      "instruction": "Attempt all questions",
                      "marks": 10,
                      "questions": [
                        {{
                          "questionNumber": 1,
                          "text": "Question text...",
                          "options": ["(A) ...", "(B) ...", "(C) ...", "(D) ..."],
                          "difficulty": "Moderate",
                          "marks": 2,
                          "type": "MCQ"
                        }}
                      ]
                    }}
                  ]
                }}"""
                
                try:
                    progress_bar.progress(50, text="Generating content (this may take up to a minute)...")
                    paper_data = call_ai(prompt, retries=1)
                    
                    progress_bar.progress(90, text="Finalizing paper format...")
                    
                    st.session_state.generated_paper = paper_data
                    progress_bar.progress(100, text="Done!")
                    time.sleep(0.5)
                    st.session_state.page = 'view'
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating assessment: {str(e)}")

def get_difficulty_class(diff: str) -> str:
    diff = diff.lower()
    if 'easy' in diff: return 'difficulty-easy'
    if 'hard' in diff: return 'difficulty-hard'
    if 'mix' in diff: return 'difficulty-mixed'
    return 'difficulty-moderate'

def render_view_page():
    paper = st.session_state.generated_paper
    if not paper:
        st.session_state.page = 'create'
        st.rerun()
        
    # Actions Bar
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("← Back / Edit", use_container_width=True):
            st.session_state.page = 'create'
            st.rerun()
    with col2:
        pdf_buffer = generate_pdf(paper)
        st.download_button(
            label="📄 Download PDF",
            data=pdf_buffer,
            file_name=f"{paper.get('subject', 'Assessment')}_{paper.get('grade', 'Grade').replace(' ', '')}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
        
    st.markdown("<br>", unsafe_allow_html=True)
        
    # Paper Display
    st.markdown(f"""
        <div class="paper-header">
            <div class="paper-title">{paper.get('title', 'Assessment Paper')}</div>
            <div class="paper-meta">
                <span><b>Subject:</b> {paper.get('subject', '')}</span>
                <span><b>Grade:</b> {paper.get('grade', '')}</span>
                <span><b>Total Marks:</b> {paper.get('totalMarks', '')}</span>
                <span><b>Time Allowed:</b> {paper.get('timeAllowed', '')}</span>
            </div>
            <div class="student-info">
                <span>Name: ___________________________</span>
                <span>Roll No: ____________</span>
                <span>Section: ____________</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    for section in paper.get('sections', []):
        st.markdown(f"""
            <div class="section-card">
                <h3 style="margin-top:0; color:#111827;">Section {section.get('sectionLabel', '')}: {section.get('sectionTitle', '')}</h3>
                <p style="color:#4b5563; font-style:italic; margin-bottom: 24px;">{section.get('instruction', '')}</p>
        """, unsafe_allow_html=True)
        
        for q in section.get('questions', []):
            diff_class = get_difficulty_class(q.get('difficulty', 'Moderate'))
            diff_label = q.get('difficulty', 'Moderate')
            
            st.markdown(f"""
                <div class="q-row">
                    <div class="q-text"><b>Q{q.get('questionNumber', '')}.</b> {q.get('text', '')}</div>
                    <div class="q-meta">
                        <span class="{diff_class}">{diff_label}</span>
                        <span class="q-marks">[{q.get('marks', '')}]</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            options = q.get('options', [])
            if options:
                opts_html = "".join([f"<div class='q-option-item'>{opt}</div>" for opt in options])
                st.markdown(f"<div class='q-options'>{opts_html}</div>", unsafe_allow_html=True)
                
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    apply_custom_css()
    if st.session_state.page == 'create':
        render_create_page()
    else:
        render_view_page()
