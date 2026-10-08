'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import apiClient from '@/lib/api-client';

export default function VerifyEmailPage() {
  const [status, setStatus] = useState('Checking your verification link…');
  const [error, setError] = useState(false);
  const [email, setEmail] = useState('');
  const [debugToken, setDebugToken] = useState('');
  const [sending, setSending] = useState(false);
  const [requestMode, setRequestMode] = useState(false);
  useEffect(() => {
    const token = new URLSearchParams(window.location.search).get('token');
    if (!token) { setRequestMode(true); setStatus('Enter your account email and we’ll send a fresh link.'); return; }
    apiClient.post('/auth/email-verification/confirm', { token })
      .then((response) => setStatus(response.data.message))
      .catch((cause: unknown) => {
        setError(true);
        setStatus((cause as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'This verification link could not be used.');
      });
  }, []);
  async function requestLink(event: React.FormEvent) {
    event.preventDefault(); setSending(true); setError(false); setDebugToken('');
    try {
      const response = await apiClient.post('/auth/email-verification/request', { email });
      setStatus(response.data.message); setDebugToken(response.data.debug_token || '');
    } catch { setStatus('We could not send a link right now. Please try again.'); setError(true); }
    finally { setSending(false); }
  }
  return <main className="flex min-h-screen items-center justify-center bg-[#f7f8f4] px-5 py-12 text-[#17251f]"><section className="motion-enter w-full max-w-md rounded-3xl bg-white p-8 text-center shadow-xl"><span className="mx-auto grid h-12 w-12 place-items-center rounded-full bg-emerald-50 text-xl text-emerald-800">{error ? '!' : '✓'}</span><h1 className="mt-5 text-2xl font-semibold">Email verification</h1>{requestMode ? <form onSubmit={requestLink} className="mt-5 text-left"><label className="block text-sm font-semibold">Email address<input type="email" required autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} className="mt-2 block w-full rounded-xl border border-slate-200 px-4 py-3 font-normal" /></label><button disabled={sending} className="mt-4 w-full rounded-full bg-[#173f32] px-6 py-3 text-sm font-bold text-white disabled:opacity-50">{sending ? 'Sending…' : 'Send verification link'}</button></form> : null}<p role="status" className="mt-3 text-sm leading-6 text-slate-600">{status}</p>{debugToken && <Link href={`/auth/verify-email?token=${encodeURIComponent(debugToken)}`} className="mt-3 block text-sm font-semibold text-amber-800 underline">Open local development verification link</Link>}<Link href="/auth/login" className="mt-6 inline-flex rounded-full bg-[#173f32] px-6 py-3 text-sm font-bold text-white">Continue to sign in</Link></section></main>;
}
