import Link from 'next/link';
import PracticeCatalog from './PracticeCatalog';

const modules = [
  { icon: '◫', title: 'Reading practice', text: 'Build focus and comprehension with exam-style passages.', href: '/practice/reading', color: 'bg-blue-50 text-blue-700', action: 'Explore passages' },
  { icon: '♫', title: 'Listening practice', text: 'Train your ear with audio clips and thoughtful questions.', href: '/practice/listening', color: 'bg-amber-50 text-amber-700', action: 'Start listening' },
  { icon: 'Aa', title: 'Vocabulary builder', text: 'Grow your word bank with a review rhythm that sticks.', href: '/practice/vocabulary', color: 'bg-violet-50 text-violet-700', action: 'Study words' },
  { icon: '✳', title: 'Grammar studio', text: 'Make grammar feel natural with short interactive exercises.', href: '/practice/grammar', color: 'bg-emerald-50 text-emerald-700', action: 'Practice grammar' },
  { icon: '✎', title: 'Writing coach', text: 'Draft an essay and get a criterion-by-criterion practice review.', href: '/practice/writing', color: 'bg-rose-50 text-rose-700', action: 'Open writing coach' },
  { icon: 'Mic', title: 'Speaking practice', text: 'Answer a prompt aloud, review your transcript and plan a stronger next attempt.', href: '/practice/speaking', color: 'bg-sky-50 text-sky-700', action: 'Practice speaking' },
];

export default function PracticePage() {
  return <PracticeCatalog />;

  return (
    <main className="min-h-screen overflow-x-hidden bg-[#f8f8f5] px-5 py-10 text-slate-900 sm:px-8 lg:py-14">
      <div className="mx-auto w-full min-w-0 max-w-6xl">
        <Link href="/dashboard" className="text-sm font-semibold text-slate-500 transition hover:text-slate-900">← Dashboard</Link>
        <section className="motion-enter relative mt-7 overflow-hidden rounded-[2rem] bg-[#203d35] px-7 py-9 text-white shadow-xl shadow-emerald-950/10 sm:px-12 sm:py-12">
          <div className="absolute -right-14 -top-24 h-72 w-72 rounded-full bg-[#a9c9a7]/20 blur-3xl" />
          <p className="relative text-xs font-bold uppercase tracking-[.2em] text-[#bdd7bb]">Your learning space</p>
          <h1 className="relative mt-3 max-w-2xl text-3xl font-semibold tracking-tight sm:text-5xl">Small practice. <span className="font-serif italic text-[#c9e0c2]">Real progress.</span></h1>
          <p className="relative mt-4 max-w-xl text-sm leading-7 text-white/75 sm:text-base">Choose a skill, find your rhythm, and turn a little practice into a lot of confidence.</p>
          <div className="relative mt-7 flex flex-wrap gap-2 text-xs font-semibold text-white/85"><span className="rounded-full bg-white/10 px-3 py-2">✦ Bite-sized sessions</span><span className="rounded-full bg-white/10 px-3 py-2">↗ Progress you can see</span></div>
        </section>
        <div className="motion-enter mt-10 flex items-end justify-between gap-4" style={{ animationDelay: '100ms' }}>
          <div><p className="text-xs font-bold uppercase tracking-[.18em] text-emerald-800">Explore by skill</p><h2 className="mt-2 text-2xl font-semibold tracking-tight sm:text-3xl">What would you like to work on?</h2></div>
          <span className="hidden rounded-full border border-slate-200 bg-white px-4 py-2 text-xs font-semibold text-slate-500 sm:block">5 learning paths</span>
        </div>
        <Link href="/practice/diagnostic" className="mt-5 inline-flex items-center gap-3 rounded-2xl border border-emerald-200 bg-emerald-50 px-5 py-3 text-sm font-bold text-emerald-900 transition hover:border-emerald-400 hover:bg-emerald-100"><span className="grid h-9 w-9 place-items-center rounded-xl bg-white text-lg" aria-hidden="true">◎</span><span>Take a quick diagnostic <span className="ml-1 text-xs font-medium text-emerald-800/70">5 questions · save your baseline</span></span><span aria-hidden="true">→</span></Link>
        <div className="motion-stagger mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {modules.map((module) => <Link key={module.title} href={module.href} className="group min-w-0 rounded-3xl border border-slate-200/80 bg-white p-6 shadow-sm transition duration-300 hover:-translate-y-1 hover:border-emerald-200 hover:shadow-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-700">
            <span className={`grid h-12 w-12 place-items-center rounded-2xl text-xl font-semibold ${module.color}`}>{module.icon}</span>
            <h3 className="mt-5 text-lg font-semibold">{module.title}</h3><p className="mt-2 min-h-[3rem] text-sm leading-6 text-slate-500">{module.text}</p>
            <span className="mt-5 inline-flex items-center gap-2 text-sm font-bold text-emerald-800">{module.action}<span className="transition group-hover:translate-x-1" aria-hidden="true">→</span></span>
          </Link>)}
        </div>
        <p className="mt-8 text-center text-xs leading-5 text-slate-400">Practice feedback is designed to support learning; exam estimates are not official scores.</p>
      </div>
    </main>
  );
}
