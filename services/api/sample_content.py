"""Curated, fictional starter content for local exam practice."""

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

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


PASSAGES = [
    {
        "exam": "IELTS", "title": "A second life for old buildings", "difficulty": "medium", "topic": "Architecture",
        "content": "Across many cities, former factories and warehouses are being converted into homes, studios, and public spaces. Reuse can preserve local history and avoid some of the emissions associated with demolition and new construction. It is not always the cheapest option: older structures may need extensive repairs, and their layouts can limit modern uses. Planners therefore compare the carbon saved by retaining a building with the materials and energy needed to adapt it. Successful projects also invite nearby residents to shape how shared areas will be used.",
        "questions": [
            ("What is one potential benefit of adapting an old building?", [("It can preserve local history", True), ("It always costs less than new construction", False), ("It removes the need for repairs", False), ("It guarantees more parking", False)], "The passage says reuse can preserve local history."),
            ("Why do planners compare emissions and adaptation needs?", [("Reuse can have benefits but may require substantial work", True), ("All older buildings have identical layouts", False), ("Residents are not involved in projects", False), ("New construction uses no materials", False)], "The passage describes both avoided construction emissions and the resources needed to adapt a structure."),
        ],
    },
    {
        "exam": "IELTS", "title": "When cities measure street trees", "difficulty": "hard", "topic": "Environment",
        "content": "A city’s tree count offers a simple headline, but it can hide important differences. Young trees may be numerous yet provide little shade, while a smaller number of mature trees can cool busy walking routes. Researchers increasingly map canopy cover alongside heat readings and access to parks. These measures reveal whether benefits reach neighborhoods that need them most. Maintenance matters too: watering during the first summers improves survival, whereas planting without a long-term care plan can produce impressive totals that decline within a few years.",
        "questions": [
            ("Why might a tree count give an incomplete picture?", [("It does not show how much shade trees provide or who can reach it", True), ("It measures neighborhood temperatures directly", False), ("It includes only trees beside parks", False), ("It predicts rainfall exactly", False)], "Counts alone do not capture canopy, cooling, or access."),
            ("What does the passage suggest about maintenance?", [("Long-term care affects whether planting efforts last", True), ("Young trees need no water", False), ("Maintenance is less important than counting", False), ("Trees survive better without a plan", False)], "Watering and care plans improve survival over time."),
        ],
    },
    {
        "exam": "TOEFL", "title": "Why some wetlands return", "difficulty": "medium", "topic": "Ecology",
        "content": "Wetlands can reduce flooding by storing excess rainwater and can provide habitat for birds, fish, and insects. In some regions, restoration teams remove barriers that once diverted water away from marshes. The work is carefully monitored because returning water too quickly may affect nearby farms or roads. Teams track water levels and native plant growth over several seasons. A site is considered promising when it supports more wildlife without creating new risks for people living nearby.",
        "questions": [
            ("What is one purpose of restoring a wetland?", [("To store excess rainwater", True), ("To build a road through a marsh", False), ("To remove all native plants", False), ("To stop monitoring water levels", False)], "Wetlands can store excess rainwater and help reduce flooding."),
            ("Why do teams monitor restoration over several seasons?", [("They need to check ecological results and possible effects on nearby communities", True), ("Plants grow only during one season", False), ("Monitoring replaces the restoration work", False), ("Water levels never change", False)], "The passage says teams track water and plant growth and watch for risks to nearby residents."),
        ],
    },
    {
        "exam": "TOEFL", "title": "The case for quiet study zones", "difficulty": "easy", "topic": "Education",
        "content": "A college library introduced quiet zones after students said that background conversation made it hard to concentrate. The change did not remove group study rooms; instead, signs helped visitors choose spaces suited to their work. A short survey later found that students used both areas, often moving between them during a study session. Library staff concluded that clear choices were more useful than asking every visitor to follow one rule throughout the building.",
        "questions": [
            ("What prompted the library to create quiet zones?", [("Students reported difficulty concentrating", True), ("The group rooms were removed", False), ("Staff wanted shorter opening hours", False), ("A survey ended library use", False)], "Student feedback about concentration prompted the change."),
            ("What conclusion did library staff reach?", [("Different spaces can support different kinds of study", True), ("All students prefer complete silence", False), ("Group study should be prohibited", False), ("Signs prevent students from moving", False)], "Students used both zones, so the library provided choices."),
        ],
    },
    {
        "exam": "GRE", "title": "The value of a failed field trial", "difficulty": "hard", "topic": "Research methods",
        "content": "An urban farming project found that its first low-cost irrigation design distributed water unevenly. The team could have discarded the trial as a failure; instead, it treated the variation as evidence. Soil sensors showed that pressure dropped at the far end of the system, a pattern that had been masked by earlier visual inspections. A revised layout improved consistency, but the researchers cautioned that a single season could not establish how the design would perform under different weather conditions.",
        "questions": [
            ("What did the first trial reveal?", [("Water pressure decreased toward the end of the system", True), ("Visual inspections measured pressure precisely", False), ("The revised design worked in every climate", False), ("Soil sensors were unnecessary", False)], "Sensors identified a pressure drop at the far end."),
            ("Why did the researchers qualify their conclusion?", [("The design had been tested for only one season", True), ("The first trial had no variation", False), ("The sensors measured weather alone", False), ("The project had no revised layout", False)], "They said one season could not show performance across different weather conditions."),
        ],
    },
    {
        "exam": "GRE", "title": "A more careful measure of innovation", "difficulty": "medium", "topic": "Public policy",
        "content": "Patent totals are often used as a proxy for innovation, yet the measure rewards the quantity of applications rather than their eventual influence. Some inventions generate many follow-up patents while changing few daily practices; others spread widely without producing a large patent trail. A policy institute therefore compared filings with adoption rates and independent assessments of practical impact. Its report did not dismiss patent data, but argued that a single indicator can distort funding decisions when treated as a complete account of progress.",
        "questions": [
            ("What limitation of patent totals does the passage identify?", [("They measure applications more directly than practical influence", True), ("They never include useful inventions", False), ("They show adoption rates without analysis", False), ("They are unrelated to innovation", False)], "Patent counts track filings, not necessarily the impact of inventions."),
            ("What is the institute's position on patent data?", [("It can be useful but should not stand alone", True), ("It should be removed from every analysis", False), ("It is a perfect measure of progress", False), ("It should determine all funding", False)], "The report keeps patent data but recommends other measures too."),
        ],
    },
]


