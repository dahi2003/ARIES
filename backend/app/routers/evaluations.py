import os
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from ..dependencies import get_db, require_role
from .. import crud
from ..database import SessionLocal
from ..services.gemini_service import evaluate_exam_with_gemini
from ..services.report import generate_result_report

router = APIRouter(prefix='/api/evaluations', tags=['evaluations'])

class EvaluationTriggerRequest(BaseModel):
    subject_id: int

async def evaluate_single_copy_background_task(copy_id: int, answer_key_content: str):
    db = SessionLocal()
    try:
        print(f"\n --- Starting evaluation for Copy ID: {copy_id} ---")
        copy = crud.get_copy_by_id(db, copy_id)
        if not copy:
            print(" Error: Copy not found in DB.")
            return

        # Status update karo
        crud.update_copy_status(db, copy, 'processing')
        
        # --- SILENT KILLER CHECK ---
        print(f" Checking file path in DB: {copy.file_path}")
        if not copy.file_path:
            print(" ERROR: Database mein file_path NONE hai (Database sync issue)!")
            crud.update_copy_status(db, copy, 'failed')
            return
            
        if not os.path.exists(copy.file_path):
            print(f" ERROR: File hard drive par nahi mili! Path searched: {copy.file_path}")
            crud.update_copy_status(db, copy, 'failed')
            return

        print(" File found! Reading PDF...")
        # 1. Read PDF file from disk
        with open(copy.file_path, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()

        print(" Sending to Gemini...")
        # 2. Evaluate using Gemini
        evaluation_data = await evaluate_exam_with_gemini(
            pdf_bytes=pdf_bytes, 
            answer_key=answer_key_content,
            start_page=0  # Testing ke liye isko 0 rakha hai
        )

       
       
        
        evaluations_list = []
        total_q_in_key = 0
        
        # --- DEFENSE 1: Check if AI returned a Dictionary ---
        if isinstance(evaluation_data, dict):
            evaluations_list = evaluation_data.get("evaluations", [])
            total_q_in_key = evaluation_data.get("total_questions_in_key", len(evaluations_list))
            
        # --- DEFENSE 2: Check if AI forgot the dictionary and sent an Array directly ---
        elif isinstance(evaluation_data, list):
            evaluations_list = evaluation_data
            total_q_in_key = len(evaluations_list)
            
        total_score = 0
        feedback_lines = []
        valid_evaluations = []
        
        for item in evaluations_list:
            # --- DEFENSE 3: Check if the item is properly formatted as a Dictionary ---
            if isinstance(item, dict):
                q_num = item.get("question_number", item.get("question", "N/A"))
                comment = item.get("professor_comment", item.get("comment", item.get("feedback", "No comment.")))
                score = item.get("score", item.get("marks", 0))
                
                try:
                    total_score += float(score)
                except (ValueError, TypeError):
                    pass
                    
                feedback_lines.append(f"Q{q_num}: {comment}")
                valid_evaluations.append(item)
                
            # --- DEFENSE 4: If AI sent a random string instead of an object ---
            elif isinstance(item, str):
                feedback_lines.append(f"AI Note: {item}")
                
        # Handle case where AI didn't return any valid questions
        if total_q_in_key == 0:
            total_q_in_key = max(len(valid_evaluations), 1) # Prevent 0 division in UI
            
        overall_feedback = "\n".join(feedback_lines)

        # 4. Generate Report
        report_data = {
            "score": total_score,
            "max_score": total_q_in_key,
            "feedback": overall_feedback if overall_feedback else "Could not generate feedback format.",
            "details": valid_evaluations  # Sirf valid objects hi PDF me jayenge
        }        
        
        report_file = f'report_copy_{copy.id}.pdf'
        report_path = generate_result_report(
            copy.student_name, 
            copy.subject.name, 
            report_data, 
            report_file
        )
        
        # 5. Save results to DB
        crud.create_evaluation(
            db, 
            copy_id=copy.id, 
            score=total_score, 
            max_score=total_q_in_key, 
            feedback=overall_feedback, 
            report_path=report_path
        )
        
        crud.update_copy_status(db, copy, 'completed')
        print(f" SUCCESS! Copy ID {copy.id} evaluated successfully.\n")

    except Exception as e:
        print(f"\n FATAL ERROR IN BACKGROUND TASK ")
        print(f"Error on copy {copy_id}: {str(e)}")
        print(f" ❌ ❌ ❌\n")
        crud.update_copy_status(db, copy, 'failed')
    finally:
        db.close()

@router.post('/trigger')
async def trigger_evaluation(
    request: EvaluationTriggerRequest,
    background_tasks: BackgroundTasks, 
    current_user = Depends(require_role('professor', 'superadmin')),
    db: Session = Depends(get_db),
):
    subject_id = request.subject_id
    copies = crud.get_student_copies_by_subject(db, subject_id)
    if not copies:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No student copies found for subject')

    subject = copies[0].subject
    answer_key = subject.answer_keys[-1] if subject and subject.answer_keys else None
    if not answer_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Upload an answer key before evaluation')

    queued_count = 0
    for copy in copies:
        if copy.status not in ['completed', 'processing']:
            background_tasks.add_task(
                evaluate_single_copy_background_task, 
                copy_id=copy.id, 
                answer_key_content=answer_key.content
            )
            queued_count += 1
            
    return {
        'status': 'evaluation tasks queued', 
        'queued_count': queued_count,
        'message': 'Copies are being evaluated in the background.'
    }