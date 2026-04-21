import os
import asyncio
from celery import Celery
from .report import generate_result_report
from .storage import resolve_report_path
from ..config import REDIS_URL

from .gemini_service import evaluate_exam_with_gemini

celery_app = Celery(
    'evaluation_worker',
    broker=REDIS_URL,
    backend=REDIS_URL,
)

@celery_app.task(name='evaluation.process_student_copy')
def process_student_copy(task_payload: dict) -> dict:
    from ..database import SessionLocal
    from .. import crud

    db = SessionLocal()
    try:
        copy_id = task_payload['copy_id']
        copy = crud.get_copy_by_id(db, copy_id)
        
        # Safe File Check
        if not copy or not copy.file_path or not os.path.exists(copy.file_path):
            if copy: crud.update_copy_status(db, copy, 'failed')
            return {'success': False, 'reason': 'Copy or file not found in storage'}

        answer_key = db.query(type(copy.subject.answer_keys[0])).filter_by(subject_id=copy.subject_id).order_by('uploaded_at desc').first()
        if not answer_key:
            crud.update_copy_status(db, copy, 'failed')
            return {'success': False, 'reason': 'Answer key missing'}

        crud.update_copy_status(db, copy, 'processing')

        # 1. Read PDF file
        with open(copy.file_path, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()

       
        evaluation_data = asyncio.run(evaluate_exam_with_gemini(
            pdf_bytes=pdf_bytes, 
            answer_key=answer_key.content,
            start_page=0
        ))

        # 3. Apply our  Math Logic
        evaluations_list = []
        total_q_in_key = 0
        
        if isinstance(evaluation_data, dict):
            evaluations_list = evaluation_data.get("evaluations", [])
            total_q_in_key = evaluation_data.get("total_questions_in_key", len(evaluations_list))
        elif isinstance(evaluation_data, list):
            evaluations_list = evaluation_data
            total_q_in_key = len(evaluations_list)
            
        total_score = 0
        feedback_lines = []
        valid_evaluations = []
        
        for item in evaluations_list:
            if isinstance(item, dict):
                q_num = item.get("question_number", item.get("question", "N/A"))
                comment = item.get("professor_comment", item.get("comment", item.get("feedback", "No comment.")))
                score = item.get("score", item.get("marks", 0))
                try: total_score += float(score)
                except (ValueError, TypeError): pass
                    
                feedback_lines.append(f"Q{q_num}: {comment}")
                valid_evaluations.append(item)
                
        if total_q_in_key == 0: total_q_in_key = max(len(valid_evaluations), 1)
        overall_feedback = "\n".join(feedback_lines)

        report_data = {
            "score": total_score,
            "max_score": total_q_in_key,
            "feedback": overall_feedback if overall_feedback else "Could not generate feedback format.",
            "details": valid_evaluations
        }

        # 4. Generate Report and Save
        report_file = f'report_copy_{copy_id}.pdf'
        report_path = generate_result_report(copy.student_name, copy.subject.name, report_data, report_file)
        
        crud.create_evaluation(
            db, copy_id=copy_id, score=total_score, max_score=total_q_in_key, 
            feedback=overall_feedback, report_path=report_path
        )
        crud.update_copy_status(db, copy, 'completed')
        
        return {'success': True, 'report_path': report_path}

    except Exception as e:
        print(f"CELERY TASK ERROR: {str(e)}")
        if 'copy' in locals() and copy:
            crud.update_copy_status(db, copy, 'failed')
        return {'success': False, 'reason': str(e)}
    finally:
        db.close()