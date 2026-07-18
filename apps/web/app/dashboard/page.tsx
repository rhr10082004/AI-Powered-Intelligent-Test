'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Cookies from 'js-cookie';
import apiClient from '@/lib/api-client';

interface User {
  id: string;
  email: string;
  first_name: string | null;
  last_name: string | null;
  avatar_url: string | null;
  is_verified: boolean;
  created_at: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const token = Cookies.get('access_token');
        if (!token) {
          router.push('/login');
          return;
        }

        const response = await apiClient.get('/users/me', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        setUser(response.data);
      } catch (err: any) {
        setError('Failed to load user profile');
        Cookies.remove('access_token');
        Cookies.remove('refresh_token');
        router.push('/login');
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [router]);

  const handleLogout = () => {
    Cookies.remove('access_token');
    Cookies.remove('refresh_token');
    router.push('/login');
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

  if (error || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 dark:text-red-400">{error}</p>
        </div>
      </div>
    );
  }

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
                  <div className="text-2xl mb-2">📚</div>
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
                  <div className="text-2xl mb-2">✏️</div>
                  <p className="font-semibold text-gray-900 dark:text-white">
                    Start Practicing
                  </p>
                </div>
              </a>
              <a
                href="/tutor"
                className="flex items-center justify-center rounded-lg border-2 border-gray-300 dark:border-gray-600 p-6 hover:border-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/10 transition"
              >
                <div className="text-center">
                  <div className="text-2xl mb-2">🤖</div>
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
                  <div className="text-2xl mb-2">⚙️</div>
                  <p className="font-semibold text-gray-900 dark:text-white">
                    Settings
                  </p>
                </div>
              </a>
            </div>
          </div>
        </div>

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
