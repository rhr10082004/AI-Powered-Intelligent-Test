'use client';

import Link from 'next/link';
import { ArrowRight, ArrowUpRight, BookOpen, CalendarDays, Clock3, Flame, Headphones, LogOut, PenLine, Sparkles, Target, Trophy } from 'lucide-react';

type User = { email: string; first_name: string | null; is_verified: boolean };
type ProgressItem = { exam_id: string; section: string; total_questions: number; correct_answers: number; accuracy: number | null };
type Recommendation = { section: string; title: string; reason: string; href: string; accuracy_percent: number | null };
type Achievement = { id: string; title: string; description: string; current: number; target: number; unlocked: boolean };
type StudySession = { id: string; section: string; session_date: string; duration: number; questions_attempted: number; questions_correct: number; accuracy: number | null };
type ActivitySummary = { total_points: number; level: number; points_to_next_level: number; total_events: number; events_last_7_days: number };
type Day = { label: string; accuracy: number | null; count: number };

type Props = {
  user: User;
  progress: ProgressItem[];
  recommendations: Recommendation[];
  achievements: Achievement[];
  studySessions: StudySession[];
  activitySummary: ActivitySummary | null;
  recentDays: Day[];
  totalQuestions: number;
  totalCorrect: number;
  overallAccuracy: number;
  onLogout: () => void;
  onExport: () => void;
};

const quickLinks = [
  { title: 'Reading', description: 'Build comprehension', href: '/practice/reading', icon: BookOpen, color: 'bg-[#e8f2e9] text-[#35694e]' },
  { title: 'Listening', description: 'Train your focus', href: '/practice/listening', icon: Headphones, color: 'bg-[#fff2df] text-[#96601f]' },
  { title: 'Writing', description: 'Shape stronger ideas', href: '/practice/writing', icon: PenLine, color: 'bg-[#f8e9e7] text-[#9b5145]' },
  { title: 'Study plan', description: 'Take your next small step', href: '/study-plan', icon: CalendarDays, color: 'bg-[#eceafa] text-[#6256a1]' },
];

