'use client';

import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { Mic, MicOff, RotateCcw, Sparkles } from 'lucide-react';
import apiClient from '@/lib/api-client';

type SpeechResultLike = { isFinal: boolean; 0: { transcript: string } };
type SpeechEventLike = { resultIndex: number; results: ArrayLike<SpeechResultLike> };
type SpeechRecognitionLike = {
  lang: string;
  interimResults: boolean;
  continuous: boolean;
  onresult: ((event: SpeechEventLike) => void) | null;
  onerror: ((event: { error: string }) => void) | null;
  onend: (() => void) | null;
  start: () => void;
  stop: () => void;
};
type SpeechWindow = Window & {
  SpeechRecognition?: new () => SpeechRecognitionLike;
  webkitSpeechRecognition?: new () => SpeechRecognitionLike;
};
type Criterion = { name: string; score: number; feedback: string };
type Review = { id: string; exam_type: string; prompt: string; word_count: number; estimated_score: number; feedback: { summary: string; criteria: Criterion[]; strengths: string[]; next_steps: string[]; limitation: string }; created_at: string };
type HistoryItem = { id: string; exam_type: string; prompt: string; transcript_excerpt: string; word_count: number; estimated_score: number; summary: string; created_at: string };

const speakingTopics = [
  'a place where you enjoy spending time', 'an activity you learned recently', 'a person who influenced you', 'a book or film you remember',
  'a useful skill you would like to develop', 'a memorable journey', 'a time you solved a difficult problem', 'a tradition in your community',
  'a piece of technology you use often', 'a decision that changed your routine', 'a subject you enjoy learning about', 'a helpful conversation',
  'a goal you are working toward', 'an event you helped organize', 'a change you would make to your neighborhood', 'a meal shared with others',
  'an item that has personal meaning', 'a time you worked with a team', 'a new idea you recently encountered', 'a place you hope to visit',
];
const speakingPrompts = speakingTopics.flatMap((topic) => [
  `Describe ${topic}. Explain why it is important to you.`,
  `Talk about ${topic} and compare it with another experience.`,
  `Describe a challenge connected with ${topic}, and explain how you handled it.`,
  `How has ${topic} changed over time? Give specific details.`,
  `What advice would you give someone about ${topic}? Explain your reasons.`,
]);

