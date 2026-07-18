'use client';

import { useState } from 'react';

import { useQuery, useMutation } from '@tanstack/react-query';
import { getCookie } from 'cookies-next';
import apiClient from '@/lib/api-client';

interface Passage {
  id: string;
  title: string;
  content: string;
  word_count: number;
  exam_type: string;
  difficulty: string;
  time_limit: number;
}

interface Question {
  id: string;
  text: string;
  question_type: string;
  answers: Array<{ id: string; text: string }>;
}

export default function ReadingPracticePage() {
  const [selectedPassage, setSelectedPassage] = useState<Passage | null>(null);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, string>>({});
  const [startTime, setStartTime] = useState<number | null>(null);

  // Fetch passages
  const { data: passages = [], isLoading: passagesLoading } = useQuery({
    queryKey: ['passages'],
    queryFn: async () => {
      const response = await apiClient.get<Passage[]>('/passages?limit=20');
      return response.data;
    },
  });

  // Fetch questions for selected passage
  const { data: passageDetail, isLoading: questionsLoading } = useQuery({
    queryKey: ['passage', selectedPassage?.id],
    queryFn: async () => {
      if (!selectedPassage) return null;
      const response = await apiClient.get<{ questions: Question[] }>(
        `/passages/${selectedPassage.id}`
      );
      return response.data;
    },
    enabled: !!selectedPassage,
  });

  // Submit answers mutation
  useMutation({

    mutationFn: async (questionId: string) => {
      const answerId = selectedAnswers[questionId];
      if (!answerId) {
        alert('Please select an answer');
        return;
      }
      const token = getCookie('access_token');
      if (!token) {
        alert('Please login to submit answers');
        return;
      }
      const response = await apiClient.post(
        `/questions/answer?token=${encodeURIComponent(token as string)}`,
        {
          question_id: questionId,
          answer_id: answerId,
          time_taken: startTime ? Date.now() - startTime : undefined,
        }
      );
      return response.data;
    },
  });

  const handleSelectPassage = (passage: Passage) => {
    setSelectedPassage(passage);
    setStartTime(Date.now());
    setSelectedAnswers({});
  };

  const handleAnswerSelect = (questionId: string, answerId: string) => {
    setSelectedAnswers((prev) => ({
      ...prev,
      [questionId]: answerId,
    }));
  };

  if (passagesLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-gray-600 dark:text-gray-400">Loading passages...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Reading Practice
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            {selectedPassage ? 'Answer the questions below' : 'Select a passage to begin'}
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-8">
        {!selectedPassage ? (
          // Passage List
          <div className="grid gap-6 md:grid-cols-2">
            {passages.map((passage) => (
              <div
                key={passage.id}
                className="bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-lg transition cursor-pointer p-6"
                onClick={() => handleSelectPassage(passage)}
              >
                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">
                  {passage.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-3">
                  {passage.content}
                </p>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-blue-600 dark:text-blue-400 font-semibold">
                    {passage.exam_type}
                  </span>
                  <span className="text-gray-500 dark:text-gray-400">
                    {passage.word_count} words
                  </span>
                </div>
                <div className="mt-4">
                  <span className={`inline-block px-3 py-1 rounded text-xs font-semibold ${
                    passage.difficulty === 'easy'
                      ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                      : passage.difficulty === 'medium'
                      ? 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200'
                      : 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
                  }`}>
                    {passage.difficulty}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : questionsLoading ? (
          <div className="text-center text-gray-600 dark:text-gray-400">
            Loading questions...
          </div>
        ) : (
          // Reading and Questions
          <div className="grid grid-cols-3 gap-8">
            {/* Passage */}
            <div className="col-span-1 bg-white dark:bg-gray-800 rounded-lg shadow p-6 h-fit sticky top-4">
              <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
                {selectedPassage.title}
              </h2>
              <p className="text-gray-700 dark:text-gray-300 leading-relaxed text-sm whitespace-pre-wrap">
                {selectedPassage.content}
              </p>
              <div className="mt-6">
                <button
                  onClick={() => setSelectedPassage(null)}
                  className="w-full px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white rounded hover:bg-gray-300 dark:hover:bg-gray-600 font-semibold transition"
                >
                  Back to Passages
                </button>
              </div>
            </div>

            {/* Questions */}
            <div className="col-span-2 space-y-6">
              {passageDetail?.questions?.map((question, index) => (
                <div
                  key={question.id}
                  className="bg-white dark:bg-gray-800 rounded-lg shadow p-6"
                >
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
                    Question {index + 1}
                  </h3>
                  <p className="text-gray-700 dark:text-gray-300 mb-6 font-semibold">
                    {question.text}
                  </p>
                  <div className="space-y-3">
                    {question.answers.map((answer) => (
                      <label
                        key={answer.id}
                        className="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition"
                      >
                        <input
                          type="radio"
                          name={`question-${question.id}`}
                          value={answer.id}
                          checked={selectedAnswers[question.id] === answer.id}
                          onChange={() => handleAnswerSelect(question.id, answer.id)}
                          className="w-4 h-4"
                        />
                        <span className="ml-4 text-gray-700 dark:text-gray-300">
                          {answer.text}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>
              ))}

              {/* Submit Button */}
              {passageDetail?.questions && passageDetail.questions.length > 0 && (
                <button
                  onClick={() => {
                    const answeredAll = passageDetail.questions.every(
                      (q) => selectedAnswers[q.id]
                    );
                    if (!answeredAll) {
                      alert('Please answer all questions before submitting');
                      return;
                    }
                    alert('Reading practice session submitted!');
                    setSelectedPassage(null);
                  }}
                  className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold transition"
                >
                  Submit Answers
                </button>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
