# Phase 2: Core Learning Modules - Execution Plan

**Status**: Ready to Start
**Estimated Duration**: 1-2 weeks
**Tasks**: 90 planned

---

## Overview

Phase 2 focuses on building the question bank, reading/listening/vocabulary/grammar practice modules, and progress tracking system.

---

## 1. Question Bank Foundation

### Database Models
- [ ] QuestionType enum (MCQ, FIB, Matching, Essay, Speaking)
- [ ] Difficulty enum (Easy, Medium, Hard)
- [ ] Question model
  - id (UUID, PK)
  - text (Text, required)
  - exam_type (IELTS/GRE/TOEFL)
  - section (Reading/Listening/Writing/Speaking)
  - difficulty (Easy/Medium/Hard)
  - question_type (MCQ/FIB/Matching/Essay/Speaking)
  - explanation (Text)
  - audio_url (Optional, for listening)
  - created_at, updated_at
  
- [ ] Answer model
  - id (UUID, PK)
  - question_id (UUID, FK)
  - text (Text, required)
  - is_correct (Boolean)
  - order (Integer, for display)
  
- [ ] UserAnswer model (for tracking attempts)
  - id (UUID, PK)
  - user_id (UUID, FK)
  - question_id (UUID, FK)
  - selected_answer_id (UUID, FK)
  - is_correct (Boolean)
  - time_taken (Integer, seconds)
  - created_at

### API Endpoints
- [ ] GET /api/questions - List questions (with filtering)
- [ ] GET /api/questions/{id} - Get single question
- [ ] POST /api/questions/{id}/answer - Submit answer
- [ ] GET /api/questions/my-answers - View user's answers

---

## 2. Reading Module

### Features
- [ ] Passage display
- [ ] MCQ questions
- [ ] Reading time tracking
- [ ] Progress through multiple passages

### Database
- [ ] Passage model
  - id (UUID, PK)
  - title (String)
  - content (Text)
  - exam_type (IELTS/GRE/TOEFL)
  - difficulty (Easy/Medium/Hard)
  - created_at, updated_at

### API Endpoints
- [ ] GET /api/passages - List passages
- [ ] GET /api/passages/{id} - Get passage with questions
- [ ] POST /api/passages/{id}/complete - Mark complete
- [ ] GET /api/reading/progress - User's reading progress

### Frontend
- [ ] Reading practice page
- [ ] Passage display component
- [ ] MCQ answer selection
- [ ] Timer for reading section
- [ ] Results page
- [ ] Explanation display

---

## 3. Listening Module

### Features
- [ ] Audio playback
- [ ] Multiple plays (limited)
- [ ] Question display
- [ ] Transcript option

### Database
- [ ] ListeningTrack model
  - id (UUID, PK)
  - title (String)
  - audio_url (String, S3)
  - transcript (Text, optional)
  - exam_type, difficulty

### API Endpoints
- [ ] GET /api/listening-tracks - List audio
- [ ] GET /api/listening-tracks/{id} - Get track with questions
- [ ] POST /api/listening/{id}/complete - Mark complete

### Frontend
- [ ] Listening practice page
- [ ] Audio player with controls
- [ ] Play count limitation
- [ ] Transcript toggle
- [ ] MCQ questions
- [ ] Timer
- [ ] Results

---

## 4. Vocabulary Module

### Features
- [ ] Word definition
- [ ] Context examples
- [ ] Spaced repetition
- [ ] Flashcards

### Database
- [ ] VocabularyWord model
  - id (UUID, PK)
  - word (String)
  - definition (Text)
  - part_of_speech (String)
  - examples (JSON array)
  - exam_type, difficulty
  - created_at

- [ ] UserVocabulary model
  - id (UUID, PK)
  - user_id, word_id (FKs)
  - proficiency_level (1-5)
  - review_count (Integer)
  - last_reviewed (Timestamp)

### API Endpoints
- [ ] GET /api/vocabulary/words - List vocabulary
- [ ] GET /api/vocabulary/my-words - User's vocabulary
- [ ] POST /api/vocabulary/{word_id}/review - Mark reviewed
- [ ] POST /api/vocabulary/add - Add word to learning

### Frontend
- [ ] Vocabulary list page
- [ ] Flashcard view
- [ ] Study mode (spaced repetition)
- [ ] Proficiency tracking
- [ ] Search and filter

---

## 5. Grammar Module

### Features
- [ ] Grammar rules by topic
- [ ] Categorized exercises
- [ ] Explanations
- [ ] Common mistakes

### Database
- [ ] GrammarTopic model
  - id (UUID, PK)
  - topic_name (String)
  - description (Text)
  - exam_type
  - created_at

- [ ] GrammarExercise model
  - id (UUID, PK)
  - topic_id (FK)
  - sentence (Text)
  - correct_form (String)
  - explanation (Text)
  - difficulty

