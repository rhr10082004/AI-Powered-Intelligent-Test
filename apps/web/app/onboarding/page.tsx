'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import apiClient from '@/lib/api-client';

const examOptions = ['IELTS', 'GRE', 'TOEFL'];
const levelOptions = ['Beginner', 'Intermediate', 'Advanced'];

export default function OnboardingPage() {
  const router = useRouter();
  const [selectedExam, setSelectedExam] = useState('IELTS');
  const [selectedLevel, setSelectedLevel] = useState('Intermediate');
  const [goal, setGoal] = useState('Improve my score and build consistent study habits.');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setError('');
    try {
      await apiClient.post('/exams/enroll', {
        exam_type: selectedExam.toLowerCase(),
        skill_level: selectedLevel.toLowerCase(),
      });
      window.localStorage.setItem('study_exam', selectedExam);
      window.localStorage.setItem('study_goal', goal.trim());
      router.push('/dashboard');
    } catch (requestError) {
      const detail = (requestError as { response?: { data?: { detail?: string } } }).response?.data?.detail;
      if (typeof detail === 'string' && detail.includes('already enrolled')) {
        window.localStorage.setItem('study_exam', selectedExam);
        window.localStorage.setItem('study_goal', goal.trim());
        router.push('/dashboard');
        return;
      }
      setError(detail || 'Could not save your study plan. Please sign in and try again.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 px-4 py-12 dark:bg-slate-900">
      <div className="mx-auto max-w-2xl rounded-2xl bg-white p-8 shadow-lg dark:bg-slate-800">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-600">
          Welcome
        </p>
        <h1 className="mt-3 text-3xl font-bold text-slate-900 dark:text-white">
          Personalize your study plan
        </h1>
        <p className="mt-2 text-slate-600 dark:text-slate-300">
          Tell us a little about your goals so the platform can guide your preparation.
        </p>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && <p className="text-sm text-red-600" role="alert">{error}</p>}
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700 dark:text-slate-200">
              Exam focus
            </label>
            <div className="grid gap-3 sm:grid-cols-3">
              {examOptions.map((exam) => (
                <button
                  key={exam}
                  type="button"
                  onClick={() => setSelectedExam(exam)}
                  className={`rounded-xl border px-4 py-3 text-sm font-semibold transition ${
                    selectedExam === exam
                      ? 'border-blue-600 bg-blue-600 text-white'
                      : 'border-slate-200 bg-slate-50 text-slate-700 hover:border-blue-300 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-100'
                  }`}
                >
                  {exam}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700 dark:text-slate-200">
              Current level
            </label>
            <div className="grid gap-3 sm:grid-cols-3">
              {levelOptions.map((level) => (
                <button
                  key={level}
                  type="button"
                  onClick={() => setSelectedLevel(level)}
                  className={`rounded-xl border px-4 py-3 text-sm font-semibold transition ${
                    selectedLevel === level
                      ? 'border-emerald-600 bg-emerald-600 text-white'
                      : 'border-slate-200 bg-slate-50 text-slate-700 hover:border-emerald-300 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-100'
                  }`}
                >
                  {level}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700 dark:text-slate-200">
              Study goal
            </label>
            <textarea
              value={goal}
              onChange={(event) => setGoal(event.target.value)}
              rows={4}
              className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-700 outline-none transition focus:border-blue-500 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-100"
            />
          </div>

          <button
            type="submit"
            disabled={saving}
            className="w-full rounded-xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? 'Saving plan...' : 'Save and continue'}
          </button>
        </form>
      </div>
    </div>
  );
}
