import Link from 'next/link';

const features = [
  { number: '01', title: 'Practice with purpose', description: 'Build confidence with focused reading, listening, vocabulary and grammar practice.', href: '/practice', label: 'Explore practice', tone: 'mint' },
  { number: '02', title: 'A tutor when you need one', description: 'Ask questions, work through tricky concepts and keep your learning moving.', href: '/tutor', label: 'Meet your tutor', tone: 'lavender' },
  { number: '03', title: 'See your progress grow', description: 'Review your practice history and get a clearer idea of what to focus on next.', href: '/auth/register', label: 'Start your journey', tone: 'peach' },
];

export default function Home() {
  return (
    <main className="landing-shell relative min-h-screen overflow-hidden bg-[#f7f8f4] text-[#17251f]">
      <div className="landing-orb landing-orb-one" aria-hidden="true" />
      <div className="landing-orb landing-orb-two" aria-hidden="true" />
      <header className="relative z-10 mx-auto flex w-full max-w-7xl items-center justify-between px-6 py-6 sm:px-10">
        <Link href="/" className="flex items-center gap-3 rounded-xl focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-emerald-700">
          <span className="grid h-10 w-10 place-items-center rounded-2xl bg-[#173f32] text-lg font-bold text-white shadow-lg shadow-emerald-950/10">S</span>
          <span className="text-sm font-bold tracking-tight sm:text-base">Studywell<span className="text-emerald-700">.</span></span>
        </Link>
        <nav aria-label="Main navigation" className="flex items-center gap-3 sm:gap-7">
          <Link href="/practice" className="hidden text-sm font-semibold text-[#54645b] transition hover:text-[#173f32] sm:inline">Explore practice</Link>
          <Link href="/auth/login" className="hidden rounded-full px-4 py-2.5 text-sm font-semibold text-[#173f32] transition hover:bg-white/70 sm:inline-flex">Sign in</Link>
          <Link href="/auth/register" className="rounded-full bg-[#173f32] px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-emerald-950/10 transition hover:-translate-y-0.5 hover:bg-[#245744] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-700">Get started <span aria-hidden="true">↗</span></Link>
        </nav>
      </header>

      <section className="relative z-[1] mx-auto grid min-w-0 grid-cols-1 items-center gap-12 px-6 pb-20 pt-12 sm:px-10 sm:pt-20 lg:max-w-7xl lg:grid-cols-[1.08fr_.92fr] lg:gap-8 lg:pb-28 lg:pt-24">
        <div className="motion-enter min-w-0 max-w-2xl">
          <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-emerald-900/10 bg-white/70 px-4 py-2 text-xs font-bold uppercase tracking-[.15em] text-emerald-900 shadow-sm backdrop-blur"><span className="h-2 w-2 animate-pulse rounded-full bg-[#83bd91]" /> Your next chapter starts here</div>
          <h1 className="max-w-2xl text-5xl font-semibold leading-[1.04] tracking-[-.055em] text-[#17251f] sm:text-6xl lg:text-[5.25rem]">Study smarter.<br /><span className="font-serif italic font-medium text-[#3b8064]">Feel ready.</span></h1>
          <p className="mt-7 max-w-xl text-base leading-7 text-[#627168] sm:text-lg sm:leading-8">A calmer, more personal way to prepare for your next exam. Practice in small steps, learn from every answer and build momentum that lasts.</p>
          <div className="mt-9 flex flex-col gap-3 sm:flex-row">
            <Link href="/auth/register" className="group inline-flex items-center justify-center gap-3 rounded-full bg-[#173f32] px-7 py-4 text-sm font-bold text-white shadow-xl shadow-emerald-950/15 transition hover:-translate-y-1 hover:bg-[#245744] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-700">Start learning <span className="transition-transform group-hover:translate-x-1" aria-hidden="true">→</span></Link>
            <Link href="/practice" className="inline-flex items-center justify-center gap-2 rounded-full border border-[#dce4dc] bg-white/65 px-7 py-4 text-sm font-bold text-[#315645] transition hover:border-[#9bb9a5] hover:bg-white">Explore practice <span aria-hidden="true">↗</span></Link>
          </div>
          <div className="mt-10 flex flex-wrap items-center gap-x-6 gap-y-3 text-xs font-semibold text-[#718078]"><span className="inline-flex items-center gap-2"><span className="text-[#3b8064]">✓</span> Learn at your own pace</span><span className="inline-flex items-center gap-2"><span className="text-[#3b8064]">✓</span> See what to work on next</span></div>
        </div>

        <div className="motion-enter relative mx-auto min-w-0 w-full max-w-xl lg:justify-self-end" style={{ animationDelay: '120ms' }}>
          <div className="study-card relative rounded-[2rem] border border-white/80 bg-white/85 p-5 shadow-[0_30px_100px_-45px_rgba(24,62,46,.35)] backdrop-blur-xl sm:p-7">
            <div className="flex items-start justify-between"><div><p className="text-xs font-bold uppercase tracking-[.16em] text-[#8a9a90]">Your study space</p><h2 className="mt-2 text-xl font-semibold tracking-tight text-[#1b2d24]">A little progress adds up.</h2></div><span className="grid h-11 w-11 place-items-center rounded-2xl bg-[#eaf3e9] text-xl text-[#3b8064]" aria-hidden="true">✦</span></div>
            <div className="mt-7 rounded-3xl bg-[#f1f6ef] p-5 sm:p-6">
              <div className="flex items-center justify-between gap-2 text-sm"><span className="font-semibold text-[#344b3e]">A balanced week</span><span className="rounded-full bg-white px-3 py-1 text-xs font-bold text-[#4c7c5e]">One step at a time</span></div>
              <div className="mt-6 grid grid-cols-7 gap-2" aria-label="Illustration of a weekly study rhythm">{['M', 'T', 'W', 'T', 'F', 'S', 'S'].map((day, index) => <div key={`${day}-${index}`} className="flex flex-col items-center gap-2"><span className="text-[10px] font-bold text-[#84938a]">{day}</span><span className={`h-9 w-full rounded-xl ${[0, 1, 3, 4].includes(index) ? 'bg-[#5f9c75]' : index === 2 ? 'bg-[#d6e8d5]' : 'bg-white'}`} /></div>)}</div>
              <div className="mt-5 flex items-center gap-3 border-t border-[#dce8da] pt-4"><div className="grid h-9 w-9 place-items-center rounded-full bg-[#dcebdc] text-sm" aria-hidden="true">✎</div><p className="text-xs leading-5 text-[#627168]">Short, focused sessions make a big goal feel closer.</p></div>
            </div>
            <div className="mt-5 grid grid-cols-2 gap-3"><div className="rounded-2xl border border-[#edf0eb] bg-white p-4"><span className="text-lg" aria-hidden="true">◌</span><p className="mt-2 text-xs font-bold text-[#344b3e]">Practice your way</p><p className="mt-1 text-[11px] text-[#87938c]">Four focused skills</p></div><div className="rounded-2xl border border-[#edf0eb] bg-white p-4"><span className="text-lg" aria-hidden="true">⌁</span><p className="mt-2 text-xs font-bold text-[#344b3e]">Keep your momentum</p><p className="mt-1 text-[11px] text-[#87938c]">Progress that is yours</p></div></div>
          </div>
          <div className="float-note absolute -left-5 top-24 hidden rounded-2xl border border-white bg-white/90 px-4 py-3 shadow-xl shadow-emerald-950/10 sm:block lg:-left-12"><span className="text-xs font-bold text-[#3b8064]">✦ Small wins count</span></div>
          <div className="float-note float-note-later absolute -bottom-5 right-6 hidden rounded-2xl border border-white bg-white/90 px-4 py-3 shadow-xl shadow-emerald-950/10 sm:block"><span className="text-xs font-bold text-[#3b8064]">Your pace. Your plan.</span></div>
        </div>
      </section>

      <section className="relative z-[1] mx-auto max-w-7xl px-6 pb-20 sm:px-10 lg:pb-28" aria-labelledby="features-title">
        <div className="flex flex-col justify-between gap-4 border-t border-[#dfe6de] pt-10 sm:flex-row sm:items-end"><div><p className="text-xs font-bold uppercase tracking-[.18em] text-[#679074]">Made for your goals</p><h2 id="features-title" className="mt-3 text-3xl font-semibold tracking-[-.04em] text-[#1c3025] sm:text-4xl">Everything you need to move forward.</h2></div><p className="max-w-sm text-sm leading-6 text-[#718078]">A focused toolkit for exam prep, designed to make your next step feel simple.</p></div>
        <div className="motion-stagger mt-8 grid min-w-0 grid-cols-1 gap-4 md:grid-cols-3">{features.map((feature) => <Link key={feature.number} href={feature.href} className={`feature-card feature-${feature.tone} group rounded-[1.75rem] border border-white/80 p-6 transition duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-emerald-950/5 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-700 sm:p-7`}><div className="flex items-center justify-between"><span className="text-xs font-bold tracking-[.15em] text-[#6e8175]">{feature.number}</span><span className="grid h-10 w-10 place-items-center rounded-full bg-white/80 text-[#36664b] transition-transform group-hover:translate-x-1" aria-hidden="true">↗</span></div><h3 className="mt-8 text-xl font-semibold tracking-tight text-[#20372a]">{feature.title}</h3><p className="mt-3 min-h-[3rem] text-sm leading-6 text-[#64746a]">{feature.description}</p><span className="mt-6 inline-block text-xs font-bold text-[#35694e]">{feature.label} <span aria-hidden="true">→</span></span></Link>)}</div>
      </section>
      <footer className="relative z-[1] border-t border-[#dfe6de] px-6 py-6 text-center text-xs text-[#829087] sm:px-10">A more thoughtful way to prepare. <span className="font-semibold text-[#587263]">Studywell</span></footer>
    </main>
  );
}
