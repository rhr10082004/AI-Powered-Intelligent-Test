'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Cookies from 'js-cookie';
import apiClient from '@/lib/api-client';
import DashboardOverview from './DashboardOverview';

interface User {
  id: string;
  email: string;
  first_name: string | null;
  last_name: string | null;
  avatar_url: string | null;
  is_verified: boolean;
  created_at: string;
}

interface ProgressItem {
  exam_id: string;
  section: string;
  total_questions: number;
  correct_answers: number;
  accuracy: number | null;
}

interface StudyRecommendation {
  section: string;
  title: string;
  reason: string;
  href: string;
  accuracy_percent: number | null;
}

interface Achievement {
  id: string;
  title: string;
  description: string;
  current: number;
  target: number;
  unlocked: boolean;
}

interface StudySession {
  id: string;
  section: string;
  session_date: string;
  duration: number;
  questions_attempted: number;
  questions_correct: number;
  accuracy: number | null;
}

interface ActivitySummary {
  total_points: number;
  level: number;
  points_to_next_level: number;
  total_events: number;
  events_last_7_days: number;
}

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User>({ id: '', email: '', first_name: null, last_name: null, avatar_url: null, is_verified: false, created_at: '' });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [progress, setProgress] = useState<ProgressItem[]>([]);
  const [recommendations, setRecommendations] = useState<StudyRecommendation[]>([]);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [studySessions, setStudySessions] = useState<StudySession[]>([]);
  const [activitySummary, setActivitySummary] = useState<ActivitySummary | null>(null);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const token = Cookies.get('access_token');
        if (!token) {
          router.push('/auth/login');
          return;
        }

        const response = await apiClient.get('/users/me');

        setUser(response.data);
        const [progressResponse, recommendationResponse, achievementResponse, sessionsResponse, activityResponse] = await Promise.all([
          apiClient.get<ProgressItem[]>('/progress/my-summary'),
          apiClient.get<StudyRecommendation[]>('/study-plan/recommendations'),
          apiClient.get<Achievement[]>('/achievements'),
          apiClient.get<StudySession[]>('/study-sessions/my-sessions?limit=20'),
          apiClient.get<ActivitySummary>('/activity/summary'),
        ]);
        setProgress(progressResponse.data);
        setRecommendations(recommendationResponse.data);
        setAchievements(achievementResponse.data);
        setStudySessions(sessionsResponse.data);
        setActivitySummary(activityResponse.data);
      } catch {
        setError('Failed to load user profile');
        Cookies.remove('access_token');
        Cookies.remove('refresh_token');
        router.push('/auth/login');
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [router]);

  const handleLogout = () => {
    Cookies.remove('access_token');
    Cookies.remove('refresh_token');
    router.push('/auth/login');
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-gray-300 border-t-blue-600"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  if (error || !user.email) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 dark:text-red-400">{error}</p>
        </div>
      </div>
    );
  }

  const totalQuestions = progress.reduce((total, item) => total + item.total_questions, 0);
  const totalCorrect = progress.reduce((total, item) => total + item.correct_answers, 0);
  const overallAccuracy = totalQuestions ? Math.round((totalCorrect / totalQuestions) * 100) : 0;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const recentDays = Array.from({ length: 7 }, (_, index) => {
    const day = new Date(today);
    day.setDate(today.getDate() - (6 - index));
    const daySessions = studySessions.filter((session) => {
      const sessionDay = new Date(session.session_date);
      sessionDay.setHours(0, 0, 0, 0);
      return sessionDay.getTime() === day.getTime();
    });
    const accuracy = daySessions.length
      ? Math.round(daySessions.reduce((sum, session) => sum + (session.accuracy ?? (session.questions_attempted ? session.questions_correct / session.questions_attempted : 0)), 0) / daySessions.length * 100)
      : null;
    return { label: day.toLocaleDateString(undefined, { weekday: 'short' }), accuracy, count: daySessions.length };
  });

  const exportProgress = () => {
    const rows = [
      ['Date', 'Section', 'Questions', 'Correct', 'Accuracy percent', 'Duration minutes'],
      ...studySessions.map((session) => [
        new Date(session.session_date).toISOString(), session.section, session.questions_attempted,
        session.questions_correct, Math.round((session.accuracy ?? 0) * 100), Math.round(session.duration / 60),
      ]),
    ];
    const csv = rows.map((row) => row.map((value) => `"${String(value).replace(/"/g, '""')}"`).join(',')).join('\n');
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = 'studywell-progress.csv';
    link.click();
    URL.revokeObjectURL(url);
  };

  return <DashboardOverview user={user} progress={progress} recommendations={recommendations} achievements={achievements} studySessions={studySessions} activitySummary={activitySummary} recentDays={recentDays} totalQuestions={totalQuestions} totalCorrect={totalCorrect} overallAccuracy={overallAccuracy} onLogout={handleLogout} onExport={exportProgress} />;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Dashboard
          </h1>
          <button
            onClick={handleLogout}
            className="rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
          >
            Logout
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid gap-8 md:grid-cols-3">
          {/* User Card */}
          <div className="md:col-span-1 rounded-lg bg-white dark:bg-gray-800 shadow p-6">
            <div className="flex items-center space-x-4">
              <div className="h-16 w-16 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                <span className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                  {user.first_name?.[0]?.toUpperCase() || user.email[0].toUpperCase()}
                </span>
              </div>
              <div>
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  {user.first_name && user.last_name
                    ? `${user.first_name} ${user.last_name}`
                    : user.email}
                </h2>
                <p className="text-sm text-gray-600 dark:text-gray-400">{user.email}</p>
                <div className="mt-2">
                  {user.is_verified ? (
                    <span className="inline-block bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 px-2 py-1 rounded text-xs font-semibold">
                      Verified
                    </span>
                  ) : (
                    <span className="inline-block bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 px-2 py-1 rounded text-xs font-semibold">
                      Not Verified
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="md:col-span-2 rounded-lg bg-white dark:bg-gray-800 shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Quick Actions
            </h3>
            <div className="grid gap-4 sm:grid-cols-2">
              <a
                href="/exams"
                className="flex items-center justify-center rounded-lg border-2 border-gray-300 dark:border-gray-600 p-6 hover:border-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/10 transition"
              >
                <div className="text-center">
                  <div className="text-2xl mb-2">▦</div>
                  <p className="font-semibold text-gray-900 dark:text-white">
                    Select Exams
                  </p>
                </div>
              </a>
              <a
                href="/practice"
                className="flex items-center justify-center rounded-lg border-2 border-gray-300 dark:border-gray-600 p-6 hover:border-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/10 transition"
              >
                <div className="text-center">
                  <div className="text-2xl mb-2">✦</div>
                  <p className="font-semibold text-gray-900 dark:text-white">
                    Start Practicing
                  </p>
                </div>
              </a>
              <a
                href="/study-plan"
                className="flex items-center justify-center rounded-lg border-2 border-gray-300 p-6 transition hover:border-emerald-600 hover:bg-emerald-50 dark:border-gray-600 dark:hover:bg-emerald-900/10"
              >
                <div className="text-center">
                  <div className="mb-2 text-2xl" aria-hidden="true">◷</div>
                  <p className="font-semibold text-gray-900 dark:text-white">Today&apos;s Study Plan</p>
                </div>
              </a>
              <a
                href="/tutor"
                className="flex items-center justify-center rounded-lg border-2 border-gray-300 dark:border-gray-600 p-6 hover:border-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/10 transition"
              >
                <div className="text-center">
                  <div className="text-2xl mb-2">◌</div>
                  <p className="font-semibold text-gray-900 dark:text-white">
                    AI Tutor
                  </p>
                </div>
              </a>
              <a
                href="/profile"
                className="flex items-center justify-center rounded-lg border-2 border-gray-300 dark:border-gray-600 p-6 hover:border-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/10 transition"
              >
                <div className="text-center">
                  <div className="text-2xl mb-2">⚙</div>
                  <p className="font-semibold text-gray-900 dark:text-white">
                    Settings
                  </p>
                </div>
              </a>
            </div>
          </div>
        </div>

        <section className="motion-enter mt-8 rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800" aria-label="Study progress">
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Study progress</h2>
              <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">
                {totalQuestions ? `${totalCorrect} correct answers across ${totalQuestions} attempts` : 'Complete a practice set to start tracking progress.'}
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-3"><button type="button" onClick={exportProgress} disabled={studySessions.length === 0} className="rounded-full border border-slate-200 px-3 py-2 text-xs font-bold text-slate-600 transition hover:border-emerald-600 hover:text-emerald-800 disabled:cursor-not-allowed disabled:opacity-50">Export CSV</button>{activitySummary && <span className="rounded-full bg-amber-50 px-3 py-2 text-xs font-bold text-amber-900 dark:bg-amber-900/30 dark:text-amber-200">Level {activitySummary?.level ?? 1} · {activitySummary?.total_points ?? 0} pts</span>}<p className="text-2xl font-bold text-emerald-700 dark:text-emerald-300" aria-label={`Overall accuracy ${overallAccuracy} percent`}>
              {overallAccuracy}% <span className="text-sm font-medium">accuracy</span>
            </p></div>
          </div>
          {progress.length > 0 && (
            <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {progress.map((item) => (
                <div key={`${item.exam_id}-${item.section}`} className="rounded-md bg-slate-50 p-3 dark:bg-slate-700/60">
                  <p className="font-semibold capitalize text-gray-900 dark:text-white">{item.section}</p>
                  <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">
                    {item.correct_answers}/{item.total_questions} correct
                  </p>
                </div>
              ))}
            </div>
          )}
          <div className="mt-6 rounded-xl bg-slate-50 p-4 dark:bg-slate-700/40"><div className="flex flex-wrap items-baseline justify-between gap-2"><h3 className="text-sm font-semibold text-slate-800 dark:text-slate-100">Accuracy trend · last 7 days</h3><p className="text-xs text-slate-500 dark:text-slate-400">Based on completed practice sessions</p></div><div className="mt-4 grid grid-cols-7 items-end gap-2" role="img" aria-label={`Seven day accuracy chart. ${recentDays.filter((day) => day.accuracy !== null).length} days include completed sessions.`}>{recentDays.map((day, index) => <div key={`${day.label}-${index}`} className="flex h-28 flex-col items-center justify-end gap-2"><div className="flex h-20 w-full items-end justify-center rounded-t-lg bg-slate-200/70 dark:bg-slate-600/50" title={day.accuracy === null ? 'No practice session' : `${day.accuracy}% accuracy, ${day.count} sessions`}><div className={`w-full rounded-t-lg transition-all ${day.accuracy === null ? 'bg-transparent' : 'bg-emerald-600'}`} style={{ height: `${day.accuracy ?? 0}%` }} /></div><span className="text-[10px] font-medium text-slate-500 dark:text-slate-400">{day.label}</span></div>)}</div><div className="mt-2 flex justify-between text-[10px] text-slate-400"><span>0%</span><span>100%</span></div></div>
        </section>

        <div className="mt-8 grid gap-8 lg:grid-cols-2">
          <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800" aria-label="Study recommendations">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Next for you</h2>
            <div className="mt-4 space-y-3">
              {recommendations.map((recommendation) => (
                <Link key={`${recommendation.section}-${recommendation.href}`} href={recommendation.href} className="block rounded-md border border-slate-200 p-4 transition hover:border-emerald-600 dark:border-slate-700">
                  <p className="font-semibold text-gray-900 dark:text-white">{recommendation.title}</p>
                  <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">{recommendation.reason}</p>
                </Link>
              ))}
            </div>
          </section>

          <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800" aria-label="Achievements">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Milestones</h2>
            <div className="mt-4 space-y-3">
              {achievements.map((achievement) => (
                <div key={achievement.id} className={`rounded-md p-3 ${achievement.unlocked ? 'bg-emerald-50 dark:bg-emerald-900/30' : 'bg-slate-50 dark:bg-slate-700/60'}`}>
                  <div className="flex justify-between gap-3">
                    <p className="font-semibold text-gray-900 dark:text-white">{achievement.title}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-300">{achievement.current}/{achievement.target}</p>
                  </div>
                  <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">{achievement.description}</p>
                </div>
              ))}
            </div>
          </section>
        </div>

        <section className="mt-8 rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800" aria-label="Recent study sessions">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Recent sessions</h2>
            <span className="text-xs text-gray-500">Latest {studySessions.length}</span>
          </div>
          {studySessions.length === 0 ? (
            <p className="mt-3 text-sm text-gray-600 dark:text-gray-300">Your completed practice sets will appear here.</p>
          ) : (
            <div className="mt-4 divide-y divide-slate-200 dark:divide-slate-700">
              {studySessions.map((session) => (
                <div key={session.id} className="flex flex-wrap items-center justify-between gap-2 py-3 first:pt-0">
                  <div>
                    <p className="font-semibold capitalize text-gray-900 dark:text-white">{session.section} practice</p>
                    <p className="text-xs text-gray-500">{new Date(session.session_date).toLocaleString()} Â· {Math.round(session.duration / 60)} min</p>
                  </div>
                  <p className="text-sm text-gray-700 dark:text-gray-200">
                    {session.questions_correct}/{session.questions_attempted} correct
                  </p>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Getting Started */}
        <div className="mt-8 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 p-6">
          <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-2">
            Welcome to Intelligent Test Prep Platform
          </h3>
          <p className="text-blue-800 dark:text-blue-200 mb-4">
            Start by selecting the exams you want to prepare for, then begin your personalized learning journey.
          </p>
          <a
            href="/exams"
            className="inline-block rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            Get Started
          </a>
        </div>
      </main>
    </div>
  );
}

