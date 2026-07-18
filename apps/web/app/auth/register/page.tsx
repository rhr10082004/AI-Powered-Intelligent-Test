'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Cookies from 'js-cookie';
import apiClient from '@/lib/api-client';

export default function RegisterPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters');
      setLoading(false);
      return;
    }

    try {
      const response = await apiClient.post('/auth/register', {
        email: formData.email,
        password: formData.password,
        first_name: formData.firstName,
        last_name: formData.lastName,
      });

      // Store tokens
      Cookies.set('access_token', response.data.access_token);
      if (response.data.refresh_token) {
        Cookies.set('refresh_token', response.data.refresh_token);
      }

      // Redirect to onboarding
      router.push('/onboarding');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-gray-900 px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
            Create your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
            Or{' '}
            <Link
              href="/login"
              className="font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400"
            >
              sign in to an existing account
            </Link>
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="rounded-md bg-red-50 dark:bg-red-900/20 p-4">
              <p className="text-sm font-medium text-red-800 dark:text-red-200">{error}</p>
            </div>
          )}

          <div className="space-y-4">
            <div className="flex gap-4">
              <div className="flex-1">
                <label htmlFor="firstName" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  First Name (optional)
                </label>
                <input
                  id="firstName"
                  name="firstName"
                  type="text"
                  className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 px-3 py-2 text-gray-900 dark:text-white dark:bg-gray-800 placeholder-gray-500 focus:border-blue-500 focus:outline-none focus:ring-blue-500"
                  placeholder="John"
                  value={formData.firstName}
                  onChange={handleChange}
                />
              </div>
              <div className="flex-1">
                <label htmlFor="lastName" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Last Name (optional)
                </label>
                <input
                  id="lastName"
                  name="lastName"
                  type="text"
                  className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 px-3 py-2 text-gray-900 dark:text-white dark:bg-gray-800 placeholder-gray-500 focus:border-blue-500 focus:outline-none focus:ring-blue-500"
                  placeholder="Doe"
                  value={formData.lastName}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 px-3 py-2 text-gray-900 dark:text-white dark:bg-gray-800 placeholder-gray-500 focus:border-blue-500 focus:outline-none focus:ring-blue-500"
                placeholder="you@example.com"
                value={formData.email}
                onChange={handleChange}
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 px-3 py-2 text-gray-900 dark:text-white dark:bg-gray-800 placeholder-gray-500 focus:border-blue-500 focus:outline-none focus:ring-blue-500"
                placeholder="At least 8 characters"
                value={formData.password}
                onChange={handleChange}
              />
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Must be at least 8 characters
              </p>
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                required
                className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 px-3 py-2 text-gray-900 dark:text-white dark:bg-gray-800 placeholder-gray-500 focus:border-blue-500 focus:outline-none focus:ring-blue-500"
                placeholder="Confirm your password"
                value={formData.confirmPassword}
                onChange={handleChange}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="group relative flex w-full justify-center rounded-md border border-transparent bg-blue-600 py-2 px-4 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
          >
            {loading ? 'Creating account...' : 'Create account'}
          </button>
        </form>
      </div>
    </div>
  );
}
