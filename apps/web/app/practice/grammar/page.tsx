'use client';

import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api-client';

interface GrammarExercise {
  id: string;
  sentence: string;
  hint: string | null;
}

interface GrammarTopic {
  id: string;
  topic_name: string;
  description: string | null;
  difficulty: string;
  exercises: GrammarExercise[];
}

interface ExerciseResult {
  id: string;
  exercise_id: string;
  is_correct: boolean;
  correct_form: string;
  explanation: string | null;
  attempt_number: number;
  created_at: string;
}

interface GrammarAttempt {
  id: string;
  exercise_id: string;
  topic_name: string;
  sentence: string;
  user_answer: string;
  is_correct: boolean;
  created_at: string;
}

export default function GrammarPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [results, setResults] = useState<Record<string, ExerciseResult>>({});
  const [submittingId, setSubmittingId] = useState('');
  const [error, setError] = useState('');
  const queryClient = useQueryClient();
  const { data: topics = [], isLoading, isError } = useQuery({
    queryKey: ['grammar-topics'],
    queryFn: async () => (await apiClient.get<GrammarTopic[]>('/grammar/topics?limit=120')).data,
  });
  const visibleTopics = topics.filter((topic) =>
    `${topic.topic_name} ${topic.description ?? ''}`.toLowerCase().includes(searchTerm.trim().toLowerCase())
  );
  const { data: attempts = [], isError: attemptsError } = useQuery({
    queryKey: ['grammar-attempts'],
    queryFn: async () => (await apiClient.get<GrammarAttempt[]>('/grammar/my-attempts?limit=6')).data,
  });

  const submitAnswer = async (exerciseId: string) => {
    const userAnswer = answers[exerciseId]?.trim();
    if (!userAnswer) return;
    setSubmittingId(exerciseId);
    setError('');
    try {
      const response = await apiClient.post<ExerciseResult>('/grammar/exercises/answer', {
        exercise_id: exerciseId,
        user_answer: userAnswer,
      });
      setResults((current) => ({ ...current, [exerciseId]: response.data }));
      await queryClient.invalidateQueries({ queryKey: ['grammar-attempts'] });
    } catch {
      setError('Sign in to submit an answer, then try again.');
    } finally {
      setSubmittingId('');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 px-4 py-12 dark:bg-slate-900">
      <div className="motion-enter mx-auto max-w-5xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Grammar Exercises</h1>
          <p className="mt-2 text-slate-600 dark:text-slate-300">Practice common grammar patterns used in admission and academic writing.</p>
        </div>

        <section className="mb-6 grid gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:grid-cols-[minmax(0,1fr)_auto] sm:items-end" aria-label="Find grammar lessons">
          <label className="text-xs font-semibold text-slate-600">Search a grammar topic<input value={searchTerm} onChange={(event) => setSearchTerm(event.target.value)} placeholder="Try tense, articles, clauses…" className="mt-2 block w-full rounded-xl border border-slate-200 px-4 py-3 text-sm font-normal outline-none focus:border-amber-500 focus:ring-2 focus:ring-amber-100" /></label>
          <p className="pb-3 text-xs text-slate-500" role="status">{visibleTopics.length} of {topics.length} lessons · {topics.reduce((count, topic) => count + topic.exercises.length, 0)} exercises</p>
        </section>

        {isLoading && <p role="status">Loading exercises...</p>}
        {isError && <p role="alert">Grammar exercises could not be loaded.</p>}
        {error && <p className="mb-4 text-sm text-red-600" role="alert">{error}</p>}
        {!isLoading && !isError && visibleTopics.length === 0 && <p className="rounded-2xl bg-white p-8 text-center text-sm text-slate-500">No grammar topics match that search.</p>}
        <div className="motion-stagger space-y-5">
          {visibleTopics.map((topic, index) => (
            <div key={topic.id} className="rounded-lg bg-white p-6 shadow-lg dark:bg-slate-800">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold uppercase tracking-[0.2em] text-amber-600">
                    Lesson {index + 1}
                  </p>
                  <h2 className="mt-2 text-xl font-bold text-slate-900 dark:text-white">{topic.topic_name}</h2>
                </div>
                <span className="rounded-full bg-amber-100 px-2 py-1 text-xs font-semibold text-amber-700 dark:bg-amber-900 dark:text-amber-200">
                  {topic.difficulty}
                </span>
              </div>
              {topic.description && <p className="mt-4 text-slate-600 dark:text-slate-300">{topic.description}</p>}
              <div className="mt-5 space-y-5">
                {topic.exercises.map((exercise) => {
                  const result = results[exercise.id];
                  return (
                    <form key={exercise.id} onSubmit={(event) => { event.preventDefault(); void submitAnswer(exercise.id); }} className="border-t border-slate-200 pt-5 dark:border-slate-700">
                      <label className="block text-sm font-medium text-slate-800 dark:text-slate-100" htmlFor={`answer-${exercise.id}`}>{exercise.sentence}</label>
                      {exercise.hint && <p className="mt-2 text-xs text-slate-500">Hint: {exercise.hint}</p>}
                      <div className="mt-3 flex flex-col gap-3 sm:flex-row">
                        <input id={`answer-${exercise.id}`} value={answers[exercise.id] || ''} onChange={(event) => setAnswers((current) => ({ ...current, [exercise.id]: event.target.value }))} className="min-w-0 flex-1 rounded-lg border border-slate-300 bg-white px-3 py-2 dark:border-slate-600 dark:bg-slate-700 dark:text-white" placeholder="Type the correct form" />
                        <button type="submit" disabled={submittingId === exercise.id || !answers[exercise.id]?.trim()} className="rounded-lg bg-amber-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-amber-700 disabled:opacity-50">{submittingId === exercise.id ? 'Checking...' : 'Check answer'}</button>
                      </div>
                      {result && <p className={`mt-3 text-sm ${result.is_correct ? 'text-emerald-700 dark:text-emerald-300' : 'text-amber-700 dark:text-amber-300'}`} role="status">{result.is_correct ? 'Correct.' : `Answer: ${result.correct_form}.`} Attempt {result.attempt_number}. {result.explanation}</p>}
                    </form>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
        <section className="mt-10 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800" aria-labelledby="grammar-history-title">
          <div className="flex items-center justify-between gap-3"><div><h2 id="grammar-history-title" className="text-lg font-bold text-slate-900 dark:text-white">Recent attempts</h2><p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Your latest answers, saved to your account.</p></div><span className="rounded-full bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-800 dark:bg-amber-900/50 dark:text-amber-200">{attempts.length}</span></div>
          {attemptsError ? <p className="mt-4 text-sm text-slate-500">Sign in to view your saved attempts.</p> : attempts.length === 0 ? <p className="mt-4 text-sm text-slate-500 dark:text-slate-400">Complete an exercise to start your history.</p> : <ul className="mt-4 divide-y divide-slate-100 dark:divide-slate-700">{attempts.map((attempt) => <li key={attempt.id} className="flex flex-col justify-between gap-2 py-3 sm:flex-row sm:items-center"><div className="min-w-0"><p className="text-sm font-semibold text-slate-800 dark:text-slate-100">{attempt.topic_name}</p><p className="mt-1 truncate text-xs text-slate-500">{attempt.sentence}</p></div><span className={`shrink-0 text-xs font-bold ${attempt.is_correct ? 'text-emerald-700 dark:text-emerald-300' : 'text-amber-700 dark:text-amber-300'}`}>{attempt.is_correct ? 'Correct' : `Review: ${attempt.user_answer}`}</span></li>)}</ul>}
        </section>
      </div>
    </div>
  );
}