LISTENING = [
    {
        "exam": "IELTS", "title": "Calling the community garden", "difficulty": "easy", "topic": "Community life", "accent": "British", "duration": 55,
        "transcript": "Hello, this is Mina from the Riverside Community Garden. Saturday's volunteer session will begin at nine thirty, not nine, because the tool delivery is arriving later. Please meet beside the greenhouse entrance. We will plant herbs in the north beds and finish with a short safety demonstration. Gloves are available, but bring a water bottle. If it rains heavily, the session will move to Sunday morning and we will send a message by Friday evening.",
        "questions": [
            ("What time does the volunteer session begin?", [("9:30", True), ("9:00", False), ("Friday evening", False), ("Sunday afternoon", False)], "The speaker corrects the start time to nine thirty."),
            ("Where should volunteers meet?", [("Beside the greenhouse entrance", True), ("At the north gate", False), ("Inside the tool shed", False), ("At the river bridge", False)], "Volunteers are asked to meet beside the greenhouse entrance."),
        ],
    },
    {
        "exam": "TOEFL", "title": "Office hours and a research paper", "difficulty": "medium", "topic": "Campus life", "accent": "North American", "duration": 64,
        "transcript": "Hi, Professor Lee. I'm calling about the research paper. I have finished the source list, but I am not sure whether the charts belong in the appendix. Professor Lee says to include one chart in the main section because it supports the central comparison, and put the remaining charts in the appendix. She will be available during office hours on Wednesday from two until four, in room 318. Students who cannot attend may email a draft question before Tuesday evening.",
        "questions": [
            ("Where should the student place the chart that supports the main comparison?", [("In the main section", True), ("Only in the appendix", False), ("In the source list", False), ("In an email", False)], "The professor says the key chart belongs in the main section."),
            ("When are the professor's office hours?", [("Wednesday, 2 to 4", True), ("Tuesday evening", False), ("Wednesday, 4 to 6", False), ("Monday morning", False)], "The professor is available Wednesday from two until four."),
        ],
    },
    {
        "exam": "GRE", "title": "A research seminar announcement", "difficulty": "hard", "topic": "Academic life", "accent": "North American", "duration": 58,
        "transcript": "The department's methods seminar has moved from Thursday to Friday this week. It will still meet at eleven, but in the smaller room 204 because the main hall is being repaired. The guest speaker will discuss how researchers distinguish correlation from causation in long-term studies. Registered participants should download the two-page data summary beforehand. No prior statistics course is required; the opening section will review the terminology.",
        "questions": [
            ("What changed about the seminar?", [("Its day and room", True), ("Its speaker and topic", False), ("Its start time and length", False), ("Its registration requirement", False)], "The seminar moved from Thursday to Friday and to room 204."),
            ("What should registered participants do in advance?", [("Download the data summary", True), ("Complete a statistics course", False), ("Reserve the main hall", False), ("Prepare a guest lecture", False)], "Participants are asked to download a two-page summary."),
        ],
    },
]


