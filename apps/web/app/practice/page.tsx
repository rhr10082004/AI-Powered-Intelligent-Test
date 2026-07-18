'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function PracticePage() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Practice Modules
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Select a module to start practicing
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {/* Reading Module */}
          <Link href="/practice/reading" className="group">
            <div className="rounded-lg bg-white dark:bg-gray-800 shadow-lg hover:shadow-xl transition p-8 h-full">
              <div className="text-4xl mb-4">📖</div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                Reading Practice
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Practice reading comprehension with real exam passages
              </p>
              <div className="inline-block bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-3 py-1 rounded text-sm font-semibold">
                View Passages
              </div>
            </div>
          </Link>

          {/* Listening Module */}
          <Link href="/practice/listening" className="group">
            <div className="rounded-lg bg-white dark:bg-gray-800 shadow-lg hover:shadow-xl transition p-8 h-full">
              <div className="text-4xl mb-4">🎧</div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                Listening Practice
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Listen to audio clips and answer comprehension questions
              </p>
              <div className="inline-block bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 px-3 py-1 rounded text-sm font-semibold">
                Listen Now
              </div>
            </div>
          </Link>

          {/* Vocabulary Module */}
          <Link href="/practice/vocabulary" className="group">
            <div className="rounded-lg bg-white dark:bg-gray-800 shadow-lg hover:shadow-xl transition p-8 h-full">
              <div className="text-4xl mb-4">📚</div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                Vocabulary Builder
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Learn and review vocabulary with spaced repetition
              </p>
              <div className="inline-block bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 px-3 py-1 rounded text-sm font-semibold">
                Study Words
              </div>
            </div>
          </Link>

          {/* Grammar Module */}
          <Link href="/practice/grammar" className="group">
            <div className="rounded-lg bg-white dark:bg-gray-800 shadow-lg hover:shadow-xl transition p-8 h-full">
              <div className="text-4xl mb-4">✏️</div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                Grammar Exercises
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Master grammar rules with interactive exercises
              </p>
              <div className="inline-block bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 px-3 py-1 rounded text-sm font-semibold">
                Practice Grammar
              </div>
            </div>
          </Link>

          {/* Writing Module (Future) */}
          <div className="opacity-50">
            <div className="rounded-lg bg-gray-200 dark:bg-gray-700 shadow p-8 h-full">
              <div className="text-4xl mb-4 opacity-50">✍️</div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                Writing Practice
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Coming Soon
              </p>
              <div className="inline-block bg-gray-300 dark:bg-gray-600 text-gray-700 dark:text-gray-300 px-3 py-1 rounded text-sm font-semibold">
                Coming Soon
              </div>
            </div>
          </div>

          {/* Speaking Module (Future) */}
          <div className="opacity-50">
            <div className="rounded-lg bg-gray-200 dark:bg-gray-700 shadow p-8 h-full">
              <div className="text-4xl mb-4 opacity-50">🎤</div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                Speaking Practice
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Coming Soon
              </p>
              <div className="inline-block bg-gray-300 dark:bg-gray-600 text-gray-700 dark:text-gray-300 px-3 py-1 rounded text-sm font-semibold">
                Coming Soon
              </div>
            </div>
          </div>
        </div>

        {/* Info Section */}
        <div className="mt-12 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 p-6">
          <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-2">
            How to Use Practice Modules
          </h3>
          <ul className="text-blue-800 dark:text-blue-200 space-y-2">
            <li>
              ✓ <strong>Select a module</strong> to begin practicing
            </li>
            <li>
              ✓ <strong>Complete questions</strong> and get immediate feedback
            </li>
            <li>
              ✓ <strong>View explanations</strong> for all answers
            </li>
            <li>
              ✓ <strong>Track progress</strong> on your dashboard
            </li>
          </ul>
        </div>
      </main>
    </div>
  );
}
