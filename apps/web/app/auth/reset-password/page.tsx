'use client';

import Link from 'next/link';
import { FormEvent, useEffect, useState } from 'react';
import apiClient from '@/lib/api-client';

export default function ResetPasswordPage() {
  const [token, setToken] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  useEffect(() => { setToken(new URLSearchParams(window.location.search).get('token') || ''); }, []);
  async function submit(event: FormEvent) {
    event.preventDefault(); setLoading(true); setError('');
    try { const result = await apiClient.post('/auth/password-reset/confirm', { token, password }); setMessage(result.data.message); }
    catch (cause: unknown) { setError((cause as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Could not update the password. Request a fresh link and try again.'); }
    finally { setLoading(false); }
  }
  return <main className="flex min-h-screen items-center justify-center bg-[#f7f8f4] px-5 py-12 text-[#17251f]"><section className="motion-enter w-full max-w-md rounded-3xl bg-white p-7 shadow-xl sm:p-10"><Link href="/" className="text-sm font-bold text-emerald-800">Studywell</Link><h1 className="mt-8 text-3xl font-semibold">Choose a new password</h1><p className="mt-3 text-sm text-slate-500">Use at least 8 characters. The reset link can only be used once.</p><form onSubmit={submit} className="mt-7 space-y-4"><label className="block text-sm font-semibold">New password<input type="password" required minLength={8} maxLength={128} autoComplete="new-password" value={password} onChange={(e) => setPassword(e.target.value)} className="mt-2 block w-full rounded-xl border border-slate-200 px-4 py-3 font-normal outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100" /></label>{error && <p role="alert" className="text-sm text-rose-700">{error}</p>}{message && <p role="status" className="rounded-xl bg-emerald-50 p-3 text-sm text-emerald-900">{message}</p>}<button disabled={loading || !token} className="w-full rounded-full bg-[#173f32] px-5 py-3.5 text-sm font-bold text-white disabled:opacity-50">{loading ? 'Updating…' : 'Update password'}</button></form><Link href="/auth/login" className="mt-6 block text-center text-sm font-semibold text-emerald-800 underline">Go to sign in</Link></section></main>;
}
