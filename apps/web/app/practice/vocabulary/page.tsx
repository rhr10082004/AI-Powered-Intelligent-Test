'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import Cookies from 'js-cookie';
import apiClient from '@/lib/api-client';

interface VocabularyWord {
  id: string;
  word: string;
  definition: string;
  part_of_speech: string;
  exam_type: string;
  difficulty: string;
  examples: string[] | null;
}

interface ReviewWord {
  word_id: string;
  proficiency_level: number;
  review_count: number;
  next_review: string | null;
  word: VocabularyWord;
}

export default function VocabularyPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [examFilter, setExamFilter] = useState('All exams');
  const [savedWords, setSavedWords] = useState<string[]>([]);
  const [message, setMessage] = useState('');
  const [savingWord, setSavingWord] = useState('');
  const [reviewingWord, setReviewingWord] = useState('');
  const { data: reviewWords = [], refetch: refreshReviewWords } = useQuery({
    queryKey: ['my-vocabulary'],
    queryFn: async () => (await apiClient.get<ReviewWord[]>('/vocabulary/my-words')).data,
    enabled: Boolean(Cookies.get('access_token')),
    retry: false,
  });
  const { data: words = [], isLoading, isError } = useQuery({
    queryKey: ['vocabulary-words'],
    queryFn: async () => (await apiClient.get<VocabularyWord[]>('/vocabulary/words?limit=150')).data,
  });
  const visibleWords = words.filter((word) =>
    (examFilter === 'All exams' || word.exam_type === examFilter) &&
    `${word.word} ${word.definition}`.toLowerCase().includes(searchTerm.trim().toLowerCase())
  );

  const saveWord = async (wordId: string) => {
    setSavingWord(wordId);
    setMessage('');
    try {
      await apiClient.post(`/vocabulary/add?word_id=${encodeURIComponent(wordId)}`);
      setSavedWords((current) => [...current, wordId]);
      await refreshReviewWords();
      setMessage('Word added to your review list.');
    } catch (error) {
      const detail = (error as { response?: { data?: { detail?: string } } }).response?.data?.detail;
      if (typeof detail === 'string' && detail.includes('already added')) {
        setSavedWords((current) => [...current, wordId]);
        setMessage('This word is already in your review list.');
      } else {
        setMessage(detail || 'Sign in to save words to your review list.');
      }
    } finally {
      setSavingWord('');
    }
  };

  const markReviewed = async (item: ReviewWord) => {
    setReviewingWord(item.word_id);
    setMessage('');
    try {
      await apiClient.put(`/vocabulary/${encodeURIComponent(item.word_id)}`, {
        proficiency_level: Math.min(5, item.proficiency_level + 1),
      });
      await refreshReviewWords();
      setMessage(`${item.word.word} reviewed. Its next review date has been scheduled.`);
    } catch {
      setMessage('Could not save this review. Please sign in and try again.');
    } finally {
      setReviewingWord('');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 px-4 py-12 dark:bg-slate-900">
      <div className="motion-enter mx-auto max-w-5xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Vocabulary Builder</h1>
          <p className="mt-2 text-slate-600 dark:text-slate-300">Strengthen your word knowledge with focused review and context practice.</p>
        </div>

        {Cookies.get('access_token') && (
          <section className="mb-8 border-b border-slate-200 pb-8 dark:border-slate-700" aria-label="Vocabulary review queue">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Review queue</h2>
            {reviewWords.length === 0 ? (
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">Add words below to build your review queue.</p>
            ) : (
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                {reviewWords.map((item) => (
                  <div key={item.word_id} className="flex items-center justify-between gap-3 rounded-lg bg-white p-4 shadow-sm dark:bg-slate-800">
                    <div>
                      <p className="font-semibold text-slate-900 dark:text-white">{item.word.word}</p>
                      <p className="text-xs text-slate-500">Level {item.proficiency_level}/5 · {item.review_count} reviews</p>
                      {item.next_review && <p className="mt-1 text-xs text-slate-500">Due {new Date(item.next_review).toLocaleDateString()}</p>}
                    </div>
                    <button type="button" disabled={reviewingWord === item.word_id} onClick={() => markReviewed(item)} className="rounded-md bg-emerald-700 px-3 py-2 text-sm font-semibold text-white hover:bg-emerald-800 disabled:opacity-50">
                      {reviewingWord === item.word_id ? 'Saving...' : 'Review'}
                    </button>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

        <section className="mb-6 grid gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:grid-cols-[minmax(0,1fr)_180px_auto] sm:items-end" aria-label="Filter vocabulary">
          <label className="text-xs font-semibold text-slate-600">Search words or meanings<input value={searchTerm} onChange={(event) => setSearchTerm(event.target.value)} placeholder="Try evidence, change, important…" className="mt-2 block w-full rounded-xl border border-slate-200 px-4 py-3 text-sm font-normal outline-none focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100" /></label>
          <label className="text-xs font-semibold text-slate-600">Exam<select value={examFilter} onChange={(event) => setExamFilter(event.target.value)} className="mt-2 block w-full rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm outline-none focus:border-emerald-600"><option>All exams</option><option>IELTS</option><option>TOEFL</option><option>GRE</option></select></label>
          <p className="pb-3 text-xs text-slate-500" role="status">{visibleWords.length} of {words.length} words</p>
        </section>

        {isLoading ? <p role="status">Loading words...</p> : isError ? <p role="alert">Vocabulary could not be loaded.</p> : words.length === 0 ? <p>No vocabulary words are available yet.</p> : null}
        {visibleWords.length === 0 && !isLoading && !isError ? <p className="rounded-2xl bg-white p-8 text-center text-sm text-slate-500">No words match those filters. Try another exam or search term.</p> : null}
        <div className="motion-stagger grid gap-5 md:grid-cols-2">
          {visibleWords.map((item) => (
            <div key={item.word} className="rounded-2xl bg-white p-6 shadow-lg dark:bg-slate-800">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-slate-900 dark:text-white">{item.word}</h2>
                <span className="rounded-full bg-emerald-100 px-2 py-1 text-xs font-semibold text-emerald-700 dark:bg-emerald-900 dark:text-emerald-200">
                  {item.difficulty}
                </span>
              </div>
              <p className="mt-2 text-xs uppercase text-slate-500">{item.part_of_speech}</p>
              <p className="mt-4 text-slate-600 dark:text-slate-300">{item.definition}</p>
              {item.examples?.[0] && <p className="mt-3 border-l-2 border-emerald-500 pl-3 text-sm italic text-slate-500">{item.examples[0]}</p>}
              <button type="button" disabled={savingWord === item.id || savedWords.includes(item.id)} onClick={() => saveWord(item.id)} className="mt-6 rounded-lg bg-emerald-700 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-800 disabled:opacity-50">
                {savedWords.includes(item.id) ? 'Added to review' : savingWord === item.id ? 'Saving...' : 'Add to review'}
              </button>
            </div>
          ))}
        </div>
        {message && <p className="mt-5 text-sm text-slate-700 dark:text-slate-200" role="status">{message}</p>}
      </div>
    </div>
  );
}
