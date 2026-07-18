export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm">
        <div className="mb-12 flex justify-center">
          <div className="relative flex place-items-center">
            <h1 className="text-4xl font-bold">Intelligent Test Prep Platform</h1>
          </div>
        </div>

        <div className="relative flex place-items-center gap-4">
          <div className="bg-gradient-to-r from-blue-600 to-blue-800 px-8 py-4 rounded-lg text-white font-semibold text-lg">
            <a href="/login">Login</a>
          </div>
          <div className="bg-gray-200 dark:bg-gray-800 px-8 py-4 rounded-lg font-semibold text-lg">
            <a href="/register">Register</a>
          </div>
        </div>

        <div className="mt-24 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="p-6 border border-gray-200 dark:border-gray-800 rounded-lg">
            <h2 className="text-xl font-bold mb-2">🎯 Adaptive Learning</h2>
            <p className="text-gray-600 dark:text-gray-400">
              Personalized study paths that adapt to your performance in real-time.
            </p>
          </div>

          <div className="p-6 border border-gray-200 dark:border-gray-800 rounded-lg">
            <h2 className="text-xl font-bold mb-2">🤖 AI Tutor</h2>
            <p className="text-gray-600 dark:text-gray-400">
              24/7 intelligent tutoring powered by advanced language models and RAG.
            </p>
          </div>

          <div className="p-6 border border-gray-200 dark:border-gray-800 rounded-lg">
            <h2 className="text-xl font-bold mb-2">📊 Analytics</h2>
            <p className="text-gray-600 dark:text-gray-400">
              Detailed progress tracking and score prediction for your exams.
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
