'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import apiClient from '@/lib/api-client';

type PlanTask = { id: string; title: string; section: string; minutes: number; href: string; completed: boolean };
type DailyPlan = { id: string; exam_type: string; plan_date: string; target_minutes: number; tasks: PlanTask[] };

export default function StudyPlanPage() {
  const [plan, setPlan] = useState<DailyPlan | null>(null);
  const [busy, setBusy] = useState('');
  const [error, setError] = useState('');
  useEffect(() => {
    const exam = window.localStorage.getItem('study_exam') || 'GENERAL';
    apiClient.post<DailyPlan>('/study-plan/today', { exam_type: exam })
      .then((response) => setPlan(response.data))
      .catch(() => setError('Sign in to create and save your daily plan.'));
  }, []);
  async function complete(task: PlanTask) {
    if (!plan || task.completed) return;
    setBusy(task.id); setError('');
    try {
      const response = await apiClient.post<DailyPlan>(`/study-plan/${plan.id}/tasks/${task.id}/complete`);
      setPlan(response.data);
    } catch { setError('We could not update this task. Please try again.'); }
    finally { setBusy(''); }
  }
  const completedCount = plan?.tasks.filter((task) => task.completed).length || 0;
  return <main className="min-h-screen bg-[#f8f8f5] px-5 py-9 text-slate-900 sm:px-8 sm:py-12"><div className="mx-auto w-full max-w-4xl"><Link href="/dashboard" className="text-sm font-semibold text-slate-500 hover:text-slate-900">← Dashboard</Link><header className="motion-enter mt-7 rounded-[2rem] bg-[#203d35] p-7 text-white shadow-lg sm:p-10"><p className="text-xs font-bold uppercase tracking-[.18em] text-emerald-100/70">Your daily rhythm</p><h1 className="mt-3 text-3xl font-semibold sm:text-4xl">A focused plan for today.</h1><p className="mt-3 max-w-xl text-sm leading-6 text-white/70">A manageable 30-minute mix, shaped around your practice progress.</p></header>
    {error && <p role="alert" className="mt-5 rounded-xl bg-rose-50 p-4 text-sm text-rose-800">{error}</p>}
    {!plan && !error && <p role="status" className="mt-6 text-sm text-slate-500">Building your plan…</p>}
    {plan && <section className="mt-7 rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-7"><div className="flex flex-wrap items-end justify-between gap-4"><div><p className="text-xs font-bold uppercase tracking-[.15em] text-emerald-800">{plan.exam_type} · {new Date(plan.plan_date).toLocaleDateString()}</p><h2 className="mt-2 text-xl font-semibold">Your next three steps</h2></div><p className="text-sm font-semibold text-slate-500">{completedCount} / {plan.tasks.length} done · {plan.target_minutes} min</p></div><div className="mt-5 space-y-3">{plan.tasks.map((task) => <article key={task.id} className={`flex items-center gap-4 rounded-2xl border p-4 transition ${task.completed ? 'border-emerald-100 bg-emerald-50/70' : 'border-slate-200 bg-white'}`}><button type="button" aria-label={`${task.completed ? 'Completed' : 'Mark complete'}: ${task.title}`} disabled={task.completed || busy === task.id} onClick={() => void complete(task)} className={`grid h-9 w-9 shrink-0 place-items-center rounded-full border text-sm font-bold transition ${task.completed ? 'border-emerald-700 bg-emerald-700 text-white' : 'border-slate-300 text-transparent hover:border-emerald-700'} disabled:opacity-70`}>{task.completed ? '✓' : '✓'}</button><div className="min-w-0 flex-1"><p className={`text-sm font-semibold ${task.completed ? 'text-emerald-900' : 'text-slate-800'}`}>{task.title}</p><p className="mt-1 text-xs capitalize text-slate-500">{task.section} · {task.minutes} minutes</p></div><Link href={task.href} className="shrink-0 rounded-full bg-slate-100 px-3 py-2 text-xs font-bold text-slate-700 hover:bg-emerald-100 hover:text-emerald-900">Start <span aria-hidden="true">→</span></Link></article>)}</div>{completedCount === plan.tasks.length && <p role="status" className="mt-5 rounded-xl bg-emerald-50 p-4 text-sm font-semibold text-emerald-900">Lovely work. Your plan is complete for today.</p>}</section>}
  </div></main>;
}
