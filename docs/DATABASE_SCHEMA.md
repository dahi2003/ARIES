# Database Schema

## Tables

### users

- `id`: integer primary key
- `email`: unique string
- `full_name`: string
- `hashed_password`: string
- `role`: string (`superadmin`, `professor`, `student`)
- `created_at`: timestamp

### subjects

- `id`: integer primary key
- `name`: string
- `professor_id`: foreign key -> users.id
- `created_at`: timestamp

### answer_keys

- `id`: integer primary key
- `subject_id`: foreign key -> subjects.id
- `filename`: string
- `content`: text
- `uploaded_at`: timestamp

### student_copies

- `id`: integer primary key
- `subject_id`: foreign key -> subjects.id
- `student_name`: string
- `student_email`: string
- `filename`: string
- `status`: string (`pending`, `processing`, `completed`, `failed`)
- `extracted_text`: text
- `uploaded_at`: timestamp

### evaluations

- `id`: integer primary key
- `copy_id`: foreign key -> student_copies.id
- `score`: float
- `max_score`: float
- `feedback`: text
- `report_path`: string
- `created_at`: timestamp
