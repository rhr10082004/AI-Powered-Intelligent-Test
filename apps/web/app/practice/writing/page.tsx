'use client';

import Link from 'next/link';
import { FormEvent, useEffect, useMemo, useState } from 'react';
import apiClient from '@/lib/api-client';

type Criterion = { name: string; score: number; feedback: string };
type Evaluation = { id: string; exam_type: string; word_count: number; estimated_band: number; evaluation_method: 'ai' | 'rubric'; feedback: { summary: string; criteria: Criterion[]; strengths: string[]; next_steps: string[] } };
type HistoryItem = { id: string; exam_type: string; essay_excerpt: string; word_count: number; estimated_band: number; evaluation_method: 'ai' | 'rubric'; summary: string; created_at: string };

const writingTopics = [
  'cities should make public transportation affordable and reliable', 'universities should require a period of community service',
  'libraries should invest equally in digital and printed collections', 'schools should teach students how to evaluate online information',
  'employers should allow flexible working hours when possible', 'local governments should protect historic buildings during redevelopment',
  'students should learn practical financial skills before graduation', 'public parks should be designed with input from nearby residents',
  'scientific research should be explained in plain language to the public', 'people should repair useful products instead of replacing them',
  'communities should reduce food waste through shared programs', 'universities should offer more interdisciplinary courses',
  'cities should create safer routes for walking and cycling', 'online learning can complement but not fully replace classroom teaching',
  'public museums should make more of their collections available online', 'companies should consider environmental effects when choosing suppliers',
  'young adults benefit from studying or working in another region', 'governments should make preventive health services easier to access',
  'teams make better decisions when members have different backgrounds', 'success should be measured by more than economic growth',
];

const promptFrames: Record<string, ((topic: string) => string)[]> = {
  IELTS: [
    (topic) => `Some people believe ${topic}. To what extent do you agree or disagree?`,
    (topic) => `Discuss the arguments for and against the view that ${topic}. Give your own opinion.`,
    (topic) => `What benefits and challenges might arise from the proposal that ${topic}? Explain with examples.`,
    (topic) => `What factors should decision-makers consider when deciding whether ${topic}?`,
    (topic) => `What practical steps could communities take to support this proposal: ${topic[0].toUpperCase()}${topic.slice(1)}? Discuss possible outcomes.`,
  ],
  TOEFL: [
    (topic) => `Do you agree or disagree that ${topic}? Use specific reasons and examples.`,
    (topic) => `Which matters more when considering whether ${topic}: cost, access, or long-term effects? Explain your choice.`,
    (topic) => `Describe one possible benefit and one possible drawback if ${topic}. Which is more important?`,
    (topic) => `Imagine your community is considering this proposal: ${topic[0].toUpperCase()}${topic.slice(1)}. What would you recommend and why?`,
    (topic) => `Some people support the idea that ${topic}; others prefer the current approach. Which view do you find more convincing?`,
  ],
  GRE: [
    (topic) => `A policy proposal claims that ${topic}. Write a response evaluating the reasoning behind this claim.`,
    (topic) => `The best way to achieve progress is to ensure that ${topic}. Discuss the extent to which you agree.`,
    (topic) => `Evaluate the claim that ${topic}, considering assumptions and possible counterexamples.`,
    (topic) => `Some argue that ${topic}. Analyze the claim and explain what evidence would strengthen or weaken it.`,
    (topic) => `Write an argument examining the consequences of the proposal that ${topic}.`,
  ],
};

const writingPrompts = Object.fromEntries(Object.entries(promptFrames).map(([exam, frames]) => [
  exam,
  writingTopics.flatMap((topic) => frames.map((frame) => frame(topic))),
])) as Record<string, string[]>;

