'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import apiClient from '@/lib/api-client';

type Option = { id: string; text: string };
type Question = { id: string; text: string; answers: Option[] };
type QuestionSet = { exam_type: string; section: string; question_count: number; questions: Question[] };
type AnswerResult = { question_id: string; is_correct: boolean | null; correct_answer: string | null; explanation: string | null };

export default function DiagnosticPage() {
  const [exam, setExam] = useState('IELTS');
  const [questionSet, setQuestionSet] = useState<QuestionSet | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [results, setResults] = useState<Record<string, AnswerResult>>({});
  const [sessionId, setSessionId] = useState('');
  const [startedAt, setStartedAt] = useState<number | null>(null);
  const [done, setDone] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  async function load(examType: string) {
    setError(''); setQuestionSet(null); setAnswers({}); setResults({}); setDone(false);
    try {
      const response = await apiClient.get<QuestionSet>(`/diagnostic/questions?exam_type=${examType}&limit=5`);
      setQuestionSet(response.data); setSessionId(crypto.randomUUID()); setStartedAt(Date.now());
    } catch (cause: unknown) {
      const detail = (cause as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail || 'Sign in to start your diagnostic, then try again.');
    }
  }
  useEffect(() => {
    const initialExam = (window.localStorage.getItem('study_exam') || 'IELTS').toUpperCase();
    const supportedExam = ['IELTS', 'GRE', 'TOEFL'].includes(initialExam) ? initialExam : 'IELTS';
    setExam(supportedExam); void load(supportedExam);
  }, []);

  async function submit() {
    if (!questionSet || !sessionId || !questionSet.questions.every((question) => answers[question.id])) return;
    setBusy(true); setError('');
    try {
      const submitted: AnswerResult[] = [];
      for (const question of questionSet.questions) {
        const response = await apiClient.post<AnswerResult>('/questions/answer', {
          question_id: question.id,
          answer_id: answers[question.id],
          time_taken: startedAt ? Math.floor((Date.now() - startedAt) / 1000) : 0,
          session_id: sessionId,
        });
        submitted.push(response.data);
      }
      await apiClient.post('/study-sessions/complete', {
        session_id: sessionId,
        section: 'reading',
        duration: startedAt ? Math.max(1, Math.floor((Date.now() - startedAt) / 1000)) : 1,
      });
      setResults(Object.fromEntries(submitted.map((result) => [result.question_id, result])));
      setDone(true);
    } catch (cause: unknown) {
      const detail = (cause as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail || 'We could not save this diagnostic. Please try again.');
    } finally { setBusy(false); }
  }

  const correct = Object.values(results).filter((result) => result.is_correct).length;
  const completeCount = questionSet?.questions.filter((question) => answers[question.id]).length || 0;
  return <main className="min-h-screen bg-[#f8f8f5] px-5 py-8 text-slate-900 sm:px-8 sm:py-12"><div className="mx-auto w-full max-w-4xl"><Link href="/practice" className="text-sm font-semibold text-slate-500 hover:text-slate-900">← All practice</Link><header className="motion-enter mt-7 rounded-[2rem] bg-[#203d35] p-7 text-white shadow-lg sm:p-10"><p className="text-xs font-bold uppercase tracking-[.18em] text-emerald-100/70">Quick diagnostic · reading</p><h1 className="mt-3 text-3xl font-semibold sm:text-4xl">Find your starting point.</h1><p className="mt-3 max-w-xl text-sm leading-6 text-white/70">Five questions give you a baseline to guide your next study sessions. This is a practice check, not an official exam score.</p><div className="mt-6 flex flex-wrap items-center gap-3"><label className="text-xs font-semibold text-white/75">Exam<select value={exam} onChange={(event) => { const next = event.target.value; setExam(next); void load(next); }} className="ml-2 rounded-lg border border-white/20 bg-[#315549] px-3 py-2 text-sm text-white outline-none focus:ring-2 focus:ring-white/50"><option>IELTS</option><option>GRE</option><option>TOEFL</option></select></label><button type="button" onClick={() => void load(exam)} className="rounded-lg bg-white/10 px-3 py-2 text-xs font-bold text-white hover:bg-white/20">New question set</button></div></header>
    {error && <p role="alert" className="mt-5 rounded-xl bg-rose-50 p-4 text-sm text-rose-800">{error}</p>}
    {!questionSet && !error && <p role="status" className="mt-6 text-sm text-slate-500">Finding your questions…</p>}
    {questionSet && <section className="mt-6 space-y-4">{done && <div role="status" className="motion-enter rounded-2xl border border-emerald-100 bg-emerald-50 p-5"><p className="text-xs font-bold uppercase tracking-[.15em] text-emerald-800">Your baseline</p><p className="mt-2 text-2xl font-semibold text-emerald-950">{correct} / {questionSet.question_count} correct <span className="text-base text-emerald-800">· {Math.round((correct / questionSet.question_count) * 100)}%</span></p><p className="mt-2 text-sm text-emerald-900/75">Your result is saved. Try a focused practice module next, then return later to compare your progress.</p><Link href="/study-plan" className="mt-3 inline-block text-sm font-bold text-emerald-900 underline">Open today&apos;s study plan →</Link></div>}
      {!done && <div className="flex items-center justify-between text-xs font-semibold text-slate-500"><span>{completeCount} of {questionSet.question_count} answered</span><span>Untimed · take your time</span></div>}
      {questionSet.questions.map((question, index) => { const result = results[question.id]; return <article key={question.id} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6"><p className="text-xs font-bold uppercase tracking-[.14em] text-emerald-800">Question {index + 1}</p><h2 className="mt-2 text-base font-semibold leading-7">{question.text}</h2><div className="mt-4 space-y-2">{question.answers.map((option) => <label key={option.id} className={`flex cursor-pointer items-start gap-3 rounded-xl border px-4 py-3 text-sm transition ${answers[question.id] === option.id ? 'border-emerald-700 bg-emerald-50' : 'border-slate-200 hover:border-emerald-300'} ${done ? 'cursor-default' : ''}`}><input type="radio" name={question.id} value={option.id} checked={answers[question.id] === option.id} disabled={done} onChange={() => setAnswers((current) => ({ ...current, [question.id]: option.id }))} className="mt-0.5 accent-emerald-800" /><span>{option.text}</span></label>)}</div>{result && <p className={`mt-4 rounded-xl p-3 text-sm ${result.is_correct ? 'bg-emerald-50 text-emerald-900' : 'bg-amber-50 text-amber-900'}`} role="status">{result.is_correct ? 'Correct.' : `Review: ${result.correct_answer || 'check the answer explanation'}.`} {result.explanation}</p>}</article>; })}
      {!done && <button type="button" disabled={busy || completeCount !== questionSet.question_count} onClick={() => void submit()} className="w-full rounded-xl bg-[#24463b] px-5 py-4 text-sm font-bold text-white transition hover:bg-[#18372d] disabled:cursor-not-allowed disabled:opacity-50">{busy ? 'Saving your result…' : 'Finish diagnostic'}</button>}
    </section>}
  </div></main>;
}
