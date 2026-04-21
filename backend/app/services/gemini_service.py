
# genai.configure(api_key=GEMINI_API_KEY)  # type: ignore

import fitz  # PyMuPDF
import google.generativeai as genai  # type: ignore
import PIL.Image
import io
import json
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY set here")

genai.configure(api_key=GEMINI_API_KEY)
# Using Gemini 1.5 Flash
model = genai.GenerativeModel('gemini-2.5-flash')


# --- HELPER FUNCTION ---
def _convert_pdf_to_images(pdf_bytes: bytes, start_page: int = 0, end_page: Optional[int] = None) -> list:
    """Helper function to convert PDF bytes to a list of PIL Images."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages_images = []
    
    total_pages: int = len(doc)
    final_end_page: int = total_pages
    
    if end_page is not None and end_page < total_pages:
        final_end_page = end_page
        
    for i in range(start_page, final_end_page):
        page = doc.load_page(i)
        pix = page.get_pixmap(dpi=150)
        img = PIL.Image.open(io.BytesIO(pix.tobytes("png")))
        pages_images.append(img)
        
    if not pages_images:
        raise ValueError("No readable pages found in the PDF.")
        
    return pages_images



async def extract_answer_key_with_gemini(pdf_bytes: bytes) -> str:
    """
    Reads the Professor's Answer Key PDF and structures it for evaluation.
    Used during the Answer Key Upload process.
    """
    try:
        print("1. Background task started. Converting Answer Key PDF to images...")
        # Covert all pages of the answer key
        key_images = _convert_pdf_to_images(pdf_bytes, start_page=0)
        
        #  PROMPT FOR EXTRACTING ANSWER KEY
        prompt = """
        You are an expert academic assistant. I am providing you with images of an official Exam Answer Key and Marking Scheme.
        Please extract all the text accurately. 
        Format the output clearly with Question Numbers, Correct Answers, and the Weightage/Marks for each question.
        Fix any obvious typos, but do not change the core meaning of the answers.
        Return ONLY the clean, structured text.
        """
        
        print("2. Sending Answer Key to Gemini...")
        response = model.generate_content([prompt] + key_images)
        print("3. Answer Key extracted successfully!")
        
        return response.text.strip()
        
    except Exception as e:
        print(f"====== ANSWER KEY EXTRACTION ERROR: {str(e)} ======")
        raise Exception(f"Failed to extract Answer Key using Gemini: {str(e)}")

async def evaluate_exam_with_gemini(
    pdf_bytes: bytes, 
    answer_key: str, 
    start_page: int = 0, 
    end_page: Optional[int] = None
) -> dict: 
    """
    Evaluates the Student's handwritten copy against the extracted Answer Key.
    """
    try:
        print("1. Background task started. Converting PDF to images...")
        written_pages = _convert_pdf_to_images(pdf_bytes, start_page=start_page, end_page=end_page)
        print(f"2. Successfully converted {len(written_pages)} pages.")

        prompt = f"""
        You are an expert Professor evaluating an exam.
        
        OFFICIAL ANSWER KEY:
        {answer_key}
        
        INSTRUCTIONS:
        1. Count the TOTAL number of questions present in the Official Answer Key.
        2. Read the student's handwritten responses from the images.
        3. Grade ONLY the questions the student has actually attempted.
        
        CRITICAL JSON FORMAT RULES:
        You MUST return STRICTLY a JSON OBJECT with exactly two keys: "total_questions_in_key" and "evaluations".
        Do not use unescaped double quotes inside text strings.
        
        Example Format:
        {{
            "total_questions_in_key": 10,
            "evaluations": [
                {{
                    "question_number": "1",
                    "student_response": "exact transcribed text",
                    "score": 0.75,
                    "professor_comment": "brief feedback"
                }}
            ]
        }}
        """
        
        print("3. Sending request to Gemini 2.5 Flash...")
        response = model.generate_content(
            [prompt] + written_pages,
            generation_config={"response_mime_type": "application/json"}
        )
        
        print("4. Gemini responded! Cleaning JSON...")
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:-3].strip()
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:-3].strip()
            
        evaluation_data = json.loads(raw_text)
        print("5. JSON parsed successfully!")
        return evaluation_data

    except Exception as e:
        print("\n====== BACKGROUND TASK ASLI ERROR ======")
        print(str(e))
        print("========================================\n")
        raise Exception(f"Gemini Vision Evaluation failed: {str(e)}")