export default function WritingPracticePage() {
  const [exam, setExam] = useState('IELTS');
  const [prompt, setPrompt] = useState('');
  const [essay, setEssay] = useState('');
  const [result, setResult] = useState<Evaluation | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const wordCount = useMemo(() => essay.trim() ? essay.trim().split(/\s+/).length : 0, [essay]);

  async function loadHistory() {
    try { const response = await apiClient.get<HistoryItem[]>('/writing/history'); setHistory(response.data); } catch { /* Sign-in and network errors are shown when the learner submits. */ }
  }
  useEffect(() => {
    const savedExam = window.localStorage.getItem('study_exam');
    if (savedExam && ['IELTS', 'GRE', 'TOEFL'].includes(savedExam.toUpperCase())) setExam(savedExam.toUpperCase());
    void loadHistory();
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(''); setResult(null); setLoading(true);
    try {
      const response = await apiClient.post<Evaluation>('/writing/evaluate', { exam_type: exam, prompt, essay });
      setResult(response.data); await loadHistory();
    } catch (cause: unknown) {
      const detail = (cause as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail || 'We could not save this draft. Sign in and check your connection, then try again.');
    } finally { setLoading(false); }
  }

  return <main className="min-h-screen overflow-x-hidden bg-[#f8f8f5] px-5 py-8 text-slate-900 sm:px-8 sm:py-12"><div className="mx-auto w-full min-w-0 max-w-6xl">
    <Link href="/practice" className="text-sm font-semibold text-slate-500 transition hover:text-slate-900">← All practice</Link>
    <header className="motion-enter mt-7"><p className="text-xs font-bold uppercase tracking-[.2em] text-emerald-800">Writing studio</p><h1 className="mt-2 text-3xl font-semibold tracking-tight sm:text-4xl">Find your next <span className="font-serif italic text-emerald-800">stronger sentence.</span></h1><p className="mt-3 max-w-2xl text-sm leading-6 text-slate-500">Write a response, then get a structured practice review with strengths and useful next steps.</p></header>
    <div className="mt-8 grid items-start gap-6 lg:grid-cols-[minmax(0,1.4fr)_minmax(280px,.8fr)]">
      <form onSubmit={handleSubmit} className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-7">
        <div className="grid gap-4 sm:grid-cols-[180px_1fr]"><label className="text-xs font-bold text-slate-600">Exam format<select value={exam} onChange={(e) => setExam(e.target.value)} className="mt-2 block w-full rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm font-medium text-slate-800 outline-none focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100"><option>IELTS</option><option>TOEFL</option><option>GRE</option></select></label><label className="text-xs font-bold text-slate-600">Essay prompt <span className="font-normal text-slate-400">(optional)</span><input value={prompt} onChange={(e) => setPrompt(e.target.value)} maxLength={2000} placeholder="Paste the question you are answering" className="mt-2 block w-full rounded-xl border border-slate-200 px-3 py-3 text-sm font-normal text-slate-800 outline-none placeholder:text-slate-400 focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100" /></label></div>
        <label className="mt-5 block text-xs font-bold text-slate-600">Choose a practice prompt <span className="font-normal text-slate-400">({writingPrompts[exam].length} examples)</span><select defaultValue="" onChange={(event) => { if (event.target.value) setPrompt(event.target.value); }} className="mt-2 block w-full rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm font-medium text-slate-700 outline-none focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100"><option value="">Choose one of 100 {exam} prompts</option>{writingPrompts[exam].map((sample, index) => <option key={`${exam}-${index}`} value={sample}>{String(index + 1).padStart(3, '0')} · {sample}</option>)}</select></label>
        <label className="mt-6 block text-xs font-bold text-slate-600">Your response<textarea value={essay} onChange={(e) => setEssay(e.target.value)} maxLength={20000} minLength={100} rows={14} required placeholder="Start with your main idea. Use paragraphs to build your argument, and support each point with a clear example…" className="mt-2 block w-full resize-y rounded-2xl border border-slate-200 px-4 py-4 text-sm leading-7 text-slate-800 outline-none placeholder:text-slate-400 focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100" /></label>
        <div className="mt-3 flex flex-wrap items-center justify-between gap-3"><span className={`text-xs ${wordCount > 0 && wordCount < 80 ? 'font-semibold text-amber-700' : 'text-slate-400'}`}>{wordCount} words · minimum 80 words</span><span className="text-xs text-slate-400">{essay.length.toLocaleString()} / 20,000 characters</span></div>
        {error && <p role="alert" className="mt-4 rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-800">{error}</p>}
        <button disabled={loading || wordCount < 80} className="mt-5 inline-flex min-h-12 w-full items-center justify-center gap-2 rounded-xl bg-[#24463b] px-5 py-3 text-sm font-bold text-white shadow-sm transition hover:bg-[#18372d] disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto">{loading ? <><span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" />Reviewing your draft…</> : <>Get my practice review <span aria-hidden="true">→</span></>}</button>
        <p className="mt-4 text-xs leading-5 text-slate-400">Your drafts are saved to your account. Feedback is a learning estimate, not an official exam score.</p>
      </form>
      <section aria-live="polite" className="motion-enter space-y-5" style={{ animationDelay: '120ms' }}>
        {result ? <>
          <div className="rounded-3xl bg-[#203d35] p-6 text-white shadow-lg shadow-emerald-950/10"><div className="flex items-start justify-between gap-4"><div><p className="text-xs font-bold uppercase tracking-[.16em] text-white/60">Estimated practice score</p><p className="mt-2 text-5xl font-semibold tracking-tight">{result.estimated_band.toFixed(1)}<span className="ml-2 text-sm font-medium text-white/55">/ 9</span></p></div><span className="rounded-full bg-white/10 px-3 py-1.5 text-xs font-semibold">{result.evaluation_method === 'ai' ? 'AI feedback' : 'Practice rubric'}</span></div><p className="mt-5 text-sm leading-6 text-white/75">{result.feedback.summary}</p></div>
          <div className="rounded-3xl border border-slate-200 bg-white p-5"><h2 className="font-semibold">Your four criteria</h2><div className="mt-4 space-y-4">{result.feedback.criteria.map((item) => <div key={item.name}><div className="flex justify-between gap-3 text-sm"><span className="font-semibold">{item.name}</span><span className="font-bold text-emerald-800">{item.score.toFixed(1)}</span></div><div className="mt-2 h-1.5 overflow-hidden rounded-full bg-slate-100"><div className="h-full rounded-full bg-emerald-700 transition-all duration-700" style={{ width: `${(item.score / 9) * 100}%` }} /></div><p className="mt-2 text-xs leading-5 text-slate-500">{item.feedback}</p></div>)}</div></div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2"><div className="rounded-3xl border border-emerald-100 bg-emerald-50/70 p-5"><h3 className="text-sm font-bold text-emerald-900">What’s working</h3><ul className="mt-3 space-y-2 text-sm leading-5 text-emerald-950/75">{result.feedback.strengths.map((item, i) => <li key={i}>✓ {item}</li>)}</ul></div><div className="rounded-3xl border border-amber-100 bg-amber-50/70 p-5"><h3 className="text-sm font-bold text-amber-900">Try next</h3><ul className="mt-3 space-y-2 text-sm leading-5 text-amber-950/75">{result.feedback.next_steps.map((item, i) => <li key={i}>↗ {item}</li>)}</ul></div></div>
        </> : <div className="rounded-3xl border border-dashed border-slate-300 bg-white/60 p-7 text-center"><span className="mx-auto grid h-12 w-12 place-items-center rounded-2xl bg-emerald-50 text-xl text-emerald-800">✎</span><h2 className="mt-4 font-semibold">Your feedback will appear here</h2><p className="mx-auto mt-2 max-w-sm text-sm leading-6 text-slate-500">Add at least 80 words and send your draft for a clear, focused review.</p></div>}
        <div className="rounded-3xl border border-slate-200 bg-white p-5"><div className="flex items-center justify-between gap-3"><div><h2 className="font-semibold">Recent drafts</h2><p className="mt-1 text-xs text-slate-400">Private to your account</p></div><span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-500">{history.length}</span></div>{history.length ? <ul className="mt-4 divide-y divide-slate-100">{history.slice(0, 4).map((item) => <li key={item.id} className="py-3 first:pt-0 last:pb-0"><div className="flex justify-between gap-3"><span className="text-sm font-semibold">{item.exam_type} · {item.word_count} words</span><span className="text-sm font-bold text-emerald-800">{item.estimated_band.toFixed(1)}</span></div><p className="mt-1 line-clamp-2 text-xs leading-5 text-slate-500">{item.summary}</p></li>)}</ul> : <p className="mt-4 text-sm text-slate-500">Saved reviews will show up here.</p>}</div>
      </section>
    </div>
  </div></main>;
}