VOCABULARY = [
    ("advocate", "IELTS", "verb", "To publicly support or recommend a policy or action.", "The report advocates adding more shaded seating near bus stops.", ["support", "promote"], "intermediate"),
    ("consecutive", "IELTS", "adjective", "Following one after another without interruption.", "The center was fully booked on three consecutive weekends.", ["successive", "continuous"], "intermediate"),
    ("deteriorate", "IELTS", "verb", "To become worse in quality or condition.", "Without repairs, the footpath may deteriorate during winter.", ["decline", "worsen"], "advanced"),
    ("feasible", "IELTS", "adjective", "Possible and practical to carry out.", "A later bus may be feasible if enough residents use it.", ["practicable", "workable"], "intermediate"),
    ("ambiguous", "TOEFL", "adjective", "Having more than one possible meaning; unclear.", "The instructions were ambiguous, so students asked for an example.", ["unclear", "equivocal"], "intermediate"),
    ("compile", "TOEFL", "verb", "To collect information and arrange it into a list or report.", "The research team compiled survey results from six campuses.", ["assemble", "gather"], "easy"),
    ("derive", "TOEFL", "verb", "To obtain something from a source or process.", "The estimate was derived from measurements taken each month.", ["obtain", "infer"], "intermediate"),
    ("retain", "TOEFL", "verb", "To keep or continue to have something.", "The revised course helped students retain key terminology.", ["keep", "preserve"], "easy"),
    ("equivocal", "GRE", "adjective", "Open to multiple interpretations; deliberately uncertain.", "The evidence was equivocal, so the authors avoided a firm conclusion.", ["ambiguous", "uncertain"], "advanced"),
    ("mitigate", "GRE", "verb", "To make a harmful effect less severe.", "Tree cover can mitigate the heat experienced by pedestrians.", ["alleviate", "lessen"], "advanced"),
    ("salient", "GRE", "adjective", "Most noticeable or important in a particular situation.", "The most salient finding was the gap between access and use.", ["prominent", "notable"], "advanced"),
    ("substantiate", "GRE", "verb", "To support a claim with evidence.", "The author used several data sets to substantiate the claim.", ["verify", "corroborate"], "advanced"),
]


GRAMMAR = [
    ("Subject–verb agreement", "Match the verb to the subject, even when extra phrases separate them.", "The list of recommended sources is available online.", "is", "The head noun 'list' is singular, so it takes 'is'.", "Find the main subject before choosing the verb.", "IELTS", "easy"),
    ("Present perfect for continuing situations", "Use the present perfect for a situation that began in the past and continues now.", "The university ___ (offer) evening classes since 2018.", "has offered", "'Since 2018' links a past starting point to the present.", "Look for 'since' and ask whether the situation continues.", "TOEFL", "intermediate"),
    ("Parallel structure", "Keep items in a list in the same grammatical form.", "The course teaches students to analyze data, write clearly, and ___ (present) findings.", "present", "The infinitive 'to' governs the parallel verbs analyze, write, and present.", "Compare the form of each item in the list.", "GRE", "intermediate"),
    ("Conditional sentences", "Use a consistent conditional pattern to connect a condition with its likely result.", "If the sample ___ (include) more rural participants, the results might differ.", "included", "A hypothetical condition uses the past form with 'might' in the result clause.", "Notice the modal 'might' in the result.", "GRE", "advanced"),
    ("Relative clauses", "Use a relative pronoun to add information about a noun.", "The archive, ___ opened last year, contains maps from the 1800s.", "which was", "The non-defining clause describes the archive and requires a finite verb.", "The commas signal extra information about a thing.", "TOEFL", "intermediate"),
    ("Articles with general and specific nouns", "Use 'a' for a nonspecific singular count noun and 'the' for a specific one.", "Researchers developed ___ method and later tested the method with volunteers.", "a", "The method is introduced for the first time, so use 'a'.", "Is the reader hearing about this method for the first time?", "IELTS", "easy"),
]


