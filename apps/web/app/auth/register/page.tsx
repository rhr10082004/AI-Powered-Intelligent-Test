'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Cookies from 'js-cookie';
import apiClient from '@/lib/api-client';

export default function RegisterPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({ email: '', password: '', confirmPassword: '', firstName: '', lastName: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (formData.password !== formData.confirmPassword) {
      setError('Your passwords do not match. Please check them and try again.');
      return;
    }
    if (formData.password.length < 8) {
      setError('Choose a password with at least 8 characters.');
      return;
    }
    setLoading(true);
    try {
      const response = await apiClient.post('/auth/register', {
        email: formData.email,
        password: formData.password,
        first_name: formData.firstName,
        last_name: formData.lastName,
      });
      Cookies.set('access_token', response.data.access_token);
      if (response.data.refresh_token) Cookies.set('refresh_token', response.data.refresh_token);
      try {
        const verification = await apiClient.post('/auth/email-verification/request', { email: formData.email });
        if (verification.data.debug_token) {
          router.push(`/auth/verify-email?token=${encodeURIComponent(verification.data.debug_token)}`);
          return;
        }
      } catch { /* Account creation succeeded; the learner can request verification later. */ }
      router.push('/onboarding');
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail;
      setError(detail || 'We couldn’t create your account. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const inputClass = 'block w-full rounded-2xl border border-[#dce4dc] bg-white px-4 py-3 text-sm text-[#20372a] outline-none transition placeholder:text-[#9aa69e] focus:border-[#5f9c75] focus:ring-4 focus:ring-[#5f9c75]/10';

  return (
    <main className="landing-shell relative flex min-h-screen items-center justify-center overflow-hidden bg-[#f7f8f4] px-5 py-10 text-[#17251f] sm:px-8">
      <div className="landing-orb landing-orb-one" aria-hidden="true" />
      <div className="landing-orb landing-orb-two" aria-hidden="true" />
      <Link href="/" className="absolute left-6 top-6 z-10 flex items-center gap-3 rounded-xl sm:left-10 sm:top-8">
        <span className="grid h-10 w-10 place-items-center rounded-2xl bg-[#173f32] text-lg font-bold text-white">S</span>
        <span className="text-sm font-bold">Studywell<span className="text-emerald-700">.</span></span>
      </Link>
      <div className="motion-enter relative z-[1] grid w-full min-w-0 grid-cols-1 max-w-5xl overflow-hidden rounded-[2rem] border border-white/80 bg-white/80 shadow-[0_30px_100px_-45px_rgba(24,62,46,.35)] backdrop-blur-xl lg:grid-cols-[.9fr_1.1fr]">
        <aside className="relative hidden min-h-[42rem] flex-col justify-between overflow-hidden bg-[#173f32] p-10 text-white lg:flex">
          <div className="absolute -right-24 -top-20 h-72 w-72 rounded-full border border-white/10 bg-white/5" aria-hidden="true" />
          <div className="absolute -bottom-32 -left-28 h-80 w-80 rounded-full border border-white/10 bg-emerald-200/10" aria-hidden="true" />
          <div className="relative"><p className="text-xs font-bold uppercase tracking-[.18em] text-emerald-100/70">Start with one step</p><h1 className="mt-8 max-w-sm text-4xl font-semibold leading-tight tracking-[-.04em]">Build a study habit that feels like yours.</h1><p className="mt-5 max-w-sm text-sm leading-7 text-emerald-50/75">Choose a goal, find your rhythm and let each focused session take you closer.</p></div>
          <div className="relative rounded-3xl border border-white/10 bg-white/[.08] p-5 backdrop-blur"><span className="text-2xl text-emerald-200" aria-hidden="true">✦</span><p className="mt-3 text-sm font-semibold">A fresh start can be a small one.</p><p className="mt-2 text-xs text-emerald-50/60">Your pace. Your plan.</p></div>
        </aside>
        <section className="px-6 py-10 sm:px-12 sm:py-12 lg:px-14">
          <p className="text-xs font-bold uppercase tracking-[.18em] text-[#679074]">Create your space</p>
          <h2 className="mt-3 text-3xl font-semibold tracking-[-.04em] text-[#1c3025]">Let’s get you started.</h2>
          <p className="mt-2 text-sm leading-6 text-[#718078]">A few details, then you can make a plan that fits.</p>
          <form className="mt-7 space-y-4" onSubmit={handleSubmit}>
            {error && <div role="alert" className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{error}</div>}
            <div className="grid gap-4 sm:grid-cols-2">
              <div><label htmlFor="firstName" className="mb-2 block text-sm font-semibold text-[#344b3e]">First name <span className="font-normal text-[#87938c]">(optional)</span></label><input id="firstName" name="firstName" type="text" autoComplete="given-name" className={inputClass} placeholder="Alex" value={formData.firstName} onChange={handleChange} /></div>
              <div><label htmlFor="lastName" className="mb-2 block text-sm font-semibold text-[#344b3e]">Last name <span className="font-normal text-[#87938c]">(optional)</span></label><input id="lastName" name="lastName" type="text" autoComplete="family-name" className={inputClass} placeholder="Morgan" value={formData.lastName} onChange={handleChange} /></div>
            </div>
            <div><label htmlFor="email" className="mb-2 block text-sm font-semibold text-[#344b3e]">Email address</label><input id="email" name="email" type="email" autoComplete="email" required className={inputClass} placeholder="you@example.com" value={formData.email} onChange={handleChange} /></div>
            <div><label htmlFor="password" className="mb-2 block text-sm font-semibold text-[#344b3e]">Password</label><input id="password" name="password" type="password" autoComplete="new-password" required minLength={8} className={inputClass} placeholder="At least 8 characters" value={formData.password} onChange={handleChange} /><p className="mt-2 text-xs text-[#87938c]">Use at least 8 characters.</p></div>
            <div><label htmlFor="confirmPassword" className="mb-2 block text-sm font-semibold text-[#344b3e]">Confirm password</label><input id="confirmPassword" name="confirmPassword" type="password" autoComplete="new-password" required minLength={8} className={inputClass} placeholder="Enter your password again" value={formData.confirmPassword} onChange={handleChange} /></div>
            <button type="submit" disabled={loading} className="group flex w-full items-center justify-center gap-2 rounded-full bg-[#173f32] px-6 py-4 text-sm font-bold text-white shadow-lg shadow-emerald-950/10 transition hover:-translate-y-0.5 hover:bg-[#245744] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-700 disabled:cursor-wait disabled:opacity-60">{loading ? 'Creating your account…' : 'Create account'} {!loading && <span aria-hidden="true" className="transition-transform group-hover:translate-x-1">→</span>}</button>
          </form>
          <p className="mt-6 text-center text-sm text-[#718078]">Already have an account? <Link href="/auth/login" className="font-bold text-[#35694e] underline decoration-[#b7d0bc] underline-offset-4 hover:text-[#173f32]">Sign in</Link></p>
        </section>
      </div>
    </main>
  );
}

