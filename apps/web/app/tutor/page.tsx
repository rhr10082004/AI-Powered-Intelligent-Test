'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import apiClient from '@/lib/api-client';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ConversationSummary {
  id: string;
  title: string;
  exam_type: string | null;
  updated_at: string;
}

interface ConversationDetail extends ConversationSummary {
  messages: Array<Message & { id: string; created_at: string }>;
}

const starterMessages: Message[] = [
  { role: 'assistant', content: 'Hi! I can help you with test strategies, explanations, and practice planning.' },
];

const tutorTopics = [
  'finding a passage main idea', 'eliminating reading distractors', 'recognizing inference questions', 'tracking details while listening',
  'taking concise listening notes', 'building an academic vocabulary routine', 'using new words in context', 'subject and verb agreement',
  'using articles correctly', 'writing a clear thesis statement', 'organizing body paragraphs', 'supporting an argument with evidence',
  'writing a useful conclusion', 'planning a 30-minute study session', 'reviewing mistakes without losing motivation',
  'preparing for a timed exam', 'improving sentence variety', 'paraphrasing source ideas fairly', 'managing test-day nerves',
  'choosing which skill to practice next',
];
const tutorFrames = [
  (topic: string) => `Explain ${topic} in simple steps and give me one example.`,
  (topic: string) => `Quiz me with a short practice question about ${topic}, then explain the answer.`,
  (topic: string) => `Show me a strategy for improving ${topic} in a 20-minute session.`,
  (topic: string) => `What common mistake should I watch for when working on ${topic}?`,
  (topic: string) => `Help me make a small study plan focused on ${topic}.`,
];
const starterQuestions = tutorTopics.flatMap((topic) => tutorFrames.map((frame) => frame(topic)));