async def _question(session: AsyncSession, exam: str, section: str, text: str, options: list, explanation: str) -> Question:
    found = await session.scalar(select(Question).where(Question.exam_type == exam, Question.section == section, Question.text == text))
    if found:
        return found
    item = Question(text=text, exam_type=exam, section=section, question_type="MCQ", difficulty="medium", explanation=explanation, answers=[Answer(text=label, is_correct=correct, order=index + 1) for index, (label, correct) in enumerate(options)])
    session.add(item)
    await session.flush()
    return item


async def seed_expanded_content(session: AsyncSession) -> None:
    """Append missing curated examples without replacing learner data or existing samples."""
    for item in PASSAGES:
        passage = await session.scalar(select(Passage).where(Passage.title == item["title"]))
        if not passage:
            passage = Passage(title=item["title"], content=item["content"], word_count=len(item["content"].split()), exam_type=item["exam"], difficulty=item["difficulty"], topic=item["topic"], source="Studywell practice sample", time_limit=900)
            session.add(passage)
            await session.flush()
        linked = set((await session.execute(select(passage_questions.c.question_id).where(passage_questions.c.passage_id == passage.id))).scalars().all())
        for text, options, explanation in item["questions"]:
            question = await _question(session, item["exam"], "reading", text, options, explanation)
            if question.id not in linked:
                await session.execute(insert(passage_questions).values(passage_id=passage.id, question_id=question.id))
                linked.add(question.id)

    for item in LISTENING:
        track = await session.scalar(select(ListeningTrack).where(ListeningTrack.title == item["title"]))
        if not track:
            track = ListeningTrack(title=item["title"], audio_url="", duration=item["duration"], transcript=item["transcript"], exam_type=item["exam"], difficulty=item["difficulty"], topic=item["topic"], source="Studywell practice sample", accent=item["accent"])
            session.add(track)
            await session.flush()
        linked = set((await session.execute(select(listening_questions.c.question_id).where(listening_questions.c.track_id == track.id))).scalars().all())
        for text, options, explanation in item["questions"]:
            question = await _question(session, item["exam"], "listening", text, options, explanation)
            if question.id not in linked:
                await session.execute(insert(listening_questions).values(track_id=track.id, question_id=question.id))
                linked.add(question.id)

    for word, exam, part, definition, example, synonyms, difficulty in VOCABULARY:
        exists = await session.scalar(select(VocabularyWord.id).where(VocabularyWord.word == word))
        if not exists:
            session.add(VocabularyWord(word=word, definition=definition, part_of_speech=part, examples=[example], synonyms=synonyms, exam_type=exam, difficulty=difficulty, frequency=5, source="Studywell practice sample"))

    for order, (name, description, sentence, correct, explanation, hint, exam, difficulty) in enumerate(GRAMMAR, start=2):
        topic = await session.scalar(select(GrammarTopic).where(GrammarTopic.topic_name == name))
        if not topic:
            topic = GrammarTopic(topic_name=name, description=description, explanation=description, examples=[sentence], exam_type=exam, difficulty=difficulty, order=order)
            session.add(topic)
            await session.flush()
            session.add(GrammarExercise(topic_id=topic.id, sentence=sentence, correct_form=correct, explanation=explanation, difficulty=difficulty, hint=hint))

    from services.api.bulk_content import seed_bulk_examples
    await seed_bulk_examples(session)
