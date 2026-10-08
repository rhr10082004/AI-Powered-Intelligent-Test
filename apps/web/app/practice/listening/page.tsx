'use client';

import { useState, useRef } from 'react';

import { useQuery } from '@tanstack/react-query';
import Cookies from 'js-cookie';
import apiClient from '@/lib/api-client';

interface ListeningTrack {
  id: string;
  title: string;
  audio_url: string;
  duration: number;
  transcript?: string;
  exam_type: string;
  difficulty: string;
  accent?: string;
}

interface Question {
  id: string;
  text: string;
  question_type: string;
  answers: Array<{ id: string; text: string }>;
}

interface AnswerResult {
  id: string;
  question_id: string;
  is_correct: boolean | null;
  correct_answer: string | null;
  explanation: string | null;
  attempts: number;
}

export default function ListeningPracticePage() {
  const [selectedTrack, setSelectedTrack] = useState<ListeningTrack | null>(null);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, string>>({});
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [showTranscript, setShowTranscript] = useState(false);
  const [submissionMessage, setSubmissionMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [answerResults, setAnswerResults] = useState<Record<string, AnswerResult>>({});
  const [sessionId, setSessionId] = useState('');
  const [sessionCompleted, setSessionCompleted] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [examFilter, setExamFilter] = useState('All exams');
  const audioRef = useRef<HTMLAudioElement>(null);

  // Fetch tracks
  const { data: tracks = [], isLoading: tracksLoading } = useQuery({
    queryKey: ['listening-tracks'],
    queryFn: async () => {
      const response = await apiClient.get<ListeningTrack[]>('/listening-tracks?limit=120');
      return response.data;
    },
  });
  const visibleTracks = tracks.filter((track) =>
    (examFilter === 'All exams' || track.exam_type === examFilter) &&
    `${track.title} ${track.transcript ?? ''}`.toLowerCase().includes(searchTerm.trim().toLowerCase())
  );

  // Fetch questions for selected track
  const { data: trackDetail, isLoading: questionsLoading } = useQuery({
    queryKey: ['listening-track', selectedTrack?.id],
    queryFn: async () => {
      if (!selectedTrack) return null;
      const response = await apiClient.get<Question[]>(
        `/listening-tracks/${selectedTrack.id}/questions`
      );
      return response.data;
    },
    enabled: !!selectedTrack,
  });

  const handleSelectTrack = (track: ListeningTrack) => {
    setSelectedTrack(track);
    setSelectedAnswers({});
    setCurrentTime(0);
    setIsPlaying(false);
    setAnswerResults({});
    setSubmissionMessage('');
    setSessionId(crypto.randomUUID());
    setSessionCompleted(false);
  };

  const handleAnswerSelect = (questionId: string, answerId: string) => {
    setSelectedAnswers((prev) => ({
      ...prev,
      [questionId]: answerId,
    }));
  };

  const togglePlayPause = () => {
    if (selectedTrack?.audio_url && audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        void audioRef.current.play().catch(() => setSubmissionMessage('This audio track could not be played.'));
      }
      return;
    }

    if (!selectedTrack?.transcript || !('speechSynthesis' in window)) {
      setSubmissionMessage('Audio playback is not available for this track.');
      return;
    }

    if (isPlaying) {
      window.speechSynthesis.cancel();
      setIsPlaying(false);
    } else {
      const utterance = new SpeechSynthesisUtterance(selectedTrack.transcript);
      utterance.onstart = () => setIsPlaying(true);
      utterance.onend = () => {
        setIsPlaying(false);
        setCurrentTime(selectedTrack.duration);
      };
      utterance.onerror = () => setIsPlaying(false);
      utterance.onboundary = (event) => {
        setCurrentTime(Math.floor((event.charIndex / selectedTrack.transcript!.length) * selectedTrack.duration));
      };
      window.speechSynthesis.speak(utterance);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

  if (tracksLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-gray-600 dark:text-gray-400">Loading listening tracks...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Listening Practice
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            {selectedTrack ? 'Listen and answer the questions' : 'Select an audio track to begin'}
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-8">
        {!selectedTrack ? (
          // Track List
          <>
          <section className="mb-6 grid gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:grid-cols-[minmax(0,1fr)_180px_auto] sm:items-end" aria-label="Filter listening tracks">
            <label className="text-xs font-semibold text-slate-600">Find a track or topic<input value={searchTerm} onChange={(event) => setSearchTerm(event.target.value)} placeholder="Try campus, workshop, research…" className="mt-2 block w-full rounded-xl border border-slate-200 px-4 py-3 text-sm font-normal outline-none focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100" /></label>
            <label className="text-xs font-semibold text-slate-600">Exam<select value={examFilter} onChange={(event) => setExamFilter(event.target.value)} className="mt-2 block w-full rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm outline-none focus:border-emerald-600"><option>All exams</option><option>IELTS</option><option>TOEFL</option><option>GRE</option></select></label>
            <p className="pb-3 text-xs text-slate-500" role="status">{visibleTracks.length} of {tracks.length} tracks</p>
          </section>
          {visibleTracks.length === 0 ? <p className="rounded-2xl bg-white p-8 text-center text-sm text-slate-500">No tracks match those filters. Try another exam or search term.</p> : <div className="grid gap-6 md:grid-cols-2">
            {visibleTracks.map((track) => (
              <button
                type="button"
                key={track.id}
                className="block w-full rounded-lg bg-white p-6 text-left shadow transition hover:shadow-lg dark:bg-gray-800"
                onClick={() => handleSelectTrack(track)}
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                      {track.title}
                    </h3>
                    {track.accent && (
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        Accent: {track.accent}
                      </p>
                    )}
                  </div>
                  <div className="text-3xl">🎧</div>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-blue-600 dark:text-blue-400 font-semibold">
                    {track.exam_type}
                  </span>
                  <span className="text-gray-500 dark:text-gray-400">
                    {formatTime(track.duration)}
                  </span>
                </div>
                <div className="mt-4">
                  <span className={`inline-block px-3 py-1 rounded text-xs font-semibold ${
                    track.difficulty === 'easy'
                      ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                      : track.difficulty === 'medium'
                      ? 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200'
                      : 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
                  }`}>
                    {track.difficulty}
                  </span>
                </div>
              </button>
            ))}
          </div>}
          </>
        ) : questionsLoading ? (
          <div className="text-center text-gray-600 dark:text-gray-400">
            Loading questions...
          </div>
        ) : (
          // Audio Player and Questions
          <div className="space-y-8">
            {/* Audio Player */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                {selectedTrack.title}
              </h2>

              {/* Audio Element (hidden) */}
              {selectedTrack.audio_url && <audio
                ref={audioRef}
                src={selectedTrack.audio_url}
                onTimeUpdate={(e) => setCurrentTime(e.currentTarget.currentTime)}
                onPlay={() => setIsPlaying(true)}
                onPause={() => setIsPlaying(false)}
                onEnded={() => setIsPlaying(false)}
              />}

              {/* Player Controls */}
              <div className="space-y-4">
                <div className="flex items-center gap-4">
                  <button
                    onClick={togglePlayPause}
                    className="flex-shrink-0 w-12 h-12 rounded-full bg-blue-600 hover:bg-blue-700 text-white font-bold text-xl transition flex items-center justify-center"
                  >
                    {isPlaying ? '⏸' : '▶'}
                  </button>
                  <div className="flex-1">
                    <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-blue-600 transition-all"
                        style={{
                          width: `${(currentTime / selectedTrack.duration) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                  <span className="text-sm text-gray-600 dark:text-gray-400 font-mono">
                    {formatTime(currentTime)} / {formatTime(selectedTrack.duration)}
                  </span>
                </div>

                {/* Transcript Button */}
                {selectedTrack.transcript && (
                  <button
                    onClick={() => setShowTranscript(!showTranscript)}
                    className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white rounded hover:bg-gray-300 dark:hover:bg-gray-600 transition"
                  >
                    {showTranscript ? 'Hide Transcript' : 'Show Transcript'}
                  </button>
                )}
              </div>

              {/* Transcript */}
              {showTranscript && selectedTrack.transcript && (
                <div className="mt-6 p-4 bg-gray-100 dark:bg-gray-700 rounded text-gray-700 dark:text-gray-300 text-sm">
                  <p className="font-semibold mb-2">Transcript:</p>
                  <p className="whitespace-pre-wrap">{selectedTrack.transcript}</p>
                </div>
              )}
            </div>

            {/* Questions */}
            <div className="space-y-6">
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                Questions
              </h3>
              {(trackDetail ?? []).map((question, index) => (
                <div
                  key={question.id}
                  className="bg-white dark:bg-gray-800 rounded-lg shadow p-6"
                >
                  <h4 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
                    Question {index + 1}
                  </h4>
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
                  {answerResults[question.id] && (
                    <div className={`mt-4 rounded-md p-3 text-sm ${answerResults[question.id].is_correct ? 'bg-emerald-50 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-200' : 'bg-amber-50 text-amber-900 dark:bg-amber-900/30 dark:text-amber-100'}`} role="status">
                      <p className="font-semibold">{answerResults[question.id].is_correct ? 'Correct' : `Review: ${answerResults[question.id].correct_answer || 'Answer recorded'}`}</p>
                      {answerResults[question.id].explanation && <p className="mt-1">{answerResults[question.id].explanation}</p>}
                    </div>
                  )}
                </div>
              ))}

              {/* Action Buttons */}
              <div className="flex gap-4">
                <button
                  onClick={() => setSelectedTrack(null)}
                  className="flex-1 px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg font-bold hover:bg-gray-300 dark:hover:bg-gray-600 transition"
                >
                  Back to Tracks
                </button>
                <button
                  disabled={isSubmitting || sessionCompleted}
                  onClick={async () => {
                    const questions = trackDetail ?? [];
                    const answeredAll = questions.length > 0 && questions.every(
                      (q) => selectedAnswers[q.id]
                    );
                    if (!answeredAll) {
                      setSubmissionMessage('Please answer every question before submitting.');
                      return;
                    }

                    const token = Cookies.get('access_token');
                    if (!token) {
                      setSubmissionMessage('Sign in before submitting answers.');
                      return;
                    }

                    setIsSubmitting(true);
                    setSubmissionMessage('');
                    try {
                      const results: AnswerResult[] = [];
                      for (const question of questions) {
                        const response = await apiClient.post<AnswerResult>('/questions/answer', {
                          question_id: question.id,
                          answer_id: selectedAnswers[question.id],
                          time_taken: currentTime ? Math.floor(currentTime) : undefined,
                          session_id: sessionId,
                        });
                        results.push(response.data);
                      }
                      await apiClient.post('/study-sessions/complete', {
                        session_id: sessionId,
                        section: 'listening',
                        duration: Math.floor(currentTime),
                      });
                      setSessionCompleted(true);
                      setAnswerResults(Object.fromEntries(results.map((result) => [result.question_id, result])));
                      const correct = results.filter((result) => result.is_correct).length;
                      setSubmissionMessage(`Result: ${correct} of ${results.length} correct (${Math.round((correct / results.length) * 100)}%).`);
                    } catch {
                      setSubmissionMessage('Could not submit your answers. Please try again.');
                    } finally {
                      setIsSubmitting(false);
                    }
                  }}
                  className="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold transition"
                >
                  {isSubmitting ? 'Submitting...' : sessionCompleted ? 'Session complete' : 'Submit Answers'}
                </button>
              </div>
              {submissionMessage && <p className="text-sm text-gray-700 dark:text-gray-300" role="status">{submissionMessage}</p>}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
