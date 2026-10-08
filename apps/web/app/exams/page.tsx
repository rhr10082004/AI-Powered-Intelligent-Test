'use client';

import Link from 'next/link';
import { useState } from 'react';
import apiClient from '@/lib/api-client';

const exams = [
  {
    name: 'IELTS',
    level: 'Academic & General',
    description: 'Boost reading, writing, listening, and speaking performance across all modules.',
    accent: 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-200',
  },
  {
    name: 'GRE',
    level: 'Quant + Verbal',
    description: 'Prepare for analytical writing, verbal reasoning, and quantitative problem solving.',
    accent: 'bg-violet-100 text-violet-700 dark:bg-violet-900 dark:text-violet-200',
  },
  {
    name: 'TOEFL',
    level: 'Integrated Skills',
    description: 'Improve academic listening, reading, speaking, and writing with AI feedback.',
    accent: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-200',
  },
];

export default function ExamsPage() {
  const [enrolledExam, setEnrolledExam] = useState('');
  const [message, setMessage] = useState('');
  const [savingExam, setSavingExam] = useState('');

  const enroll = async (examName: string) => {
    setSavingExam(examName);
    setMessage('');
    try {
      await apiClient.post('/exams/enroll', {
        exam_type: examName.toLowerCase(),
        skill_level: 'intermediate',
      });
      window.localStorage.setItem('study_exam', examName);
      setEnrolledExam(examName);
      setMessage(`${examName} added to your study plan.`);
    } catch (error) {
      const detail = (error as { response?: { data?: { detail?: string } } }).response?.data?.detail;
      if (typeof detail === 'string' && detail.includes('already enrolled')) {
        setEnrolledExam(examName);
        setMessage(`${examName} is already in your study plan.`);
      } else {
        setMessage(detail || 'Sign in before adding an exam to your study plan.');
      }
    } finally {
      setSavingExam('');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 px-4 py-12 dark:bg-slate-900">
      <div className="mx-auto max-w-6xl">
        <div className="mb-8">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-600">
            Test prep
          </p>
          <h1 className="mt-3 text-3xl font-bold text-slate-900 dark:text-white">
            Choose your exam track
          </h1>
        </div>

        <div className="motion-stagger grid gap-6 md:grid-cols-3">
          {exams.map((exam) => (
            <div key={exam.name} className="rounded-2xl bg-white p-6 shadow-lg dark:bg-slate-800">
              <div className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${exam.accent}`}>
                {exam.name}
              </div>
              <h2 className="mt-4 text-xl font-bold text-slate-900 dark:text-white">{exam.level}</h2>
              <p className="mt-3 text-slate-600 dark:text-slate-300">{exam.description}</p>

              {enrolledExam === exam.name ? (
                <Link href="/practice" className="mt-6 inline-flex rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">Start practicing</Link>
              ) : (
                <button type="button" onClick={() => enroll(exam.name)} disabled={!!savingExam} className="mt-6 rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50">
                  {savingExam === exam.name ? 'Adding...' : 'Add study plan'}
                </button>
              )}
            </div>
          ))}
        </div>
        {message && <p className="mt-6 text-sm text-slate-700 dark:text-slate-200" role="status">{message}</p>}
      </div>
    </div>
  );
}