export default function TutorPage() {
  const [messages, setMessages] = useState<Message[]>(starterMessages);
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [draft, setDraft] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    const loadHistory = async () => {
      try {
        const response = await apiClient.get<ConversationSummary[]>('/tutor/conversations');
        if (!active) return;
        setConversations(response.data);
        const latest = response.data[0];
        if (!latest) return;
        const detail = await apiClient.get<ConversationDetail>(`/tutor/conversations/${latest.id}`);
        if (active) {
          setConversationId(latest.id);
          setMessages(detail.data.messages.length ? detail.data.messages : starterMessages);
        }
      } catch {
        if (active) setError('Sign in to save and revisit your tutor conversations.');
      } finally {
        if (active) setIsLoadingHistory(false);
      }
    };
    void loadHistory();
    return () => { active = false; };
  }, []);

  const openConversation = async (id: string) => {
    if (isSending || id === conversationId) return;
    setError('');
    try {
      const response = await apiClient.get<ConversationDetail>(`/tutor/conversations/${id}`);
      setConversationId(id);
      setMessages(response.data.messages.length ? response.data.messages : starterMessages);
    } catch {
      setError('That conversation could not be loaded. Please try again.');
    }
  };

  const startNewConversation = () => {
    if (isSending) return;
    setConversationId(null);
    setMessages(starterMessages);
    setError('');
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    const content = draft.trim();
    if (!content || isSending) return;

    const nextMessages = [...messages, { role: 'user' as const, content }];
    setMessages(nextMessages);
    setDraft('');
    setError('');
    setIsSending(true);

    try {
      const response = await apiClient.post<{ response: string; conversation_id: string }>('/tutor/chat', {
        exam_type: window.localStorage.getItem('study_exam') || undefined,
        conversation_id: conversationId || undefined,
        messages: nextMessages.slice(-30),
      });
      setConversationId(response.data.conversation_id);
      setMessages((current) => [...current, { role: 'assistant', content: response.data.response }]);
      const history = await apiClient.get<ConversationSummary[]>('/tutor/conversations');
      setConversations(history.data);
    } catch {
      setError('Could not reach the tutor. Your question is still here; check your connection and try again.');
    } finally {
      setIsSending(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#f7f8f4] px-4 py-8 text-[#17251f] sm:px-6 sm:py-12">
      <div className="motion-enter mx-auto grid max-w-6xl gap-5 md:grid-cols-[250px_minmax(0,1fr)]">
        <aside className="rounded-3xl border border-[#e5ebe4] bg-white p-4 shadow-sm">
          <div className="flex items-center justify-between gap-3">
            <div><p className="text-xs font-bold uppercase tracking-[.14em] text-[#679074]">Studywell</p><h1 className="mt-1 text-lg font-bold">Your tutor</h1></div>
            <button type="button" onClick={startNewConversation} disabled={isSending} className="rounded-full bg-[#173f32] px-3 py-2 text-xs font-bold text-white transition hover:bg-[#245744] disabled:opacity-50">+ New</button>
          </div>
          <p className="mt-4 text-xs leading-5 text-[#718078]">Ask a question, or pick up a saved conversation.</p>
          <div className="mt-5 space-y-2" aria-label="Saved conversations">
            {isLoadingHistory && <p className="px-3 py-2 text-xs text-[#87938c]" role="status">Loading your history…</p>}
            {!isLoadingHistory && conversations.length === 0 && <p className="rounded-2xl bg-[#f4f7f2] px-3 py-3 text-xs leading-5 text-[#87938c]">Your tutor chats will appear here.</p>}
            {conversations.map((conversation) => <button key={conversation.id} type="button" onClick={() => void openConversation(conversation.id)} className={`block w-full rounded-2xl px-3 py-3 text-left text-sm transition ${conversationId === conversation.id ? 'bg-[#eaf3e9] text-[#173f32]' : 'text-[#53655a] hover:bg-[#f4f7f2]'}`}><span className="block truncate font-semibold">{conversation.title}</span><span className="mt-1 block text-[11px] text-[#87938c]">{conversation.exam_type || 'Study session'}</span></button>)}
          </div>
          <Link href="/dashboard" className="mt-6 inline-block text-xs font-bold text-[#35694e] underline decoration-[#b7d0bc] underline-offset-4">Back to dashboard</Link>
        </aside>

        <section className="flex min-h-[75vh] min-w-0 flex-col overflow-hidden rounded-3xl border border-[#e5ebe4] bg-white shadow-sm">
          <header className="border-b border-[#edf0eb] px-5 py-5 sm:px-7">
            <p className="text-xs font-bold uppercase tracking-[.14em] text-[#679074]">Personal study support</p>
            <h2 className="mt-1 text-xl font-bold">Ask, learn, keep going.</h2>
            <p className="mt-1 text-sm text-[#718078]">Your conversations are saved privately to your account.</p>
          </header>
          <div className="flex-1 space-y-4 overflow-y-auto px-4 py-5 sm:px-7" aria-live="polite">
            {messages.map((message, index) => <div key={`${message.role}-${index}`} className={`max-w-2xl whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm leading-6 ${message.role === 'user' ? 'ml-auto bg-[#173f32] text-white' : 'bg-[#f2f6f0] text-[#344b3e]'}`}>{message.content}</div>)}
            {isSending && <p className="text-sm text-[#718078]" role="status">Tutor is thinking…</p>}
          </div>
          <form onSubmit={handleSubmit} className="border-t border-[#edf0eb] px-4 py-4 sm:px-7 sm:py-5">
            {error && <p className="mb-3 text-sm text-red-700" role="alert">{error} <Link href="/auth/login" className="font-semibold underline">Sign in</Link></p>}
            {messages.length === 1 && <div className="mb-3"><p className="mb-2 text-[11px] font-bold uppercase tracking-wide text-[#87938c]">Try asking</p><div className="flex flex-wrap gap-2">{starterQuestions.slice(0, 4).map((question) => <button key={question} type="button" disabled={isSending} onClick={() => setDraft(question)} className="rounded-full border border-[#e5ebe4] bg-[#fafbf9] px-3 py-2 text-left text-xs text-[#53655a] transition hover:border-[#b7d0bc] hover:bg-[#f2f6f0] disabled:opacity-50">{question}</button>)}</div><details className="mt-3"><summary className="w-fit cursor-pointer text-xs font-bold text-[#35694e] underline decoration-[#b7d0bc] underline-offset-4">Browse 100 tutor prompt examples</summary><label className="mt-3 block text-xs font-semibold text-[#718078]">Choose an example prompt<select defaultValue="" onChange={(event) => { if (event.target.value) setDraft(event.target.value); }} className="mt-2 block w-full rounded-xl border border-[#dce4dc] bg-white px-3 py-2.5 text-sm text-[#344b3e] outline-none focus:border-[#5f9c75]"><option value="">Select a prompt</option>{starterQuestions.map((question, index) => <option key={index} value={question}>{String(index + 1).padStart(3, '0')} · {question}</option>)}</select></label></details></div>}
            <div className="flex gap-2 sm:gap-3">
              <input value={draft} required maxLength={12000} onChange={(event) => setDraft(event.target.value)} placeholder="Ask the tutor a question…" aria-label="Your message" className="min-w-0 flex-1 rounded-2xl border border-[#dce4dc] bg-[#fafbf9] px-4 py-3 text-sm text-[#20372a] outline-none focus:border-[#5f9c75] focus:ring-4 focus:ring-[#5f9c75]/10" />
              <button type="submit" disabled={isSending || !draft.trim()} className="rounded-2xl bg-[#173f32] px-4 py-3 text-sm font-bold text-white transition hover:bg-[#245744] disabled:cursor-not-allowed disabled:opacity-50 sm:px-6">{isSending ? 'Sending…' : 'Send'}</button>
            </div>
          </form>
        </section>
      </div>
    </main>
  );
}



