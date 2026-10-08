"""Small idempotent starter content set for local development."""

import asyncio

from sqlalchemy import func, insert, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from services.api.models_phase2_isolated import (
    Answer,
    GrammarExercise,
    GrammarTopic,
    ListeningTrack,
    Passage,
    Question,
    VocabularyWord,
    listening_questions,
    passage_questions,
)
from services.api.sample_content import seed_expanded_content


async def seed_learning_content(session_factory: async_sessionmaker) -> None:
    """Populate empty learning tables with a small usable practice set."""
    async with session_factory() as session:
        count = await session.scalar(select(func.count()).select_from(Passage))
        if not count:
            passage = Passage(
                title="The changing shape of city parks",
                content=(
                    "Urban parks were once designed mainly as ornamental spaces, but their role has expanded. "
                    "Today, many cities use parks to manage storm water, cool neighborhoods, and support local wildlife. "
                    "A meadow can absorb heavy rain more effectively than a paved plaza, while trees lower nearby "
                    "temperatures during heat waves. These benefits depend on thoughtful planning. A park that is "
                    "easy to reach, safe to use, and shaped with community input is more likely to become part of "
                    "daily life. Researchers therefore evaluate parks not only by their area, but also by access, "
                    "ecological value, and the activities they make possible."
                ),
                word_count=113,
                exam_type="IELTS",
                difficulty="easy",
                topic="Urban planning",
                time_limit=600,
            )
            reading_question = Question(
                text="Which benefit of urban parks is mentioned in the passage?",
                exam_type="IELTS",
                section="reading",
                question_type="MCQ",
                difficulty="easy",
                explanation="The passage says trees lower nearby temperatures during heat waves.",
                answers=[
                    Answer(text="They lower nearby temperatures", is_correct=True, order=1),
                    Answer(text="They eliminate all city traffic", is_correct=False, order=2),
                    Answer(text="They increase the amount of paved land", is_correct=False, order=3),
                    Answer(text="They replace the need for public transport", is_correct=False, order=4),
                ],
            )
            second_reading_question = Question(
                text="According to the passage, what helps a park become part of daily life?",
                exam_type="IELTS",
                section="reading",
                question_type="MCQ",
                difficulty="easy",
                explanation="The passage highlights access, safety, and community input.",
                answers=[
                    Answer(text="Easy access, safety, and community input", is_correct=True, order=1),
                    Answer(text="A large entrance fee", is_correct=False, order=2),
                    Answer(text="Ornamental design alone", is_correct=False, order=3),
                    Answer(text="A location outside the city", is_correct=False, order=4),
                ],
            )
            session.add_all([passage, reading_question, second_reading_question])
            await session.flush()
            await session.execute(
                insert(passage_questions),
                [
                    {"passage_id": passage.id, "question_id": reading_question.id},
                    {"passage_id": passage.id, "question_id": second_reading_question.id},
                ],
            )

        count = await session.scalar(select(func.count()).select_from(ListeningTrack))
        if not count:
            session.add_all([
                ListeningTrack(
                    title="Campus orientation: library services",
                    audio_url="",
                    duration=48,
                    transcript=(
                        "Welcome to the campus library. The main floor is open every day from eight in the morning "
                        "until ten at night. Group study rooms can be reserved online up to one week in advance. "
                        "If you need research help, visit the information desk on the second floor. During exam "
                        "week, the library extends its hours until midnight."
                    ),
                    exam_type="IELTS",
                    difficulty="easy",
                    topic="Campus life",
                    accent="North American",
                ),
                Question(
                    text="Where can students get help with research?",
                    exam_type="IELTS",
                    section="listening",
                    question_type="MCQ",
                    difficulty="easy",
                    answers=[
                        Answer(text="At the information desk on the second floor", is_correct=True, order=1),
                        Answer(text="At the entrance to the main floor", is_correct=False, order=2),
                        Answer(text="In the group study rooms", is_correct=False, order=3),
                        Answer(text="At the campus bookstore", is_correct=False, order=4),
                    ],
                ),
                Question(
                    text="How far ahead can students reserve a group study room?",
                    exam_type="IELTS",
                    section="listening",
                    question_type="MCQ",
                    difficulty="easy",
                    answers=[
                        Answer(text="Up to one week", is_correct=True, order=1),
                        Answer(text="One month", is_correct=False, order=2),
                        Answer(text="Only on the same day", is_correct=False, order=3),
                        Answer(text="Two weeks", is_correct=False, order=4),
                    ],
                ),
            ])

        count = await session.scalar(select(func.count()).select_from(VocabularyWord))
        if not count:
            session.add_all([
                VocabularyWord(
                    word="meticulous",
                    definition="Showing great attention to detail; very careful and precise.",
                    part_of_speech="adjective",
                    examples=["The researcher kept meticulous notes during the experiment."],
                    synonyms=["careful", "thorough"],
                    exam_type="IELTS",
                    difficulty="advanced",
                    frequency=8,
                ),
                VocabularyWord(
                    word="pragmatic",
                    definition="Dealing with problems in a practical and realistic way.",
                    part_of_speech="adjective",
                    examples=["The team chose a pragmatic solution that fit the budget."],
                    synonyms=["practical", "realistic"],
                    exam_type="IELTS",
                    difficulty="intermediate",
                    frequency=7,
                ),
            ])

        count = await session.scalar(select(func.count()).select_from(GrammarTopic))
        if not count:
            session.add(
                GrammarTopic(
                    topic_name="Verb tense consistency",
                    description="Keep time relationships clear when describing events and evidence.",
                    explanation="Use the same tense for actions that occur in the same time frame.",
                    examples=["The study found a pattern and explained its causes."],
                    exam_type="IELTS",
                    difficulty="intermediate",
                    order=1,
                    exercises=[
                        GrammarExercise(
                            sentence="Yesterday, the committee ___ (review) the proposal and approved it.",
                            correct_form="reviewed",
                            explanation="The past-time marker 'Yesterday' calls for the simple past.",
                            difficulty="easy",
                            hint="Look for the past-time marker.",
                        )
                    ],
                )
            )

        # A small cross-exam reading bank supports the quick diagnostic route.
        diagnostic_items = {
            "IELTS": [
                ("A university library extended its evening hours after a student survey. What most directly prompted the change?", [
                    ("Student feedback", True), ("A new building", False), ("A staff reduction", False), ("A change in course fees", False)]),
                ("Researchers compared two planting methods over three seasons. Which detail would make the comparison fairest?", [
                    ("Using similar plots and recording the same measures", True), ("Changing the measures each season", False), ("Selecting only the best result", False), ("Asking participants to recall results later", False)]),
                ("A city planted shade trees along a busy street. Which outcome would best support the project’s stated aim of reducing heat?", [
                    ("Lower afternoon temperatures beneath the trees", True), ("More cars using the street", False), ("Fewer street signs", False), ("Higher nighttime lighting costs", False)]),
            ],
            "TOEFL": [
                ("A campus notice says laboratory access is limited during equipment maintenance. What should students do before visiting?", [
                    ("Check the updated access schedule", True), ("Bring their own equipment", False), ("Ask for a course grade change", False), ("Visit after the term ends", False)]),
                ("A study found that students who took short breaks reported better concentration. What can be concluded from this statement alone?", [
                    ("The students reported a relationship between breaks and concentration", True), ("Breaks guarantee higher exam scores", False), ("Every student prefers the same schedule", False), ("The study proves breaks cause all improvements", False)]),
                ("The word ‘allocate’ in ‘the department allocated funds for new computers’ is closest in meaning to:", [
                    ("Set aside", True), ("Take away", False), ("Count again", False), ("Put off", False)]),
                ("A lecturer says the first draft is a starting point rather than a finished product. What does the lecturer imply?", [
                    ("Students should revise their drafts", True), ("Students should skip the draft", False), ("The topic will be replaced", False), ("The assignment has no deadline", False)]),
                ("Which sentence best summarizes a report that found bike lanes increased cycling but had little effect on bus use?", [
                    ("Bike lanes encouraged cycling while bus use stayed similar", True), ("Bike lanes reduced all public transport use", False), ("Bus use caused cycling to rise", False), ("The report measured only walking", False)]),
            ],
            "GRE": [
                ("Although the proposal was initially dismissed as impractical, later evidence made it seem ___. Choose the best completion.", [
                    ("plausible", True), ("irrelevant", False), ("unrelated", False), ("invisible", False)]),
                ("A critic calls a policy ‘unprecedented’. Which meaning best fits the word?", [
                    ("Not done or known before", True), ("Widely disliked", False), ("Carefully measured", False), ("Repeated every year", False)]),
                ("A survey sampled only volunteers from one club. Which concern most limits its conclusions about all students?", [
                    ("The sample may not represent the wider student population", True), ("The survey has too many response options", False), ("Volunteers cannot express preferences", False), ("Clubs never include students", False)]),
                ("If every archived item has a catalog number, and some maps are archived items, what follows?", [
                    ("Some maps have catalog numbers", True), ("Every catalog number belongs to a map", False), ("No maps are archived", False), ("Every map is archived", False)]),
                ("A result is robust because it remains similar under several reasonable assumptions. ‘Robust’ most nearly means:", [
                    ("Resilient", True), ("Unexpected", False), ("Temporary", False), ("Unclear", False)]),
            ],
        }
        for exam_type, items in diagnostic_items.items():
            for text, options in items:
                exists = await session.scalar(
                    select(Question.id).where(
                        Question.exam_type == exam_type,
                        Question.section == "reading",
                        Question.text == text,
                    )
                )
                if not exists:
                    session.add(Question(
                        text=text,
                        exam_type=exam_type,
                        section="reading",
                        question_type="MCQ",
                        difficulty="medium",
                        explanation="Review the key detail in the question and eliminate options that add unsupported claims.",
                        answers=[Answer(text=answer_text, is_correct=is_correct, order=index + 1)
                                 for index, (answer_text, is_correct) in enumerate(options)],
                    ))

        track_result = await session.execute(select(ListeningTrack).limit(1))
        listening_track = track_result.scalar_one_or_none()
        if listening_track:
            questions_result = await session.execute(
                select(Question)
                .where(
                    Question.exam_type == "IELTS",
                    Question.section == "listening",
                    Question.text.in_([
                        "Where can students get help with research?",
                        "How far ahead can students reserve a group study room?",
                    ]),
                )
                .order_by(Question.created_at)
            )
            legacy_questions = questions_result.scalars().all()
            legacy_question_ids = [question.id for question in legacy_questions]
            if legacy_question_ids:
                await session.execute(
                    listening_questions.delete().where(
                        listening_questions.c.track_id == listening_track.id,
                        listening_questions.c.question_id.not_in(legacy_question_ids),
                    )
                )
            linked_result = await session.execute(
                select(listening_questions.c.question_id).where(
                    listening_questions.c.track_id == listening_track.id
                )
            )
            linked_ids = set(linked_result.scalars().all())
            missing_links = [
                {"track_id": listening_track.id, "question_id": question.id}
                for question in legacy_questions
                if question.id not in linked_ids
            ]
            if missing_links:
                await session.execute(insert(listening_questions), missing_links)

        await seed_expanded_content(session)
        await session.commit()


async def _seed_from_environment() -> None:
    from services.api.database import async_session_factory, close_db

    try:
        await seed_learning_content(async_session_factory)
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(_seed_from_environment())
