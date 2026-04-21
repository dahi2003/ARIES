# Additional CRUD functions for marks/grading feature

def get_results_with_grades(db, subject_id):
    """Get all student results with grades for a subject"""
    from . import models
    results = db.query(
        models.StudentCopy,
        models.Evaluation
    ).outerjoin(
        models.Evaluation, models.Evaluation.copy_id == models.StudentCopy.id
    ).filter(
        models.StudentCopy.subject_id == subject_id
    ).all()
    
    data = []
    for copy, evaluation in results:
        score = evaluation.score if evaluation else 0.0
        max_score = evaluation.max_score if evaluation else 100.0
        percentage = (score / max_score * 100) if max_score > 0 else 0.0
        
        data.append({
            'copy_id': copy.id,
            'student_name': copy.student_name,
            'student_email': copy.student_email,
            'roll_number': copy.roll_number,
            'score': score,
            'max_score': max_score,
            'percentage': percentage,
            'feedback': evaluation.feedback if evaluation else None,
            'status': copy.status,
            'evaluation_id': evaluation.id if evaluation else None,
        })
    
    return data


def get_evaluation_by_id(db, evaluation_id):
    """Get evaluation by ID"""
    from . import models
    return db.query(models.Evaluation).filter(models.Evaluation.id == evaluation_id).first()


def update_evaluation(db, evaluation_id, score=None, feedback=None):
    """Update evaluation score and feedback"""
    from . import models
    evaluation = db.query(models.Evaluation).filter(models.Evaluation.id == evaluation_id).first()
    if evaluation:
        if score is not None:
            evaluation.score = score
        if feedback is not None:
            evaluation.feedback = feedback
        db.commit()
        db.refresh(evaluation)
    return evaluation
