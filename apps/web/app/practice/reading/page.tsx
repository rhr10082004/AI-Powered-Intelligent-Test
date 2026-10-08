'use client';

import { useState } from 'react';

import { useQuery, useMutation } from '@tanstack/react-query';
import Cookies from 'js-cookie';
import apiClient from '@/lib/api-client';

interface Passage {
  id: string;
  title: string;
  content: string;
  word_count: number;
  exam_type: string;
  difficulty: string;
  time_limit: number;
}

interface Question {
  id: string;
  text: string;
  question_type: string;
  answers: Array<{ id: string; text: string }>;
}

interface AnswerResult {
  id: string;
  question_id: string;
  is_correct: boolean | null;
  correct_answer: string | null;
  explanation: string | null;
  attempts: number;
}

export default function ReadingPracticePage() {
  const [selectedPassage, setSelectedPassage] = useState<Passage | null>(null);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, string>>({});
  const [startTime, setStartTime] = useState<number | null>(null);
  const [submissionMessage, setSubmissionMessage] = useState('');
  const [answerResults, setAnswerResults] = useState<Record<string, AnswerResult>>({});
  const [sessionId, setSessionId] = useState('');
  const [sessionCompleted, setSessionCompleted] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [examFilter, setExamFilter] = useState('All exams');

  // Fetch passages
  const { data: passages = [], isLoading: passagesLoading } = useQuery({
    queryKey: ['passages'],
    queryFn: async () => {
      const response = await apiClient.get<Passage[]>('/passages?limit=120');
      return response.data;
    },
  });
  const visiblePassages = passages.filter((passage) =>
    (examFilter === 'All exams' || passage.exam_type === examFilter) &&
    `${passage.title} ${passage.content}`.toLowerCase().includes(searchTerm.trim().toLowerCase())
  );

  // Fetch questions for selected passage
  const { data: passageDetail, isLoading: questionsLoading } = useQuery({
    queryKey: ['passage', selectedPassage?.id],
    queryFn: async () => {
      if (!selectedPassage) return null;
      const response = await apiClient.get<{ questions: Question[] }>(
        `/passages/${selectedPassage.id}`
      );
      return response.data;
    },
    enabled: !!selectedPassage,
  });

  // Submit answers mutation
  const submitMutation = useMutation({
    mutationFn: async () => {
      const token = Cookies.get('access_token');
      if (!token) {
        throw new Error('Please sign in before submitting answers.');
      }

      const questions = passageDetail?.questions ?? [];
      const results: AnswerResult[] = [];
      for (const question of questions) {
        const response = await apiClient.post<AnswerResult>(
          '/questions/answer',
          {
            question_id: question.id,
            answer_id: selectedAnswers[question.id],
            time_taken: startTime ? Math.floor((Date.now() - startTime) / 1000) : undefined,
            session_id: sessionId,
          },
        );
        results.push(response.data);
      }
      await apiClient.post('/study-sessions/complete', {
        session_id: sessionId,
        section: 'reading',
        duration: startTime ? Math.floor((Date.now() - startTime) / 1000) : 0,
      });
      return results;
    },
    onSuccess: (results) => {
      setAnswerResults(Object.fromEntries(results.map((result) => [result.question_id, result])));
      setSessionCompleted(true);
      const correct = results.filter((result) => result.is_correct).length;
      setSubmissionMessage(`Result: ${correct} of ${results.length} correct (${Math.round((correct / results.length) * 100)}%).`);
    },
    onError: (error) => setSubmissionMessage(error instanceof Error ? error.message : 'Could not submit your answers.'),
  });

  const handleSelectPassage = (passage: Passage) => {
    setSelectedPassage(passage);
    setStartTime(Date.now());
    setSelectedAnswers({});
    setAnswerResults({});
    setSubmissionMessage('');
    setSessionId(crypto.randomUUID());
    setSessionCompleted(false);
  };

  const handleAnswerSelect = (questionId: string, answerId: string) => {
    setSelectedAnswers((prev) => ({
      ...prev,
      [questionId]: answerId,
    }));
  };

  if (passagesLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-gray-600 dark:text-gray-400">Loading passages...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Reading Practice
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            {selectedPassage ? 'Answer the questions below' : 'Select a passage to begin'}
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-8">
        {!selectedPassage ? (
          // Passage List
          <>
          <section className="mb-6 grid gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:grid-cols-[minmax(0,1fr)_180px_auto] sm:items-end" aria-label="Filter reading passages">
            <label className="text-xs font-semibold text-slate-600">Find a topic or passage<input value={searchTerm} onChange={(event) => setSearchTerm(event.target.value)} placeholder="Try parks, research, campus…" className="mt-2 block w-full rounded-xl border border-slate-200 px-4 py-3 text-sm font-normal outline-none focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100" /></label>
            <label className="text-xs font-semibold text-slate-600">Exam<select value={examFilter} onChange={(event) => setExamFilter(event.target.value)} className="mt-2 block w-full rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm outline-none focus:border-emerald-600"><option>All exams</option><option>IELTS</option><option>TOEFL</option><option>GRE</option></select></label>
            <p className="pb-3 text-xs text-slate-500" role="status">{visiblePassages.length} of {passages.length} passages</p>
          </section>
          {visiblePassages.length === 0 ? <p className="rounded-2xl bg-white p-8 text-center text-sm text-slate-500">No passages match those filters. Try another exam or search term.</p> : <div className="motion-stagger grid gap-6 md:grid-cols-2">
            {visiblePassages.map((passage) => (
              <button
                type="button"
                key={passage.id}
                className="block w-full rounded-lg bg-white p-6 text-left shadow transition hover:shadow-lg dark:bg-gray-800"
                onClick={() => handleSelectPassage(passage)}
              >
                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">
                  {passage.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-3">
                  {passage.content}
                </p>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-blue-600 dark:text-blue-400 font-semibold">
                    {passage.exam_type}
                  </span>
                  <span className="text-gray-500 dark:text-gray-400">
                    {passage.word_count} words
                  </span>
                </div>
                <div className="mt-4">
                  <span className={`inline-block px-3 py-1 rounded text-xs font-semibold ${
                    passage.difficulty === 'easy'
                      ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                      : passage.difficulty === 'medium'
                      ? 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200'
                      : 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
                  }`}>
                    {passage.difficulty}
                  </span>
                </div>
              </button>
            ))}
          </div>}
          </>
        ) : questionsLoading ? (
          <div className="text-center text-gray-600 dark:text-gray-400">
            Loading questions...
          </div>
        ) : (
          // Reading and Questions
          <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
            {/* Passage */}
            <div className="h-fit rounded-lg bg-white p-6 shadow dark:bg-gray-800 lg:sticky lg:top-4">
              <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
                {selectedPassage.title}
              </h2>
              <p className="text-gray-700 dark:text-gray-300 leading-relaxed text-sm whitespace-pre-wrap">
                {selectedPassage.content}
              </p>
              <div className="mt-6">
                <button
                  onClick={() => setSelectedPassage(null)}
                  className="w-full px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white rounded hover:bg-gray-300 dark:hover:bg-gray-600 font-semibold transition"
                >
                  Back to Passages
                </button>
              </div>
            </div>

            {/* Questions */}
            <div className="space-y-6 lg:col-span-2">
              {passageDetail?.questions?.map((question, index) => (
                <div
                  key={question.id}
                  className="bg-white dark:bg-gray-800 rounded-lg shadow p-6"
                >
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
                    Question {index + 1}
                  </h3>
                  <p className="text-gray-700 dark:text-gray-300 mb-6 font-semibold">
                    {question.text}
                  </p>
                  <div className="space-y-3">
                    {question.answers.map((answer) => (
                      <label
                        key={answer.id}
                        className="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition"
                      >
                        <input
                          type="radio"
                          name={`question-${question.id}`}
                          value={answer.id}
                          checked={selectedAnswers[question.id] === answer.id}
                          onChange={() => handleAnswerSelect(question.id, answer.id)}
                          className="w-4 h-4"
                        />
                        <span className="ml-4 text-gray-700 dark:text-gray-300">
                          {answer.text}
                        </span>
                      </label>
                    ))}
                  </div>
                  {answerResults[question.id] && (
                    <div className={`mt-4 rounded-md p-3 text-sm ${answerResults[question.id].is_correct ? 'bg-emerald-50 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-200' : 'bg-amber-50 text-amber-900 dark:bg-amber-900/30 dark:text-amber-100'}`} role="status">
                      <p className="font-semibold">{answerResults[question.id].is_correct ? 'Correct' : `Review: ${answerResults[question.id].correct_answer || 'Answer recorded'}`}</p>
                      {answerResults[question.id].explanation && <p className="mt-1">{answerResults[question.id].explanation}</p>}
                    </div>
                  )}
                </div>
              ))}

              {/* Submit Button */}
              {passageDetail?.questions && passageDetail.questions.length > 0 && (
                <div>
                  {submissionMessage && <p className="mb-3 text-sm text-gray-700 dark:text-gray-300" role="status">{submissionMessage}</p>}
                  <button
                    onClick={() => {
                      if (!passageDetail.questions.every((question) => selectedAnswers[question.id])) {
                        setSubmissionMessage('Please answer every question before submitting.');
                        return;
                      }
                      setSubmissionMessage('');
                      submitMutation.mutate();
                    }}
                    disabled={submitMutation.isPending || sessionCompleted}
                    className="w-full rounded-lg bg-blue-600 px-6 py-3 font-bold text-white transition hover:bg-blue-700 disabled:opacity-50"
                  >
                    {submitMutation.isPending ? 'Submitting...' : sessionCompleted ? 'Session complete' : 'Submit answers'}
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