export default function SpeakingPracticePage() {
  const [exam, setExam] = useState('IELTS');
  const [prompt, setPrompt] = useState(speakingPrompts[0]);
  const [transcript, setTranscript] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [review, setReview] = useState<Review | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);
  const wordCount = transcript.trim() ? transcript.trim().split(/\s+/).length : 0;

  useEffect(() => {
    let active = true;
    apiClient.get<HistoryItem[]>('/speaking/history').then((response) => { if (active) setHistory(response.data); }).catch(() => undefined);
    return () => { active = false; recognitionRef.current?.stop(); };
  }, []);

  const toggleRecording = () => {
    setError('');
    if (isRecording) { recognitionRef.current?.stop(); setIsRecording(false); return; }
    const speech = window as SpeechWindow;
    const Recognition = speech.SpeechRecognition || speech.webkitSpeechRecognition;
    if (!Recognition) { setError('Speech recognition is not available in this browser. You can type your response in the transcript box.'); return; }
    const recognition = new Recognition();
    recognition.lang = exam === 'IELTS' ? 'en-GB' : 'en-US';
    recognition.interimResults = false;
    recognition.continuous = true;
    recognition.onresult = (event) => {
      const phrases: string[] = [];
      for (let index = event.resultIndex; index < event.results.length; index += 1) {
        if (event.results[index]?.isFinal) phrases.push(event.results[index][0].transcript.trim());
      }
      if (phrases.length) setTranscript((current) => [current.trim(), phrases.join(' ')].filter(Boolean).join(' '));
    };
    recognition.onerror = (event) => { setError(`Microphone transcription stopped: ${event.error}. You can continue by typing.`); setIsRecording(false); };
    recognition.onend = () => setIsRecording(false);
    recognitionRef.current = recognition;
    try { recognition.start(); setIsRecording(true); } catch { setError('The microphone could not start. Check browser permissions or type your response.'); }
  };

  const submitResponse = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setError(''); setLoading(true); setReview(null);
    try {
      const response = await apiClient.post<Review>('/speaking/evaluate', { exam_type: exam, prompt, transcript });
      setReview(response.data);
      const historyResponse = await apiClient.get<HistoryItem[]>('/speaking/history');
      setHistory(historyResponse.data);
    } catch (cause: unknown) {
      const detail = (cause as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail || 'Could not save the speaking review. Sign in and try again.');
    } finally { setLoading(false); }
  };

  return (
    <main className="min-h-screen overflow-x-hidden bg-[#f7f8f4] px-4 py-8 text-[#1b3025] sm:px-7 sm:py-12">
      <div className="mx-auto max-w-6xl">
        <Link href="/practice" className="text-sm font-semibold text-[#718078] transition hover:text-[#173f32]">← All practice</Link>
        <header className="motion-enter mt-7"><p className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-[.18em] text-[#679074]"><Sparkles size={14}/> Speaking studio · 100 prompts</p><h1 className="mt-2 text-3xl font-semibold tracking-tight sm:text-4xl">Find your <span className="font-serif italic text-emerald-800">speaking rhythm.</span></h1><p className="mt-3 max-w-2xl text-sm leading-6 text-[#718078]">Practice a short response using speech recognition or type a transcript. Feedback helps you reflect on structure and development.</p></header>
        <div className="mt-8 grid items-start gap-6 lg:grid-cols-[minmax(0,1.35fr)_minmax(280px,.75fr)]">
          <form onSubmit={submitResponse} className="rounded-3xl border border-[#e1e8df] bg-white p-5 shadow-sm sm:p-7">
            <div className="grid gap-4 sm:grid-cols-[150px_1fr]"><label className="text-xs font-bold text-[#53665a]">Exam<select value={exam} onChange={(event) => setExam(event.target.value)} className="mt-2 block w-full rounded-xl border border-[#dce4dc] bg-white px-3 py-3 text-sm font-medium outline-none focus:border-emerald-600"><option>IELTS</option><option>TOEFL</option><option>GRE</option></select></label><label className="text-xs font-bold text-[#53665a]">Choose a speaking prompt<select value={prompt} onChange={(event) => setPrompt(event.target.value)} className="mt-2 block w-full rounded-xl border border-[#dce4dc] bg-white px-3 py-3 text-sm font-medium outline-none focus:border-emerald-600">{speakingPrompts.map((item,index)=><option key={index} value={item}>{String(index+1).padStart(3,'0')} · {item}</option>)}</select></label></div>
            <div className="mt-6 rounded-2xl bg-[#f0f5ed] p-4 sm:p-5"><p className="text-[10px] font-bold uppercase tracking-[.16em] text-[#718c75]">Your prompt</p><p className="mt-2 text-base font-semibold leading-7 text-[#304a38]">{prompt}</p></div>
            <div className="mt-5 flex flex-wrap items-center justify-between gap-3"><div><h2 className="text-sm font-bold text-[#344b3e]">Your response</h2><p className="mt-1 text-xs text-[#89958c]">Aim for 30–90 seconds, then review the transcript.</p></div><button type="button" onClick={toggleRecording} className={`inline-flex min-h-11 items-center gap-2 rounded-full px-4 py-2.5 text-xs font-bold transition ${isRecording?'bg-rose-600 text-white hover:bg-rose-700':'bg-[#1d4034] text-white hover:bg-[#2d5845]'}`}>{isRecording?<><MicOff size={16}/> Stop recording</>:<><Mic size={16}/> Start speaking</>}</button></div>
            <label className="sr-only" htmlFor="speaking-transcript">Transcript</label><textarea id="speaking-transcript" value={transcript} onChange={(event) => setTranscript(event.target.value)} maxLength={12000} rows={9} placeholder="Your speech transcript appears here. You can also type your response." className="mt-4 block w-full resize-y rounded-2xl border border-[#dce4dc] bg-[#fcfdfb] px-4 py-4 text-sm leading-7 outline-none placeholder:text-[#a0aaa2] focus:border-emerald-600 focus:ring-4 focus:ring-emerald-100" />
            <div className="mt-3 flex flex-wrap items-center justify-between gap-3"><span className={`text-xs ${wordCount>0&&wordCount<20?'font-semibold text-amber-700':'text-[#8b978d]'}`}>{wordCount} words · minimum 20</span><button type="button" onClick={() => { setTranscript(''); setReview(null); setError(''); }} className="inline-flex items-center gap-1 text-xs font-semibold text-[#718078] hover:text-[#173f32]"><RotateCcw size={13}/> Clear response</button></div>
            {error&&<p role="alert" className="mt-4 rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-800">{error}</p>}
            <button type="submit" disabled={loading||wordCount<20} className="mt-5 inline-flex min-h-12 w-full items-center justify-center gap-2 rounded-xl bg-[#24463b] px-5 py-3 text-sm font-bold text-white transition hover:bg-[#18372d] disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto">{loading?'Saving your review…':'Review my response'}</button>
            <p className="mt-4 text-xs leading-5 text-[#98a39a]">Transcript-based feedback is a study aid. It does not score pronunciation, pace, intonation or accent and is not an official exam score.</p>
          </form>

          <aside className="space-y-5"><section className="rounded-3xl border border-[#e1e8df] bg-white p-5 shadow-sm sm:p-6" aria-live="polite"><p className="text-[10px] font-bold uppercase tracking-[.16em] text-[#76917d]">Practice review</p>{review?<><div className="mt-3 flex items-end justify-between"><h2 className="text-lg font-bold">Your reflection</h2><span className="text-3xl font-extrabold text-[#35694e]">{review.estimated_score}<span className="text-xs font-semibold text-[#8b978d]"> / 5</span></span></div><p className="mt-2 text-xs leading-5 text-[#718078]">{review.feedback.summary}</p><div className="mt-4 space-y-3">{review.feedback.criteria.map((item)=><div key={item.name} className="rounded-2xl bg-[#f8f9f6] p-3"><div className="flex justify-between gap-3"><p className="text-xs font-bold text-[#40574a]">{item.name}</p><span className="text-xs font-extrabold text-[#4b7155]">{item.score}/5</span></div><p className="mt-1 text-[11px] leading-5 text-[#7b8980]">{item.feedback}</p></div>)}</div><h3 className="mt-4 text-xs font-bold text-[#40574a]">Try next</h3><ul className="mt-2 list-disc space-y-1 pl-4 text-xs leading-5 text-[#718078]">{review.feedback.next_steps.map((item)=><li key={item}>{item}</li>)}</ul><p className="mt-4 rounded-xl bg-amber-50 p-3 text-[11px] leading-5 text-amber-900">{review.feedback.limitation}</p></>:<div className="mt-4 rounded-2xl bg-[#f8f9f6] p-4"><h2 className="text-sm font-bold text-[#40574a]">A quick practice loop</h2><ol className="mt-3 space-y-3 text-xs leading-5 text-[#718078]"><li><span className="mr-2 font-bold text-[#679074]">01</span>Choose one of the 100 prompts.</li><li><span className="mr-2 font-bold text-[#679074]">02</span>Speak or type a short answer.</li><li><span className="mr-2 font-bold text-[#679074]">03</span>Review the transcript feedback and try again.</li></ol></div>}</section>
            <section className="rounded-3xl border border-[#e1e8df] bg-white p-5 shadow-sm sm:p-6" aria-label="Recent speaking practice"><h2 className="text-sm font-bold text-[#40574a]">Recent responses <span className="ml-1 rounded-full bg-[#f0f5ed] px-2 py-1 text-[10px] text-[#5e7863]">{history.length}</span></h2>{history.length?<ul className="mt-3 divide-y divide-[#eef1ec]">{history.slice(0,4).map((item)=><li key={item.id} className="py-3"><div className="flex items-start justify-between gap-2"><p className="line-clamp-2 text-xs font-semibold leading-5 text-[#53665a]">{item.prompt}</p><span className="shrink-0 text-xs font-bold text-[#4b7155]">{item.estimated_score}/5</span></div><p className="mt-1 text-[10px] text-[#98a39a]">{item.word_count} words · {new Date(item.created_at).toLocaleDateString()}</p></li>)}</ul>:<p className="mt-3 text-xs leading-5 text-[#89958c]">Saved responses will appear here after you complete a review.</p>}</section></aside>
        </div>
      </div>
    </main>
  );
}