export default function DashboardOverview({ user, progress, recommendations, achievements, studySessions, activitySummary, recentDays, totalQuestions, totalCorrect, overallAccuracy, onLogout, onExport }: Props) {
  const firstName = user.first_name || user.email.split('@')[0];
  const activeDays = recentDays.filter((day) => day.count > 0).length;
  const nextSteps = recommendations.slice(0, 2);
  const milestones = achievements.slice(0, 3);
  const sessions = studySessions.slice(0, 5);

  return (
    <main className="min-h-screen overflow-x-hidden bg-[#f6f7f2] px-4 py-5 text-[#1b3025] sm:px-7 sm:py-8 lg:px-10">
      <div className="mx-auto w-full max-w-7xl">
        <header className="flex items-center justify-between gap-4">
          <Link href="/" className="flex items-center gap-3" aria-label="Studywell home"><span className="grid h-10 w-10 place-items-center rounded-2xl bg-[#173f32] text-lg font-black text-white shadow-sm">S</span><span className="text-sm font-extrabold tracking-tight">Studywell<span className="text-emerald-700">.</span></span></Link>
          <nav className="hidden items-center gap-6 text-sm font-semibold text-[#708078] sm:flex" aria-label="Main navigation"><Link href="/practice" className="transition hover:text-[#173f32]">Practice</Link><Link href="/tutor" className="transition hover:text-[#173f32]">Tutor</Link><Link href="/profile" className="transition hover:text-[#173f32]">Profile</Link></nav>
          <div className="flex items-center gap-2"><Link href="/profile" className="grid h-10 w-10 place-items-center rounded-full bg-[#dfeadf] text-sm font-bold text-[#28523d]" aria-label="Open profile">{firstName[0]?.toUpperCase()}</Link><button type="button" onClick={onLogout} className="inline-flex items-center gap-2 rounded-full border border-[#dce4dc] bg-white px-3 py-2 text-xs font-bold text-[#66766d] transition hover:border-rose-200 hover:text-rose-700" aria-label="Sign out"><LogOut size={15}/><span className="hidden sm:inline">Sign out</span></button></div>
        </header>

        <section className="motion-enter relative mt-7 overflow-hidden rounded-[2rem] bg-[#1c4034] px-6 py-7 text-white shadow-[0_25px_80px_-45px_rgba(19,58,42,.6)] sm:px-10 sm:py-9 lg:px-12">
          <div aria-hidden="true" className="absolute -right-12 -top-28 h-72 w-72 rounded-full border border-white/10 bg-white/[.04]"/><div aria-hidden="true" className="absolute -right-2 -top-16 h-52 w-52 rounded-full border border-white/[.08]"/><div aria-hidden="true" className="absolute -bottom-32 right-44 h-64 w-64 rounded-full bg-[#9bc8a2]/10 blur-3xl"/>
          <div className="relative flex flex-col justify-between gap-8 md:flex-row md:items-end"><div><p className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/[.08] px-3 py-1.5 text-[11px] font-bold uppercase tracking-[.15em] text-[#c4ddc5]"><Sparkles size={13}/> Your learning space</p><h1 className="mt-5 max-w-2xl text-3xl font-semibold tracking-[-.04em] sm:text-5xl">A little progress, <span className="font-serif italic text-[#bad8bc]">every day.</span></h1><p className="mt-3 max-w-xl text-sm leading-6 text-white/70">Welcome back, {firstName}. Pick up where you left off and keep building confidence at your own pace.</p></div><Link href="/practice" className="group inline-flex w-fit shrink-0 items-center gap-3 rounded-full bg-[#e4efe1] px-5 py-3.5 text-sm font-bold text-[#1b4032] shadow-lg transition hover:-translate-y-0.5 hover:bg-white">Start a practice session <ArrowRight size={17} className="transition-transform group-hover:translate-x-1"/></Link></div>
          <div className="relative mt-8 grid grid-cols-2 gap-3 border-t border-white/10 pt-5 sm:grid-cols-4">
            <div><p className="text-[11px] font-semibold uppercase tracking-wider text-white/55">Study rhythm</p><p className="mt-1 flex items-center gap-2 text-xl font-bold"><Flame size={17} className="text-[#f6c27a]"/>{activeDays}<span className="text-xs font-medium text-white/60">active days</span></p></div>
            <div><p className="text-[11px] font-semibold uppercase tracking-wider text-white/55">Questions tried</p><p className="mt-1 text-xl font-bold">{totalQuestions}</p></div>
            <div><p className="text-[11px] font-semibold uppercase tracking-wider text-white/55">Your accuracy</p><p className="mt-1 text-xl font-bold">{overallAccuracy}%</p></div>
            <div><p className="text-[11px] font-semibold uppercase tracking-wider text-white/55">Learner level</p><p className="mt-1 flex items-center gap-2 text-xl font-bold"><Trophy size={17} className="text-[#f6c27a]"/>{activitySummary?.level??1}<span className="text-xs font-medium text-white/60">{activitySummary?.total_points??0} points</span></p></div>
          </div>
        </section>

        <section className="mt-8" aria-labelledby="continue-heading"><div className="mb-4 flex items-end justify-between gap-3"><div><p className="text-[11px] font-bold uppercase tracking-[.18em] text-[#76917d]">Your toolkit</p><h2 id="continue-heading" className="mt-1 text-xl font-semibold tracking-tight sm:text-2xl">Where to next?</h2></div><Link href="/practice" className="inline-flex items-center gap-1 text-xs font-bold text-[#35694e] hover:underline">All practice <ArrowUpRight size={14}/></Link></div>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">{quickLinks.map(({title,description,href,icon:Icon,color})=><Link key={title} href={href} className="group rounded-3xl border border-[#e5eae2] bg-white p-5 shadow-[0_4px_18px_-14px_rgba(21,47,32,.25)] transition duration-200 hover:-translate-y-1 hover:border-[#c6d8c8] hover:shadow-lg focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#35694e]"><div className="flex items-start justify-between"><span className={`grid h-11 w-11 place-items-center rounded-2xl ${color}`}><Icon size={20}/></span><ArrowUpRight size={17} className="text-[#a3b0a7] transition group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-[#35694e]"/></div><h3 className="mt-5 font-bold">{title}</h3><p className="mt-1 text-xs text-[#7b8980]">{description}</p></Link>)}</div>
        </section>

        <div className="mt-5 grid gap-5 lg:grid-cols-[minmax(0,1.4fr)_minmax(290px,.8fr)]">
          <section className="rounded-3xl border border-[#e5eae2] bg-white p-5 shadow-sm sm:p-6" aria-labelledby="progress-heading"><div className="flex flex-wrap items-start justify-between gap-3"><div><p className="text-[11px] font-bold uppercase tracking-[.16em] text-[#76917d]">Your rhythm</p><h2 id="progress-heading" className="mt-1 text-lg font-bold">Weekly practice</h2><p className="mt-1 text-xs text-[#829087]">{activeDays?`${activeDays} of 7 days with a completed session`:'Finish a practice set to start your weekly view.'}</p></div><button type="button" onClick={onExport} disabled={!studySessions.length} className="rounded-full border border-[#dce4dc] px-3 py-2 text-xs font-bold text-[#53665a] transition hover:border-[#8aaf91] hover:text-[#28523d] disabled:cursor-not-allowed disabled:opacity-40">Export CSV</button></div>
            <div className="mt-7 grid grid-cols-7 gap-2 sm:gap-3" role="img" aria-label={`Weekly accuracy chart. ${recentDays.filter((day)=>day.accuracy!==null).length} days include sessions.`}>{recentDays.map((day,index)=><div key={`${day.label}-${index}`} className="flex min-w-0 flex-col items-center gap-2"><div className="flex h-28 w-full items-end rounded-2xl bg-[#f2f5ef] p-1" title={day.accuracy===null?'No practice session':`${day.accuracy}% accuracy, ${day.count} sessions`}><div className={`w-full rounded-xl transition-[height] duration-700 ${day.accuracy===null?'bg-[#dfe7dc]':'bg-gradient-to-t from-[#397252] to-[#8db996]'}`} style={{height:`${Math.max(day.accuracy??0,day.count?8:4)}%`}}/></div><span className="text-[10px] font-semibold text-[#859188]">{day.label}</span></div>)}</div>
            <div className="mt-6 grid gap-2 sm:grid-cols-2">{progress.length?progress.slice(0,4).map((item)=><div key={`${item.exam_id}-${item.section}`} className="flex items-center justify-between rounded-2xl bg-[#f8f9f6] px-4 py-3"><div><p className="text-xs font-bold capitalize text-[#40574a]">{item.section}</p><p className="mt-1 text-[11px] text-[#89958c]">{item.correct_answers} / {item.total_questions} correct</p></div><span className="text-sm font-extrabold text-[#35694e]">{Math.round((item.accuracy??0)*100)}%</span></div>):<div className="rounded-2xl bg-[#f8f9f6] px-4 py-3 text-xs text-[#829087] sm:col-span-2">Your section breakdown will appear after your first practice session.</div>}</div>
          </section>

          <section className="rounded-3xl border border-[#e5eae2] bg-[#edf3e9] p-5 sm:p-6" aria-labelledby="next-step-heading"><p className="text-[11px] font-bold uppercase tracking-[.16em] text-[#698571]">Made for you</p><h2 id="next-step-heading" className="mt-1 text-lg font-bold">Your next step</h2>{nextSteps.length?<div className="mt-4 space-y-3">{nextSteps.map((rec)=><Link key={`${rec.section}-${rec.href}`} href={rec.href} className="group block rounded-2xl border border-white/90 bg-white/85 p-4 transition hover:bg-white hover:shadow-sm"><div className="flex items-start justify-between gap-3"><p className="text-sm font-bold text-[#2c4738]">{rec.title}</p><ArrowUpRight size={16} className="shrink-0 text-[#809186] transition group-hover:text-[#35694e]"/></div><p className="mt-2 text-xs leading-5 text-[#75847a]">{rec.reason}</p>{rec.accuracy_percent!==null&&<div className="mt-3 h-1.5 overflow-hidden rounded-full bg-[#e9efe7]"><div className="h-full rounded-full bg-[#659873]" style={{width:`${Math.max(4,Math.min(100,rec.accuracy_percent))}%`}}/></div>}</Link>)}</div>:<div className="mt-4 rounded-2xl bg-white/80 p-4"><p className="text-sm font-semibold text-[#40574a]">Your plan is ready when you are.</p><p className="mt-1 text-xs leading-5 text-[#75847a]">Try a short session and we&apos;ll suggest what to focus on next.</p><Link href="/practice/diagnostic" className="mt-3 inline-flex items-center gap-1 text-xs font-bold text-[#35694e]">Take a quick diagnostic <ArrowRight size={14}/></Link></div>}<Link href="/study-plan" className="mt-4 flex items-center justify-between rounded-2xl bg-[#1d4034] px-4 py-3 text-xs font-bold text-white transition hover:bg-[#2d5845]"><span className="flex items-center gap-2"><CalendarDays size={15}/> Open today&apos;s plan</span><ArrowRight size={15}/></Link></section>
        </div>

        <div className="mt-5 grid gap-5 lg:grid-cols-2">
          <section className="rounded-3xl border border-[#e5eae2] bg-white p-5 shadow-sm sm:p-6" aria-labelledby="milestones-heading"><div className="flex items-center justify-between"><div><p className="text-[11px] font-bold uppercase tracking-[.16em] text-[#76917d]">Keep it going</p><h2 id="milestones-heading" className="mt-1 text-lg font-bold">Milestones</h2></div><Trophy size={20} className="text-[#c58a3f]"/></div>{milestones.length?<div className="mt-4 space-y-3">{milestones.map((item)=><div key={item.id} className="rounded-2xl bg-[#f8f9f6] p-4"><div className="flex justify-between gap-3"><p className="text-sm font-bold text-[#40574a]">{item.title}</p><span className="text-xs font-bold text-[#7b8b80]">{item.current}/{item.target}</span></div><p className="mt-1 text-xs text-[#89958c]">{item.description}</p><div className="mt-3 h-1.5 overflow-hidden rounded-full bg-[#e6ebe4]"><div className={`h-full rounded-full ${item.unlocked?'bg-[#4b8c60]':'bg-[#9ab99b]'}`} style={{width:`${Math.min(100,item.current/Math.max(item.target,1)*100)}%`}}/></div></div>)}</div>:<p className="mt-4 text-sm text-[#829087]">Practice milestones will appear here as you build your routine.</p>}<div className="mt-4 rounded-2xl bg-[#fdf4e8] p-4"><div className="flex items-center justify-between gap-3"><div><p className="text-xs font-bold text-[#74552e]">Level {activitySummary?.level??1} learner</p><p className="mt-1 text-[11px] text-[#92764f]">{activitySummary?.points_to_next_level??100} points to your next level</p></div><span className="rounded-full bg-white px-3 py-2 text-xs font-extrabold text-[#886b42]">{activitySummary?.total_points??0} pts</span></div></div></section>

          <section className="rounded-3xl border border-[#e5eae2] bg-white p-5 shadow-sm sm:p-6" aria-labelledby="sessions-heading"><div className="flex items-center justify-between gap-3"><div><p className="text-[11px] font-bold uppercase tracking-[.16em] text-[#76917d]">Your history</p><h2 id="sessions-heading" className="mt-1 text-lg font-bold">Recent sessions</h2></div><Clock3 size={19} className="text-[#809186]"/></div>{sessions.length?<ul className="mt-3 divide-y divide-[#eef1ec]">{sessions.map((session)=><li key={session.id} className="flex items-center justify-between gap-3 py-3"><div className="flex min-w-0 items-center gap-3"><span className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-[#edf3e9] text-[#467653]"><Target size={17}/></span><div className="min-w-0"><p className="truncate text-xs font-bold capitalize text-[#40574a]">{session.section} practice</p><p className="mt-1 text-[10px] text-[#8a968d]">{new Date(session.session_date).toLocaleDateString()} · {Math.round(session.duration/60)} min</p></div></div><span className="shrink-0 rounded-full bg-[#f1f5ef] px-3 py-1.5 text-[11px] font-bold text-[#4b7155]">{session.questions_correct}/{session.questions_attempted}</span></li>)}</ul>:<div className="mt-4 rounded-2xl bg-[#f8f9f6] p-4"><p className="text-sm font-semibold text-[#40574a]">Your first session is waiting.</p><p className="mt-1 text-xs text-[#89958c]">Choose a skill and complete a short set to see your progress.</p></div>}</section>
        </div>
        <footer className="mt-8 flex flex-col items-center justify-between gap-3 border-t border-[#e5eae2] py-5 text-[11px] text-[#92a096] sm:flex-row"><p>{user.is_verified?'Account verified':'Email verification recommended'} · {totalCorrect} correct answers logged</p><div className="flex gap-4"><Link href="/profile" className="hover:text-[#35694e]">Profile settings</Link><Link href="/exams" className="hover:text-[#35694e]">Exam goals</Link><button type="button" onClick={onExport} disabled={!studySessions.length} className="hover:text-[#35694e] disabled:opacity-40">Download progress</button></div></footer>
      </div>
    </main>
  );
}
