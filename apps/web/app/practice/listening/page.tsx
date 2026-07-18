'use client';

import { useState, useRef } from 'react';

import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api-client';
import { getCookie } from 'cookies-next';

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

export default function ListeningPracticePage() {
  const [selectedTrack, setSelectedTrack] = useState<ListeningTrack | null>(null);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, string>>({});
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [showTranscript, setShowTranscript] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);

  // Fetch tracks
  const { data: tracks = [], isLoading: tracksLoading } = useQuery({
    queryKey: ['listening-tracks'],
    queryFn: async () => {
      const response = await apiClient.get<ListeningTrack[]>('/listening-tracks?limit=20');
      return response.data;
    },
  });

  // Fetch questions for selected track
  const { data: trackDetail, isLoading: questionsLoading } = useQuery({
    queryKey: ['listening-track', selectedTrack?.id],
    queryFn: async () => {
      if (!selectedTrack) return null;
      const response = await apiClient.get<{ questions: Question[] }>(
        `/listening-tracks/${selectedTrack.id}`
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
  };

  const handleAnswerSelect = (questionId: string, answerId: string) => {
    setSelectedAnswers((prev) => ({
      ...prev,
      [questionId]: answerId,
    }));
  };

  const togglePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
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
          <div className="grid gap-6 md:grid-cols-2">
            {tracks.map((track) => (
              <div
                key={track.id}
                className="bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-lg transition cursor-pointer p-6"
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
              </div>
            ))}
          </div>
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
              <audio
                ref={audioRef}
                src={selectedTrack.audio_url}
                onTimeUpdate={(e) => setCurrentTime(e.currentTarget.currentTime)}
                onEnded={() => setIsPlaying(false)}
              />

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
              {trackDetail?.questions?.map((question, index) => (
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
                  onClick={async () => {
                    const answeredAll = trackDetail?.questions?.every(
                      (q) => selectedAnswers[q.id]
                    );
                    if (!answeredAll) {
                      alert('Please answer all questions before submitting');
                      return;
                    }

                    const token = getCookie('access_token');
                    if (!token) {
                      alert('Please login to submit answers');
                      return;
                    }

                    // Submit each selected answer
                    for (const q of trackDetail?.questions ?? []) {
                      const answerId = selectedAnswers[q.id];
                      if (!answerId) continue;

                      await apiClient.post(
                        `/questions/answer?token=${encodeURIComponent(token as string)}`,
                        {
                          question_id: q.id,
                          answer_id: answerId,
                          time_taken: currentTime ? Math.floor(currentTime) : undefined,
                        }
                      );
                    }

                    alert('Listening practice session submitted!');
                    setSelectedTrack(null);
                  }}
                  className="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold transition"
                >
                  Submit Answers
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