### API Endpoints
- [ ] GET /api/grammar/topics - List grammar topics
- [ ] GET /api/grammar/topics/{id} - Topic with exercises
- [ ] POST /api/grammar/{exercise_id}/answer - Submit answer

### Frontend
- [ ] Grammar topics page
- [ ] Exercise view
- [ ] Interactive correction
- [ ] Rule explanations
- [ ] Progress tracker

---

## 6. Progress Tracking

### Database Models
- [ ] UserProgress model
  - id (UUID, PK)
  - user_id (UUID, FK)
  - exam_id (UUID, FK)
  - section (Reading/Listening/Writing/Speaking)
  - total_questions (Integer)
  - correct_answers (Integer)
  - accuracy (Float)
  - last_updated (Timestamp)

- [ ] StudySession model
  - id (UUID, PK)
  - user_id, exam_id (FKs)
  - session_date (Timestamp)
  - duration (Integer, seconds)
  - questions_attempted (Integer)
  - score (Float)

### API Endpoints
- [ ] GET /api/progress - Overall progress
- [ ] GET /api/progress/{exam_id} - Exam-specific progress
- [ ] GET /api/sessions - Study session history

### Frontend
- [ ] Progress dashboard
- [ ] Charts and statistics
- [ ] Study streak counter
- [ ] Accuracy trends
- [ ] Session history

---

## 7. Performance Improvements

- [ ] Add database indexes for frequently queried columns
- [ ] Implement Redis caching for frequently accessed data
- [ ] Add pagination to list endpoints
- [ ] Optimize database queries (N+1 prevention)
- [ ] Implement search with full-text indexing

---

## 8. Integration & Testing

- [ ] Unit tests for question models
- [ ] Integration tests for practice endpoints
- [ ] Frontend component tests
- [ ] E2E tests for learning flow
- [ ] Performance tests for question loading

---

## Implementation Order

### Week 1
1. Create all database models (Question, Answer, Passage, etc.)
2. Create migrations
3. Implement question bank API endpoints
4. Implement reading module endpoints

### Week 2
1. Implement listening module endpoints
2. Implement vocabulary module
3. Implement grammar module
4. Frontend pages for all modules
5. Testing and bug fixes

---

## API Summary - Phase 2 Endpoints

### Questions
- `GET /api/questions`
- `GET /api/questions/{id}`
- `POST /api/questions/{id}/answer`
- `GET /api/questions/my-answers`

### Reading
- `GET /api/passages`
- `GET /api/passages/{id}`
- `POST /api/passages/{id}/complete`
- `GET /api/reading/progress`

### Listening
- `GET /api/listening-tracks`
- `GET /api/listening-tracks/{id}`
- `POST /api/listening/{id}/complete`

### Vocabulary
- `GET /api/vocabulary/words`
- `GET /api/vocabulary/my-words`
- `POST /api/vocabulary/{word_id}/review`
- `POST /api/vocabulary/add`

### Grammar
- `GET /api/grammar/topics`
- `GET /api/grammar/topics/{id}`
- `POST /api/grammar/{exercise_id}/answer`

### Progress
- `GET /api/progress`
- `GET /api/progress/{exam_id}`
- `GET /api/sessions`

---

## New Frontend Pages

- [ ] `/practice` - Practice module selection
- [ ] `/practice/reading` - Reading practice
- [ ] `/practice/listening` - Listening practice
- [ ] `/practice/vocabulary` - Vocabulary builder
- [ ] `/practice/grammar` - Grammar exercises
- [ ] `/progress` - Progress dashboard
- [ ] `/progress/{exam_id}` - Exam-specific progress

---

## Database Tables to Create

1. questions
2. answers
3. user_answers
4. passages
5. listening_tracks
6. vocabulary_words
7. user_vocabulary
8. grammar_topics
9. grammar_exercises
10. user_progress
11. study_sessions

---

## Success Criteria

- ✅ All 12 new API endpoints functional
- ✅ Database schema properly normalized
- ✅ Reading practice fully working
- ✅ Listening with audio playback
- ✅ Vocabulary with spaced repetition
- ✅ Grammar exercises with explanations
- ✅ Progress tracking accurate
- ✅ 80%+ test coverage
- ✅ Performance acceptable (< 200ms API response)

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Large question dataset performance | Implement pagination, caching |
| Audio file serving | Use S3 with CDN |
| Real-time progress tracking | Queue updates with background jobs |
| UI complexity | Component library (shadcn/ui) |

---

## Dependencies

- Phase 1 completion ✅ (Complete)
- S3 bucket setup (for audio/images)
- OpenAI API for explanations (optional, Phase 3)

---

**Ready to Execute**: Phase 2 can start immediately after Phase 1 completion.

**Estimated Completion**: 1-2 weeks of active development

**Resources Needed**: 1 Full-stack developer
