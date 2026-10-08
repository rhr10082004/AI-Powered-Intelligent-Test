'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, CheckCircle2, RotateCcw, Target, Trophy } from 'lucide-react';
import apiClient from '@/lib/api-client';

type Option = { id: string; text: string };
type Question = { id: string; text: string; section: string; difficulty: string; answers: Option[] };
type Started = { attempt_id: string; exam_type: string; question_count: number; adaptive_level: string; questions: Question[] };
type ScoreGroup = Record<string, { correct: number; total: number; accuracy: number }>;
type Result = { id: string; exam_type: string; question_count: number; correct_count: number; accuracy: number; adaptive_level: string; section_scores: ScoreGroup; topic_scores: ScoreGroup; score_label: string; created_at: string };
type HistoryItem = Result;

export default function AdaptiveMockTestPage() {
  const [exam, setExam] = useState('IELTS');
  const [questionCount, setQuestionCount] = useState(10);
  const [attempt, setAttempt] = useState<Started | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [startedAt, setStartedAt] = useState<number | null>(null);
  const [result, setResult] = useState<Result | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const loadHistory = async () => {
    try { setHistory((await apiClient.get<HistoryItem[]>('/mock-tests/history?limit=20')).data); } catch { /* Sign-in is requested when the learner starts. */ }
  };
  useEffect(() => { void loadHistory(); }, []);

  const startTest = async () => {
    setLoading(true); setError(''); setResult(null); setAnswers({});
    try {
      const response = await apiClient.post<Started>('/mock-tests/start', { exam_type: exam, question_count: questionCount });
      setAttempt(response.data); setStartedAt(Date.now());
    } catch (cause: unknown) {
      const detail = (cause as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail || 'Sign in to start a mock test, then try again.');
    } finally { setLoading(false); }
  };

  const submitTest = async () => {
    if (!attempt || Object.keys(answers).length !== attempt.questions.length) return;
    setLoading(true); setError('');
    try {
      const response = await apiClient.post<Result>('/mock-tests/submit', {
        attempt_id: attempt.attempt_id,
        duration: startedAt ? Math.round((Date.now() - startedAt) / 1000) : 0,
        answers: attempt.questions.map((question) => ({ question_id: question.id, answer_id: answers[question.id] })),
      });
      setResult(response.data); setAttempt(null); setStartedAt(null); await loadHistory();
    } catch (cause: unknown) {
      const detail = (cause as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail || 'Your answers could not be saved. Please try again.');
    } finally { setLoading(false); }
  };

  return <main className="min-h-screen overflow-x-hidden bg-[#f7f8f4] px-4 py-8 text-[#1b3025] sm:px-7 sm:py-12"><div className="mx-auto max-w-6xl">
    <Link href="/practice" className="inline-flex items-center gap-2 text-sm font-semibold text-[#718078] hover:text-[#173f32]"><ArrowLeft size={15}/> All practice</Link>
    <header className="motion-enter mt-7"><p className="text-xs font-bold uppercase tracking-[.18em] text-[#679074]">Adaptive assessment</p><h1 className="mt-2 text-3xl font-semibold tracking-tight sm:text-4xl">Mock test <span className="font-serif italic text-emerald-800">studio.</span></h1><p className="mt-3 max-w-2xl text-sm leading-6 text-[#718078]">Reading and listening questions adjust to your recent results. Review section and topic accuracy after you submit.</p></header>

    {!attempt && !result && <section className="mt-8 grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(280px,.7fr)]"><div className="rounded-3xl border border-[#e1e8df] bg-white p-5 shadow-sm sm:p-7"><div className="grid gap-4 sm:grid-cols-2"><label className="text-xs font-bold text-[#53665a]">Exam<select value={exam} onChange={(event)=>setExam(event.target.value)} className="mt-2 block w-full rounded-xl border border-[#dce4dc] bg-white px-3 py-3 text-sm font-medium"><option>IELTS</option><option>TOEFL</option><option>GRE</option></select></label><label className="text-xs font-bold text-[#53665a]">Test length<select value={questionCount} onChange={(event)=>setQuestionCount(Number(event.target.value))} className="mt-2 block w-full rounded-xl border border-[#dce4dc] bg-white px-3 py-3 text-sm font-medium"><option value={10}>10 questions · about 10 minutes</option><option value={20}>20 questions · about 20 minutes</option><option value={30}>30 questions · about 30 minutes</option></select></label></div><div className="mt-6 rounded-2xl bg-[#eff5ed] p-4"><p className="flex items-center gap-2 text-sm font-bold text-[#36573f]"><Target size={17}/> Questions adapt to your recent practice</p><p className="mt-2 text-xs leading-5 text-[#718078]">New learners get a balanced set. After you practice, the test leans toward an easier, medium, or harder mix based on your last 20 saved answers.</p></div>{error&&<p role="alert" className="mt-4 rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-800">{error}</p>}<button type="button" onClick={()=>void startTest()} disabled={loading} className="mt-5 inline-flex min-h-12 items-center justify-center gap-2 rounded-xl bg-[#24463b] px-5 py-3 text-sm font-bold text-white transition hover:bg-[#18372d] disabled:opacity-50">{loading?'Preparing your test…':'Start adaptive mock test'}</button><p className="mt-4 text-[11px] leading-5 text-[#98a39a]">This is a practice estimate for reading and listening. It is not an official exam score.</p></div>
      <section className="rounded-3xl border border-[#e1e8df] bg-white p-5 shadow-sm sm:p-6" aria-label="Recent mock tests"><h2 className="text-sm font-bold text-[#40574a]">Recent results <span className="ml-1 rounded-full bg-[#f0f5ed] px-2 py-1 text-[10px] text-[#5e7863]">{history.length}</span></h2>{history.length?<ul className="mt-3 divide-y divide-[#eef1ec]">{history.slice(0,6).map((item)=><li key={item.id} className="py-3"><div className="flex items-start justify-between gap-3"><div><p className="text-xs font-bold text-[#53665a]">{item.exam_type} · {item.question_count} questions</p><p className="mt-1 text-[10px] text-[#98a39a]">{new Date(item.created_at).toLocaleDateString()} · {item.adaptive_level} set</p></div><span className="text-sm font-extrabold text-[#35694e]">{item.accuracy}%</span></div></li>)}</ul>:<p className="mt-3 text-xs leading-5 text-[#89958c]">Completed tests and their score trends will appear here.</p>}</section></section>}

    {attempt&&<section className="mt-8"><div className="mb-5 flex flex-wrap items-center justify-between gap-3 rounded-2xl bg-[#1d4034] px-5 py-4 text-white"><div><p className="text-xs font-bold uppercase tracking-wider text-white/60">{attempt.exam_type} adaptive mock</p><p className="mt-1 text-sm font-semibold">{Object.keys(answers).length} of {attempt.question_count} answered</p></div><span className="rounded-full bg-white/10 px-3 py-2 text-xs font-bold capitalize">{attempt.adaptive_level} level mix</span></div><div className="space-y-4">{attempt.questions.map((question,index)=><fieldset key={question.id} className="rounded-3xl border border-[#e1e8df] bg-white p-5 shadow-sm sm:p-6"><legend className="sr-only">Question {index+1}</legend><div className="flex flex-wrap items-center gap-2"><span className="rounded-full bg-[#edf3e9] px-3 py-1 text-[10px] font-bold text-[#51745a]">Question {index+1}</span><span className="rounded-full bg-[#f4f5f1] px-3 py-1 text-[10px] font-bold capitalize text-[#7c8a80]">{question.section}</span><span className="text-[10px] font-semibold capitalize text-[#9aa49c]">{question.difficulty}</span></div><p className="mt-4 text-sm font-semibold leading-6 text-[#304a38]">{question.text}</p><div className="mt-4 grid gap-2 sm:grid-cols-2">{question.answers.map((option,optionIndex)=><label key={option.id} className={`flex cursor-pointer items-start gap-3 rounded-2xl border p-3 text-xs leading-5 transition ${answers[question.id]===option.id?'border-[#75a17c] bg-[#f0f6ee] text-[#284933]':'border-[#edf0eb] bg-[#fcfdfb] text-[#617167] hover:border-[#cad9c9]'}`}><input type="radio" name={question.id} value={option.id} checked={answers[question.id]===option.id} onChange={()=>setAnswers((current)=>({...current,[question.id]:option.id}))} className="mt-0.5 accent-emerald-800"/><span className="font-bold">{String.fromCharCode(65+optionIndex)}.</span><span>{option.text}</span></label>)}</div></fieldset>)}</div>{error&&<p role="alert" className="mt-4 rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-800">{error}</p>}<div className="mt-5 flex flex-wrap items-center justify-between gap-3"><p className="text-xs text-[#829087]">Answer each question; the score appears after submission.</p><button type="button" onClick={()=>void submitTest()} disabled={loading||Object.keys(answers).length!==attempt.question_count} className="inline-flex min-h-12 items-center gap-2 rounded-xl bg-[#24463b] px-5 py-3 text-sm font-bold text-white transition hover:bg-[#18372d] disabled:opacity-45">{loading?'Scoring…':`Submit ${attempt.question_count} answers`} <CheckCircle2 size={16}/></button></div></section>}

    {result&&<section className="mt-8"><div className="rounded-[2rem] bg-[#1d4034] p-6 text-white shadow-lg sm:p-9"><div className="flex flex-wrap items-end justify-between gap-4"><div><p className="flex items-center gap-2 text-xs font-bold uppercase tracking-[.16em] text-[#c4ddc5]"><Trophy size={15}/> Mock test complete</p><h2 className="mt-3 text-2xl font-semibold">{result.score_label} progress</h2><p className="mt-2 text-sm text-white/70">{result.correct_count} of {result.question_count} correct · {result.exam_type} · {result.adaptive_level} question mix</p></div><p className="text-5xl font-black tracking-tight">{result.accuracy}<span className="text-2xl">%</span></p></div><p className="mt-5 max-w-2xl text-xs leading-5 text-white/60">This result summarizes reading and listening accuracy for this practice set. It should not be interpreted as an official whole-exam score.</p></div><div className="mt-5 grid gap-5 lg:grid-cols-2"><section className="rounded-3xl border border-[#e1e8df] bg-white p-5 shadow-sm sm:p-6"><h3 className="text-sm font-bold text-[#40574a]">By section</h3><div className="mt-4 space-y-3">{Object.entries(result.section_scores).map(([name,score])=><div key={name} className="rounded-2xl bg-[#f8f9f6] p-4"><div className="flex justify-between gap-3"><span className="text-xs font-bold capitalize text-[#53665a]">{name}</span><span className="text-xs font-extrabold text-[#35694e]">{score.accuracy}% · {score.correct}/{score.total}</span></div><div className="mt-3 h-2 overflow-hidden rounded-full bg-[#e6ebe4]"><div className="h-full rounded-full bg-[#659873]" style={{width:`${score.accuracy}%`}}/></div></div>)}</div></section><section className="rounded-3xl border border-[#e1e8df] bg-white p-5 shadow-sm sm:p-6"><h3 className="text-sm font-bold text-[#40574a]">Topic trend for this set</h3><div className="mt-4 space-y-2">{Object.entries(result.topic_scores).sort((a,b)=>a[1].accuracy-b[1].accuracy).map(([name,score])=><div key={name} className="flex items-center justify-between gap-3 rounded-2xl bg-[#f8f9f6] px-4 py-3"><span className="min-w-0 truncate text-xs font-semibold text-[#617167]">{name}</span><span className="shrink-0 text-xs font-extrabold text-[#35694e]">{score.accuracy}%</span></div>)}</div></section></div><button type="button" onClick={()=>{setResult(null);setAnswers({});setError('');}} className="mt-5 inline-flex items-center gap-2 rounded-full border border-[#dce4dc] bg-white px-4 py-2.5 text-xs font-bold text-[#53665a] transition hover:border-[#8aaf91]"><RotateCcw size={14}/> Start another test</button></section>}
  </div></main>;
}
