import { useState } from 'react';
import './style.css';

type Result = { report: string; evidence: { repository: { name: string; url: string; description?: string; stars: number; language?: string }; issues: { title: string; url: string; state: string }[]; pull_requests: { title: string; url: string; state: string }[]; commits: { message: string; url: string }[] } };

export default function App() {
  const [repository, setRepository] = useState('');
  const [question, setQuestion] = useState('Investigate recent activity and summarize the main themes.');
  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setError(''); setResult(null); setLoading(true);
    try {
      const response = await fetch('/api/investigate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ repository, question }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Investigation failed');
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unexpected error');
    } finally { setLoading(false); }
  }

  return <main className="shell">
    <header><span className="eyebrow">READ-ONLY REPOSITORY RESEARCH</span><h1>GitHub Investigation Agent</h1><p>Gather repository activity and turn source-linked evidence into a concise investigation report.</p></header>
    <form className="panel" onSubmit={submit}>
      <label>GitHub repository<input required value={repository} onChange={e => setRepository(e.target.value)} placeholder="owner/repository" pattern="[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+" /></label>
      <label>Investigation question<textarea required minLength={5} maxLength={2000} value={question} onChange={e => setQuestion(e.target.value)} rows={3} /></label>
      <button disabled={loading}>{loading ? 'Investigating…' : 'Investigate repository'}</button>
      <small>Public repositories work without credentials. Configure a GitHub token in the backend for authorized private repository access.</small>
    </form>
    {error && <div className="error" role="alert">{error}</div>}
    {result && <>
      <section className="panel"><h2><a href={result.evidence.repository.url} target="_blank" rel="noreferrer">{result.evidence.repository.name}</a></h2><p>{result.evidence.repository.description}</p><p>{result.evidence.repository.language || 'Unknown language'} · {result.evidence.repository.stars} stars</p><article className="report">{result.report}</article></section>
      <section className="grid"><Evidence title="Issues" items={result.evidence.issues} /><Evidence title="Pull requests" items={result.evidence.pull_requests} /><Evidence title="Recent commits" items={result.evidence.commits} /></section>
    </>}
    <footer>Verify conclusions against linked GitHub source material. AI summaries can be incomplete or incorrect.</footer>
  </main>;
}

function Evidence({ title, items }: { title: string; items: { title?: string; message?: string; url: string; state?: string }[] }) {
  return <section className="panel"><h2>{title}</h2>{items.length ? <ul>{items.slice(0, 5).map((item, index) => <li key={`${item.url}-${index}`}><a href={item.url} target="_blank" rel="noreferrer">{item.title || item.message}</a>{item.state && <small> · {item.state}</small>}</li>)}</ul> : <p>No recent items found.</p>}</section>;
}
