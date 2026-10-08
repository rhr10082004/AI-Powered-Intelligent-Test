"""Deterministic local practice-bank expansion for the three supported exams."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.models_phase2_isolated import (
    Answer, GrammarExercise, GrammarTopic, ListeningTrack, Passage, Question,
    VocabularyWord, listening_questions, passage_questions,
)


READING_CONTEXTS = [
    ("urban gardens", "unused rooftops", "food access", "shared growing beds", "seasonal harvest weights", "harvests increased after volunteers received short training", "the trial covered one growing season", "repeat the trial through winter"),
    ("campus libraries", "evening crowding", "study-space access", "a reservation board", "seat availability each hour", "students found open seats faster", "the survey included only first-year students", "invite more year groups"),
    ("coastal towns", "shoreline erosion", "habitat protection", "native dune plants", "sand movement after storms", "planted areas retained more sand", "storm strength varied between sites", "monitor the coast for several years"),
    ("public clinics", "missed appointments", "health-service access", "text reminders", "attendance across appointment types", "reminders were most useful for morning visits", "some patients changed phone numbers", "offer a second contact method"),
    ("regional buses", "unreliable transfers", "commute times", "coordinated departure times", "transfer waits at busy stops", "average waits fell on weekdays", "weekend routes were not included", "extend measurement to weekends"),
    ("community colleges", "course-material costs", "student participation", "open digital textbooks", "course completion rates", "more students opened the assigned readings", "completion depended on several other factors", "compare outcomes across more subjects"),
    ("museum teams", "uneven visitor flow", "gallery access", "timed entry windows", "queue length by gallery", "queues shortened near popular exhibits", "visitor numbers changed by season", "repeat observations in summer"),
    ("small farms", "water use during dry months", "crop resilience", "soil-moisture sensors", "water use per field", "farmers reduced unnecessary irrigation", "sensor costs differed by farm size", "test lower-cost equipment"),
    ("neighborhood councils", "low turnout at meetings", "resident participation", "rotating meeting locations", "attendance by district", "attendance rose in districts hosting a meeting", "online participation was not measured", "include remote attendance next time"),
    ("science classes", "difficulty interpreting charts", "student confidence", "weekly data discussions", "accuracy on chart questions", "students improved at identifying trends", "the classes used the same teacher", "compare more teaching groups"),
    ("city maintenance crews", "delayed sidewalk repairs", "pedestrian safety", "a public issue map", "time from report to repair", "simple repairs were completed sooner", "complex jobs still required inspections", "separate urgent and routine requests"),
    ("language centers", "low speaking confidence", "class participation", "paired discussion warmups", "voluntary speaking turns", "more learners contributed during the lesson", "the study did not measure long-term fluency", "follow learners into the next term"),
    ("regional parks", "litter near trail entrances", "visitor experience", "clearly marked return bins", "litter counts along each trail", "entrances with signs had fewer discarded bottles", "weather affected weekend visits", "repeat counts in different seasons"),
    ("energy cooperatives", "high household demand at dusk", "electricity reliability", "shared battery storage", "peak-hour demand", "stored power covered short demand spikes", "the analysis used a mild winter", "model a colder season"),
    ("local archives", "fragile paper collections", "document preservation", "digital scanning stations", "page handling during research visits", "staff reported less handling of originals", "not every document could be scanned", "prioritize frequently requested items"),
    ("public art programs", "limited access to exhibitions", "arts participation", "temporary outdoor displays", "visitor counts by neighborhood", "more residents encountered the displays", "counts do not show how visitors felt", "pair attendance with short interviews"),
    ("school cafeterias", "avoidable food waste", "meal planning", "smaller first servings", "uneaten food by meal period", "waste fell while students could request seconds", "the menu changed during the trial", "repeat the measure with a stable menu"),
    ("water utilities", "hard-to-detect pipe leaks", "water conservation", "night-flow monitoring", "water loss before and after repairs", "several hidden leaks were found", "older meters produced uncertain readings", "replace meters before expanding"),
    ("research laboratories", "inconsistent sample labeling", "data quality", "standardized digital labels", "label corrections per week", "corrections declined after adoption", "the comparison involved one laboratory", "replicate in other departments"),
    ("community theaters", "unused rehearsal hours", "facility access", "shared online calendars", "room conflicts each month", "double bookings became less common", "last-minute changes still occurred", "add a simple change-notification step"),
]

LISTENING_CONTEXTS = [
    ("library workshop", "Room 214", "Tuesday at 10:30", "bring a notebook", "the event moves to Thursday if the speaker is delayed"),
    ("campus garden", "the east greenhouse", "Saturday at 9:15", "bring a water bottle", "the session moves indoors if it rains"),
    ("writing center", "the second-floor desk", "Wednesday at 14:00", "bring a draft paragraph", "students can book another slot online"),
    ("science museum", "the north entrance", "Sunday at 11:00", "bring the confirmation email", "late arrivals join the next tour"),
    ("language exchange", "the student union lounge", "Friday at 16:30", "bring one discussion question", "the group changes tables after the first activity"),
    ("research seminar", "lecture room 108", "Monday at 13:00", "download the short reading", "the recording is posted the following day"),
    ("career advice session", "the careers office", "Thursday at 15:45", "bring a current resume", "walk-ins are accepted after registered guests"),
    ("community clean-up", "the riverside gate", "Saturday at 8:40", "wear closed-toe shoes", "the backup date is the next Sunday"),
    ("music practice group", "Studio B", "Tuesday at 18:20", "bring headphones", "the room is unavailable during the final week"),
    ("student council meeting", "the west conference room", "Wednesday at 12:10", "read the agenda beforehand", "members can send comments by email"),
    ("history talk", "the archive reading room", "Friday at 17:00", "show a campus identification card", "seating is limited to the first thirty guests"),
    ("health information session", "the clinic classroom", "Monday at 9:50", "bring a list of questions", "the handout is available in large print"),
    ("public speaking practice", "the media lab", "Thursday at 17:30", "prepare a one-minute introduction", "participants may observe without presenting"),
    ("walking tour", "the clock tower steps", "Sunday at 10:20", "wear comfortable shoes", "the route is shortened during hot weather"),
    ("data skills class", "computer lab 3", "Tuesday at 11:45", "bring your student login", "a second class is offered next week"),
    ("volunteer orientation", "the main reception desk", "Saturday at 13:15", "bring a photo identification card", "training materials are emailed afterward"),
    ("film discussion", "the arts building lounge", "Friday at 19:10", "watch the short film in advance", "the discussion starts fifteen minutes after screening"),
    ("open lecture", "the auditorium balcony", "Wednesday at 16:05", "arrive ten minutes early", "questions can be submitted on paper"),
    ("exam study group", "the quiet floor meeting room", "Monday at 18:35", "bring one practice question", "the group finishes promptly at seven"),
    ("local history walk", "the old station entrance", "Sunday at 14:25", "check the route map first", "the walk is postponed during severe weather"),
]


VOCABULARY_BANK = [
    ("abundant","adjective","Existing in large quantities","plentiful"),("accurate","adjective","Correct and free from significant error","precise"),("adapt","verb","Change something to suit new conditions","adjust"),("adequate","adjective","Enough for a particular purpose","sufficient"),("adjacent","adjective","Located next to or very near something","neighboring"),("administer","verb","Manage or direct a process or organization","oversee"),("alter","verb","Make a change to something","modify"),("alternative","noun","Another available choice","option"),("analyze","verb","Examine information methodically","inspect"),("annual","adjective","Happening once every year","yearly"),
    ("anticipate","verb","Expect something and prepare for it","foresee"),("apparent","adjective","Easy to notice or understand","evident"),("approximate","adjective","Close to a value but not exact","estimated"),("aspect","noun","One particular part or feature","dimension"),("assemble","verb","Bring separate parts together","gather"),("assess","verb","Judge the quality or importance of something","evaluate"),("assign","verb","Give a task or responsibility to someone","allocate"),("attain","verb","Succeed in reaching a goal","achieve"),("available","adjective","Ready for use or able to be obtained","accessible"),("aware","adjective","Having knowledge of a situation","conscious"),
    ("brief","adjective","Short in duration or length","concise"),("capacity","noun","The ability or amount something can contain","volume"),("category","noun","A group of things with shared features","class"),("cease","verb","Bring an activity or process to an end","stop"),("clarify","verb","Make an idea easier to understand","explain"),("coherent","adjective","Logical and easy to follow","consistent"),("coincide","verb","Happen at the same time or correspond","align"),("colleague","noun","A person who works with another","coworker"),("commence","verb","Begin an activity or process","start"),("complex","adjective","Made of several connected parts","complicated"),
    ("comprehensive","adjective","Including nearly all relevant details","complete"),("concentrate","verb","Give focused attention to something","focus"),("conclude","verb","Reach a decision after considering evidence","infer"),("conduct","verb","Organize and carry out an activity","perform"),("confirm","verb","Establish that something is true","verify"),("conflict","noun","A serious disagreement or incompatibility","dispute"),("consequent","adjective","Happening as a result of something","resulting"),("considerable","adjective","Large enough to be important","substantial"),("consistent","adjective","Remaining similar across situations or time","steady"),("construct","verb","Build or form something","create"),
    ("consume","verb","Use a resource or supply","expend"),("context","noun","The circumstances surrounding an event or idea","setting"),("contradict","verb","State the opposite of a claim","oppose"),("contribute","verb","Help bring about a result","add"),("conventional","adjective","Following commonly accepted practice","traditional"),("convert","verb","Change something into a different form","transform"),("crucial","adjective","Extremely important to an outcome","essential"),("decline","verb","Become smaller, weaker, or less common","decrease"),("demonstrate","verb","Show clearly by evidence or example","illustrate"),("denote","verb","Mean or indicate a particular thing","signify"),
    ("detect","verb","Discover something that is difficult to notice","identify"),("distinct","adjective","Clearly different from other things","separate"),("distribute","verb","Give or deliver things across a group","allocate"),("diverse","adjective","Including a range of different types","varied"),("domestic","adjective","Relating to a home or one country","household"),("dominate","verb","Have the greatest influence or control","prevail"),("duration","noun","The length of time something continues","period"),("dynamic","adjective","Characterized by ongoing activity or change","active"),("emerge","verb","Become visible or begin to exist","appear"),("emphasis","noun","Special importance given to an idea","stress"),
    ("enable","verb","Make it possible for someone to do something","allow"),("encounter","verb","Meet or experience something","face"),("enhance","verb","Improve the quality or value of something","improve"),("ensure","verb","Make certain that something happens","guarantee"),("establish","verb","Set up or prove something firmly","found"),("estimate","verb","Make an approximate calculation or judgment","assess"),("evident","adjective","Clear from the available facts","obvious"),("evolve","verb","Develop gradually over time","change"),("exceed","verb","Be greater than a limit or amount","surpass"),("exclude","verb","Leave something or someone out","omit"),
    ("expand","verb","Become larger or make something larger","extend"),("explicit","adjective","Stated clearly and directly","specific"),("exploit","verb","Make full use of a resource or opportunity","utilize"),("facilitate","verb","Make an action or process easier","assist"),("feature","noun","A notable part or characteristic","attribute"),("fluctuate","verb","Rise and fall irregularly","vary"),("focus","noun","The central point of attention","emphasis"),("function","noun","The purpose or activity of something","role"),("fundamental","adjective","Forming a necessary basis","basic"),("generate","verb","Produce or create something","produce"),
    ("goal","noun","An outcome that someone aims to achieve","aim"),("grant","verb","Give or allow something formally","award"),("identify","verb","Recognize or establish what something is","detect"),("illustrate","verb","Explain an idea with examples","demonstrate"),("impact","noun","A strong effect or influence","effect"),("implement","verb","Put a plan or decision into effect","apply"),("imply","verb","Suggest something without stating it directly","indicate"),("impose","verb","Force a rule or burden onto someone","enforce"),("incentive","noun","Something that encourages an action","motivation"),("indicate","verb","Point out or show a fact","signal"),
    ("individual","noun","One person considered separately","person"),("infer","verb","Reach a conclusion from available evidence","deduce"),("initial","adjective","Existing or occurring at the beginning","first"),("instance","noun","A particular example of something","case"),("interact","verb","Act or communicate with one another","engage"),("interpret","verb","Explain the meaning of information","understand"),("interval","noun","A period or space between events","gap"),("involve","verb","Include something as a necessary part","entail"),("justify","verb","Give reasons that support a decision","defend"),("maintain","verb","Keep something at the same level or condition","preserve"),
    ("major","adjective","Important or greater in size or degree","significant"),("method","noun","A planned way of doing something","approach"),("migrate","verb","Move from one place or system to another","relocate"),("minimum","noun","The smallest amount that is possible or required","least"),("modify","verb","Change something without replacing it completely","adjust"),("monitor","verb","Observe something over a period of time","track"),("motivate","verb","Give someone a reason to act","encourage"),("obtain","verb","Get or acquire something","secure"),("obvious","adjective","Easy to see or understand","apparent"),("occur","verb","Happen or take place","arise"),
    ("outcome","noun","The result of an action or process","result"),("participate","verb","Take part in an activity","engage"),("perceive","verb","Notice or understand something","recognize"),("persist","verb","Continue despite difficulty","endure"),("perspective","noun","A particular way of viewing something","viewpoint"),("phase","noun","One stage in a process","stage"),("policy","noun","A course of action adopted by a group","plan"),("precise","adjective","Exact and carefully stated","accurate"),("predict","verb","Say what is likely to happen","forecast"),("previous","adjective","Existing or happening before something else","prior"),
    ("primary","adjective","Most important or occurring first","main"),("principle","noun","A basic rule or belief","standard"),("proceed","verb","Continue or begin moving forward","continue"),("process","noun","A series of steps toward a result","procedure"),("require","verb","Need something as necessary","demand"),("research","noun","Careful study to discover information","investigation"),("respond","verb","React or give an answer","reply"),("restrict","verb","Limit the size or range of something","constrain"),("reveal","verb","Make something known or visible","disclose"),("role","noun","The function or part played by someone","function"),
    ("select","verb","Choose something from available options","choose"),("sequence","noun","A set of things in a particular order","series"),("significant","adjective","Important enough to deserve attention","notable"),("similar","adjective","Having features in common","alike"),("source","noun","A place or person from which something comes","origin"),("specific","adjective","Clearly defined and particular","precise"),("strategy","noun","A plan designed to reach a goal","approach"),("structure","noun","The way parts are arranged together","organization"),("submit","verb","Present work for consideration","present"),("sufficient","adjective","As much as is needed","adequate"),
    ("survey","noun","A set of questions used to gather information","questionnaire"),("task","noun","A piece of work that must be completed","assignment"),("technique","noun","A particular way of doing something","method"),("theory","noun","A set of ideas explaining observations","model"),("topic","noun","The subject being discussed or studied","subject"),("transfer","verb","Move something from one place to another","shift"),("trend","noun","A general direction of change","pattern"),("valid","adjective","Well-founded and supported by sound reasoning","sound"),("vary","verb","Change or differ across examples","differ"),("verify","verb","Check that information is accurate","confirm"),
    ("allocate","verb","Distribute resources for a particular purpose","assign"),("empirical","adjective","Based on observation or experiment","observed"),("feasible","adjective","Possible and practical to carry out","workable"),("hypothesis","noun","A proposed explanation to be tested","proposition"),("inevitable","adjective","Certain to happen and difficult to avoid","unavoidable"),("mitigate","verb","Make a harmful effect less severe","reduce"),("objective","noun","A result someone plans to achieve","goal"),("reliable","adjective","Consistently dependable or trustworthy","dependable"),("relevant","adjective","Closely connected to the matter in question","pertinent"),("sustain","verb","Keep something going over time","maintain"),
]

VERB_EXAMPLES = {
    "cease": "The interruption ceased after the repair was completed.",
    "coincide": "The two measurements coincide with the start of the review period.",
    "concentrate": "The research team concentrated on the most relevant findings.",
    "contribute": "Several factors contribute to the final outcome.",
    "decline": "Attendance declined during the examination period.",
    "emerge": "New patterns emerged after the second review.",
    "evolve": "The research question evolved as more evidence became available.",
    "fluctuate": "Daily readings fluctuated throughout the observation period.",
    "interact": "The two variables interact in the final model.",
    "migrate": "Several species migrate when local temperatures change.",
    "occur": "Errors may occur when labels are entered too quickly.",
    "participate": "Students participate in a weekly review session.",
    "persist": "The effect persisted across several review periods.",
    "proceed": "The project proceeded after the panel approved the plan.",
    "respond": "Students responded to the feedback with a revised draft.",
    "vary": "Results varied across the three study groups.",
}


GRAMMAR_RULES = [
    ("Subject and verb agreement", "Choose a verb that agrees with the main subject", "The {subject} of the report ___ (be) available online.", "is", "The main subject is singular."),
    ("Past perfect", "Use the past perfect for an action completed before another past event", "By the time the review began, the team ___ (finish) the survey.", "had finished", "The survey was already complete when the review began."),
    ("Present perfect", "Use the present perfect for an action that continues or matters now", "The center ___ (offer) evening classes since {year}.", "has offered", "'Since' marks a period continuing to the present."),
    ("Passive voice", "Use a form of be with a past participle when the action matters most", "The final measurements ___ (record) by two independent observers.", "were recorded", "The plural measurements receive the action."),
    ("Conditional clauses", "Use a past form for a hypothetical condition about the present", "If the study ___ (include) more sites, its conclusion might change.", "included", "A hypothetical condition pairs a past form with 'might'."),
    ("Parallel structure", "Keep connected list items in the same grammatical form", "The course teaches students to compare evidence, ___ (summarize) results, and present findings.", "summarize", "The verbs share the infinitive 'to'."),
    ("Relative clauses", "Use a relative pronoun that refers clearly to the noun", "The archive, ___ (which) opened last year, contains local maps.", "which", "'Which' refers to the archive, a thing."),
    ("Comparative adjectives", "Use the comparative form when comparing two things", "The revised process is ___ (efficient) than the original one.", "more efficient", "A multi-syllable adjective uses 'more' for comparison."),
    ("Modal verbs", "Use a modal to express advice, possibility, or obligation", "Students ___ (should) check the source before citing it.", "should", "'Should' gives advice."),
    ("Prepositions in academic phrases", "Learn common prepositions used with academic verbs and adjectives", "The findings are consistent ___ (preposition) earlier observations.", "with", "The standard phrase is 'consistent with'."),
    ("Articles", "Use an article that fits whether a singular noun is new or already known", "Researchers proposed ___ (a/an) alternative explanation.", "an", "'Alternative' begins with a vowel sound."),
    ("Count and noncount nouns", "Use a quantifier that matches the noun type", "The report provides several useful ___ (piece) of evidence.", "pieces", "'Piece' is countable; 'evidence' is noncount."),
    ("Reported speech", "Shift tense appropriately when reporting a past statement", "The lecturer said that the results ___ (be) preliminary.", "were", "The reporting verb is past, so the statement shifts to past."),
    ("Gerunds after prepositions", "Use a gerund after a preposition", "The team improved accuracy by ___ (check) each label twice.", "checking", "A verb after 'by' takes the -ing form."),
    ("Infinitives of purpose", "Use an infinitive to explain why an action is done", "The team repeated the measurement ___ (confirm) the pattern.", "to confirm", "The infinitive explains the purpose of repeating."),
    ("Adverb placement", "Place an adverb where it clearly modifies the intended verb", "The data were ___ (careful) reviewed before publication.", "carefully", "An adverb modifies the verb 'reviewed'."),
    ("Noun clauses", "Use a statement word order inside an indirect question", "The analyst explained why the first estimate ___ (change).", "changed", "An indirect question uses statement word order."),
    ("Punctuation in non-defining clauses", "Use commas around extra information that is not needed to identify a noun", "The main library, ___ (which) was renovated recently, stays open late.", "which", "The commas mark optional information about the library."),
    ("Uncountable academic nouns", "Avoid plural forms for uncountable nouns", "The new ___ (equip) is available to all research groups.", "equipment", "'Equipment' is uncountable and takes a singular verb."),
    ("Conjunctive adverbs", "Use punctuation around a conjunctive adverb joining complete ideas", "The sample was small; ___ (however), the pattern was consistent.", "however", "A semicolon can precede a conjunctive adverb."),
]


def _reading_item(index: int) -> dict:
    context = READING_CONTEXTS[(index - 1) % len(READING_CONTEXTS)]
    setting, issue, goal, intervention, measure, finding, limitation, next_step = context
    variant = (index - 1) // len(READING_CONTEXTS) + 1
    follow_up_details = [
        "A second observation was collected after the first week to check whether the effect lasted.",
        "Participants also recorded one barrier they had not expected at the start of the project.",
        "The team compared comments from new participants with comments from returning participants.",
        "A small change to the schedule was documented so later teams could repeat the process.",
        "The report included the original measurements as well as the final average.",
    ]
    title = f"{setting.title()}: practice study {variant}"
    content = (
        f"A local project examined {issue} in {setting}. The team asked how to improve {goal} without adding avoidable cost. "
        f"During a {6 + (variant % 5)}-week pilot, staff compared {intervention} with the previous arrangement. They recorded {measure} at regular intervals and collected comments from participants. "
        f"The results suggested that {finding}. The team did not treat the finding as a universal rule: {limitation}. "
        f"{follow_up_details[(variant - 1) % len(follow_up_details)]} "
        f"The report recommends that future projects {next_step}. It also argues that clear measurement plans make it easier to distinguish a promising early result from a lasting improvement. "
        f"For that reason, the researchers plan to publish the next set of observations alongside the original figures, including results that do not match their initial expectations."
    )
    exam = ("IELTS", "TOEFL", "GRE")[(index - 1) % 3]
    return {"title": title, "content": content, "word_count": len(content.split()), "exam": exam, "topic": setting.title(), "difficulty": ("easy", "medium", "hard")[(index - 1) % 3], "intervention": intervention, "limitation": limitation, "next_step": next_step}


async def _add_question(session: AsyncSession, exam: str, section: str, text: str, options: list[tuple[str, bool]], explanation: str) -> Question:
    found = await session.scalar(select(Question).where(Question.exam_type == exam, Question.section == section, Question.text == text))
    if found:
        return found
    question = Question(text=text, exam_type=exam, section=section, question_type="MCQ", difficulty="medium", explanation=explanation, source="Studywell generated practice sample", answers=[Answer(text=value, is_correct=correct, order=position + 1) for position, (value, correct) in enumerate(options)])
    session.add(question)
    await session.flush()
    return question


async def seed_bulk_examples(session: AsyncSession) -> None:
    """Ensure 100+ examples in each core skill bank, without duplicating rows."""
    for index in range(1, 101):
        item = _reading_item(index)
        passage = await session.scalar(select(Passage).where(Passage.title == item["title"]))
        if not passage:
            passage = Passage(title=item["title"], content=item["content"], word_count=item["word_count"], exam_type=item["exam"], difficulty=item["difficulty"], topic=item["topic"], source="Studywell generated practice sample", time_limit=900)
            session.add(passage)
            await session.flush()
        else:
            passage.content = item["content"]
            passage.word_count = item["word_count"]
        linked_ids = set((await session.execute(select(passage_questions.c.question_id).where(passage_questions.c.passage_id == passage.id))).scalars().all())
        q1 = await _add_question(session, item["exam"], "reading", f"In '{item['title']}', what did the team test?", [(item["intervention"], True), ("A new admissions policy", False), ("A change to exam scoring", False), ("A measure of staff attendance", False)], "The passage names the pilot intervention directly.")
        q2 = await _add_question(session, item["exam"], "reading", f"Why did the researchers recommend another stage for '{item['title']}'?", [(item["limitation"], True), ("The original project had no measurements", False), ("Participants refused to comment", False), ("The intervention could not be described", False)], "The authors caution that the early result has a stated limitation.")
        q3 = await _add_question(session, item["exam"], "reading", f"What next step did the report propose for '{item['title']}'?", [(item["next_step"], True), ("Stop collecting measurements immediately", False), ("Remove every participant comment", False), ("Replace the project with an exam", False)], "The final paragraph identifies a next step for future study.")
        for question in (q1, q2, q3):
            if question.id not in linked_ids:
                await session.execute(passage_questions.insert().values(passage_id=passage.id, question_id=question.id))
                linked_ids.add(question.id)

    for index in range(1, 101):
        event, place, time, bring, contingency = LISTENING_CONTEXTS[(index - 1) % len(LISTENING_CONTEXTS)]
        variant = (index - 1) // len(LISTENING_CONTEXTS) + 1
        day, clock = time.split(" at ")
        hour, minute = (int(part) for part in clock.split(":"))
        shifted_minutes = hour * 60 + minute + (variant - 1) * 15
        time = f"{day} at {(shifted_minutes // 60) % 24:02d}:{shifted_minutes % 60:02d}"
        title = f"{event.title()} announcement {variant}"
        transcript = (f"Hello, this is a reminder about the {event}. We will meet at {place} on {time}. Please {bring}. "
                      f"The organizer will check names at the door and give everyone a short schedule. The main activity begins five minutes after the stated meeting time, so please arrive promptly. "
                      f"{contingency.capitalize()}. If you can no longer attend, let the office know so another participant can use your place. A summary and any handouts will be sent to registered participants afterward.")
        exam = ("IELTS", "TOEFL", "GRE")[(index - 1) % 3]
        track = await session.scalar(select(ListeningTrack).where(ListeningTrack.title == title))
        if not track:
            track = ListeningTrack(title=title, audio_url="", duration=55 + index % 45, transcript=transcript, exam_type=exam, difficulty=("easy", "medium", "hard")[(index - 1) % 3], topic=event.title(), source="Studywell generated practice sample", accent=("British", "North American", "Australian")[(index - 1) % 3])
            session.add(track)
            await session.flush()
        else:
            track.transcript = transcript
        linked_ids = set((await session.execute(select(listening_questions.c.question_id).where(listening_questions.c.track_id == track.id))).scalars().all())
        q1 = await _add_question(session, exam, "listening", f"Where should participants meet for '{title}'?", [(place, True), ("The main library entrance", False), ("Room 401 at the science building", False), ("The campus bookstore", False)], "The announcement states the meeting place.")
        q2 = await _add_question(session, exam, "listening", f"What should participants bring to '{title}'?", [(bring, True), ("A printed exam result", False), ("A signed travel form", False), ("A box of laboratory equipment", False)], "The speaker tells participants what to bring.")
        q3 = await _add_question(session, exam, "listening", f"When is '{title}' scheduled to meet?", [(time, True), ("The next day, fifteen minutes earlier", False), ("Two weeks later at noon", False), ("The previous evening", False)], "The speaker gives the meeting day and time.")
        for question in (q1, q2, q3):
            if question.id not in linked_ids:
                await session.execute(listening_questions.insert().values(track_id=track.id, question_id=question.id))
                linked_ids.add(question.id)

    existing_words = set((await session.execute(select(VocabularyWord.word))).scalars().all())
    for index, (word, part, definition, synonym) in enumerate(VOCABULARY_BANK):
        normalized = word.casefold()
        if normalized in existing_words:
            continue
        exam = ("IELTS", "TOEFL", "GRE")[index % 3]
        if part == "verb":
            example = VERB_EXAMPLES.get(word, f"Researchers {word} the available evidence before drawing a conclusion.")
        elif part == "adjective":
            article = "an" if word[0].casefold() in "aeiou" else "a"
            example = f"The report presents {article} {word} explanation of the study's results."
        else:
            example = f"The study examines the role of {word} in the final outcome."
        session.add(VocabularyWord(word=word, definition=definition, part_of_speech=part, examples=[example], synonyms=[synonym], exam_type=exam, difficulty=("easy", "intermediate", "advanced")[index % 3], frequency=5 + index % 5, source="Studywell academic vocabulary sample"))
        existing_words.add(normalized)

    grammar_count = await session.scalar(select(func.count()).select_from(GrammarExercise)) or 0
    needed = max(0, 100 - grammar_count)
    for rule_index, (rule, description, template, answer, explanation) in enumerate(GRAMMAR_RULES):
        topic_name = f"Question bank: {rule}"
        topic = await session.scalar(select(GrammarTopic).where(GrammarTopic.topic_name == topic_name))
        if topic is None:
            topic = GrammarTopic(topic_name=topic_name, description=description, explanation=description, examples=[], exam_type=("IELTS", "TOEFL", "GRE")[rule_index % 3], difficulty=("easy", "intermediate", "advanced")[rule_index % 3], order=20 + rule_index)
            session.add(topic)
            await session.flush()
        for variant in range(1, 7):
            if needed <= 0:
                break
            if rule_index == 0:
                subject = ["schedule", "collection", "summary", "list", "map", "description"][variant - 1]
                sentence = template.format(subject=subject)
            elif rule_index == 2:
                sentence = template.format(year=2015 + variant)
            else:
                sentence = template
            sentence = f"In example {variant}, {sentence[0].lower()}{sentence[1:]}"
            exists = await session.scalar(select(GrammarExercise.id).where(GrammarExercise.sentence == sentence))
            if exists:
                continue
            session.add(GrammarExercise(topic_id=topic.id, sentence=sentence, correct_form=answer, explanation=explanation, difficulty=("easy", "intermediate", "advanced")[(variant + rule_index) % 3], hint=description))
            needed -= 1

