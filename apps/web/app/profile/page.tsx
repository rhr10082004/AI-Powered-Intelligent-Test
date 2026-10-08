'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import apiClient from '@/lib/api-client';

interface Profile {
  email: string;
  first_name: string | null;
  last_name: string | null;
}

export default function ProfilePage() {
  const router = useRouter();
  const [profile, setProfile] = useState<Profile>({ email: '', first_name: '', last_name: '' });
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [darkMode, setDarkMode] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const storedTheme = window.localStorage.getItem('study_theme') === 'dark';
    setDarkMode(storedTheme);
    document.documentElement.classList.toggle('dark', storedTheme);
    setNotificationsEnabled(window.localStorage.getItem('study_notifications') !== 'off');

    apiClient.get<Profile>('/users/me')
      .then((response) => setProfile(response.data))
      .catch(() => router.replace('/auth/login'));
  }, [router]);

  const saveProfile = async (event: React.FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setMessage('');
    try {
      const response = await apiClient.put<Profile>('/users/me', {
        first_name: profile.first_name,
        last_name: profile.last_name,
      });
      setProfile(response.data);
      window.localStorage.setItem('study_notifications', notificationsEnabled ? 'on' : 'off');
      setMessage('Profile settings saved.');
    } catch {
      setMessage('Could not save your profile. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 px-4 py-12 dark:bg-slate-900">
      <div className="mx-auto max-w-3xl rounded-2xl bg-white p-8 shadow-lg dark:bg-slate-800">
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-600">
              Account
            </p>
            <h1 className="mt-2 text-3xl font-bold text-slate-900 dark:text-white">Profile settings</h1>
          </div>
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-blue-100 text-xl font-bold text-blue-700 dark:bg-blue-900 dark:text-blue-200">
            {(profile.first_name?.[0] || profile.email[0] || 'S').toUpperCase()}
          </div>
        </div>

        <form className="mt-8 space-y-6" onSubmit={saveProfile}>
          <div className="grid gap-4 md:grid-cols-2">
            <label className="block">
              <span className="mb-2 block text-sm font-medium text-slate-700 dark:text-slate-200">First name</span>
              <input
                value={profile.first_name || ''}
                onChange={(event) => setProfile((current) => ({ ...current, first_name: event.target.value }))}
                className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-100"
              />
            </label>
            <label className="block">
              <span className="mb-2 block text-sm font-medium text-slate-700 dark:text-slate-200">Last name</span>
              <input
                value={profile.last_name || ''}
                onChange={(event) => setProfile((current) => ({ ...current, last_name: event.target.value }))}
                className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-100"
              />
            </label>
          </div>

          <label className="block">
            <span className="mb-2 block text-sm font-medium text-slate-700 dark:text-slate-200">Email</span>
            <input
              value={profile.email}
              type="email"
              readOnly
              className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-100"
            />
          </label>

          <div className="rounded-xl border border-slate-200 p-4 dark:border-slate-700">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Notifications</h2>
                <p className="text-sm text-slate-600 dark:text-slate-300">Get reminders for practice sessions and milestones.</p>
              </div>
              <button
                type="button"
                aria-label="Toggle notifications"
                aria-pressed={notificationsEnabled}
                onClick={() => {
                  const enabled = !notificationsEnabled;
                  setNotificationsEnabled(enabled);
                  window.localStorage.setItem('study_notifications', enabled ? 'on' : 'off');
                }}
                className={`relative h-7 w-12 rounded-full transition ${notificationsEnabled ? 'bg-blue-600' : 'bg-slate-300 dark:bg-slate-600'}`}
              >
                <span
                  className={`absolute top-1 h-5 w-5 rounded-full bg-white transition ${notificationsEnabled ? 'left-6' : 'left-1'}`}
                />
              </button>
            </div>
          </div>

          <div className="rounded-xl border border-slate-200 p-4 dark:border-slate-700">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Dark mode</h2>
                <p className="text-sm text-slate-600 dark:text-slate-300">Use the dark interface during evening sessions.</p>
              </div>
              <button
                type="button"
                aria-label="Toggle dark mode"
                aria-pressed={darkMode}
                onClick={() => {
                  const enabled = !darkMode;
                  setDarkMode(enabled);
                  document.documentElement.classList.toggle('dark', enabled);
                  window.localStorage.setItem('study_theme', enabled ? 'dark' : 'light');
                }}
                className={`relative h-7 w-12 rounded-full transition ${darkMode ? 'bg-blue-600' : 'bg-slate-300 dark:bg-slate-600'}`}
              >
                <span
                  className={`absolute top-1 h-5 w-5 rounded-full bg-white transition ${darkMode ? 'left-6' : 'left-1'}`}
                />
              </button>
            </div>
          </div>

          {message && <p className="text-sm text-slate-700 dark:text-slate-200" role="status">{message}</p>}
          <button type="submit" disabled={saving} className="w-full rounded-xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50">
            {saving ? 'Saving...' : 'Save changes'}
          </button>
        </form>
      </div>
    </div>
  );
}
