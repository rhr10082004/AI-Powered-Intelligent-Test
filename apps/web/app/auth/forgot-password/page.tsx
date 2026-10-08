'use client';

import Link from 'next/link';
import { FormEvent, useState } from 'react';
import apiClient from '@/lib/api-client';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [debugToken, setDebugToken] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  async function submit(event: FormEvent) {
    event.preventDefault(); setLoading(true); setError(''); setMessage(''); setDebugToken('');
    try {
      const response = await apiClient.post('/auth/password-reset/request', { email });
      setMessage(response.data.message);
      setDebugToken(response.data.debug_token || '');
    } catch { setError('We could not process the request right now. Please try again.'); }
    finally { setLoading(false); }
  }
  return <main className="flex min-h-screen items-center justify-center bg-[#f7f8f4] px-5 py-12 text-[#17251f]"><section className="motion-enter w-full max-w-md rounded-3xl border border-white bg-white p-7 shadow-xl sm:p-10"><Link href="/" className="text-sm font-bold text-emerald-800">Studywell</Link><p className="mt-8 text-xs font-bold uppercase tracking-[.18em] text-emerald-700">Account recovery</p><h1 className="mt-2 text-3xl font-semibold">Reset your password</h1><p className="mt-3 text-sm leading-6 text-slate-500">Enter the email on your account. If it exists, we’ll send a one-time reset link.</p><form onSubmit={submit} className="mt-7 space-y-4"><label className="block text-sm font-semibold">Email address<input type="email" required autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} className="mt-2 block w-full rounded-xl border border-slate-200 px-4 py-3 font-normal outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100" /></label>{error && <p role="alert" className="text-sm text-rose-700">{error}</p>}{message && <p role="status" className="rounded-xl bg-emerald-50 p-3 text-sm text-emerald-900">{message}</p>}{debugToken && <Link className="block rounded-xl bg-amber-50 p-3 text-sm font-semibold text-amber-900 underline" href={`/auth/reset-password?token=${encodeURIComponent(debugToken)}`}>Open local development reset link</Link>}<button disabled={loading} className="w-full rounded-full bg-[#173f32] px-5 py-3.5 text-sm font-bold text-white disabled:opacity-50">{loading ? 'Sending…' : 'Send reset link'}</button></form><p className="mt-6 text-center text-sm text-slate-500"><Link className="font-semibold text-emerald-800 underline" href="/auth/login">Back to sign in</Link></p></section></main>;
}
