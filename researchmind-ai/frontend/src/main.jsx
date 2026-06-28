import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  BookOpen,
  Brain,
  Clock3,
  Download,
  FileText,
  History,
  Home,
  Moon,
  Play,
  Search,
  Settings,
  ShieldCheck,
  Sun
} from "lucide-react";
import "./styles.css";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "https://research-mind-ai.onrender.com";
const navItems = [
  { id: "home", label: "Home", icon: Home },
  { id: "research", label: "Research", icon: Search },
  { id: "progress", label: "Progress", icon: Clock3 },
  { id: "history", label: "History", icon: History },
  { id: "report", label: "Report", icon: FileText },
  { id: "settings", label: "Settings", icon: Settings }
];

function App() {
  const [page, setPage] = useState("home");
  const [dark, setDark] = useState(true);
  const [topic, setTopic] = useState("Agentic AI in scientific research");
  const [depth, setDepth] = useState(2);
  const [citationStyle, setCitationStyle] = useState("APA");
  const [loading, setLoading] = useState(false);
  const [currentRun, setCurrentRun] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);

  async function refreshHistory() {
    try {
      const response = await fetch(`${API_BASE}/research/history`);
      if (response.ok) setHistory(await response.json());
    } catch {
      setError("Backend is not running at localhost:8000. Start FastAPI to enable research APIs.");
    }
  }

  useEffect(() => {
    refreshHistory().catch(() => undefined);
  }, []);

  async function startResearch(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setPage("progress");
    try {
      const response = await fetch(`${API_BASE}/research/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: topic, query: topic, depth: Number(depth), citation_style: citationStyle })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Research failed");
      const detail = await fetchResearchDetail(data.id);
      setCurrentRun(detail || { id: data.id, status: data.status, topic: data.title, report: null, events: [] });
      await refreshHistory();
      setPage("report");
    } catch (err) {
      setError(err.message.includes("Failed to fetch") ? "Backend is not running at localhost:8000. Start FastAPI to run research." : err.message);
      setPage("research");
    } finally {
      setLoading(false);
    }
  }

  async function fetchResearchDetail(projectId) {
    const response = await fetch(`${API_BASE}/research/${projectId}`);
    if (!response.ok) return null;
    const detail = await response.json();
    return {
      id: detail.id,
      status: detail.status,
      topic: detail.title,
      report: detail.report,
      reportId: detail.report_id,
      events: detail.state?.logs || detail.execution_logs || []
    };
  }

  async function openResearch(projectId) {
    const detail = await fetchResearchDetail(projectId);
    if (!detail) return;
    setCurrentRun(detail);
    setPage("report");
  }

  async function openReport(reportId) {
    const response = await fetch(`${API_BASE}/report/${reportId}`);
    if (!response.ok) return;
    const report = await response.json();
    setCurrentRun({ id: report.research_id, status: "completed", topic: report.title.replace("Research Report: ", ""), report, events: [] });
    setPage("report");
  }

  const trustedSources = useMemo(() => {
    const sources = currentRun?.report?.source_cards || [];
    return sources.map((source) => ({
      title: source.title,
      url: source.url,
      score: Math.round(source.trust_score || 0),
      reason: source.evaluation_reason
    }));
  }, [currentRun]);

  return (
    <div className="min-h-screen bg-slate-100 text-slate-950 transition dark:bg-ink dark:text-slate-100">
      <aside className="fixed inset-y-0 left-0 z-20 hidden w-72 border-r border-slate-200 bg-white/90 p-5 backdrop-blur dark:border-slate-800 dark:bg-panel/90 lg:block">
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-md bg-signal text-ink">
            <Brain size={24} />
          </div>
          <div>
            <h1 className="text-lg font-semibold">ResearchMind AI</h1>
            <p className="text-xs text-slate-500 dark:text-slate-400">Autonomous research workflow</p>
          </div>
        </div>
        <nav className="mt-8 space-y-2">
          {navItems.map((item) => (
            <button key={item.id} onClick={() => setPage(item.id)} className={`nav-button ${page === item.id ? "nav-active" : ""}`}>
              <item.icon size={18} />
              <span>{item.label}</span>
            </button>
          ))}
        </nav>
      </aside>

      <main className="lg:pl-72">
        <header className="sticky top-0 z-10 flex items-center justify-between border-b border-slate-200 bg-white/80 px-4 py-3 backdrop-blur dark:border-slate-800 dark:bg-ink/75 sm:px-8">
          <div>
            <p className="text-xs uppercase tracking-wide text-signal">Multi-agent research system</p>
            <h2 className="text-xl font-semibold">{navItems.find((item) => item.id === page)?.label}</h2>
          </div>
          <button className="icon-button" onClick={() => setDark((value) => !value)} title="Toggle dark mode">
            {dark ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </header>

        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-8">
          {page === "home" && <HomePage onStart={() => setPage("research")} />}
          {page === "research" && (
            <ResearchPage
              topic={topic}
              setTopic={setTopic}
              depth={depth}
              setDepth={setDepth}
              citationStyle={citationStyle}
              setCitationStyle={setCitationStyle}
              loading={loading}
              error={error}
              onSubmit={startResearch}
            />
          )}
          {page === "progress" && <ProgressPage run={currentRun} loading={loading} error={error} />}
          {page === "history" && <HistoryPage history={history} onOpen={openResearch} refresh={refreshHistory} />}
          {page === "report" && <ReportViewer run={currentRun} sources={trustedSources} />}
          {page === "settings" && (
            <SettingsPage
              apiBase={API_BASE}
              dark={dark}
              setDark={setDark}
            />
          )}
        </div>
      </main>
    </div>
  );
}

function HomePage({ onStart }) {
  return (
    <section className="grid gap-8 xl:grid-cols-[1.1fr_0.9fr]">
      <div className="rounded-lg bg-white p-8 shadow-sm dark:bg-panel">
        <div className="flex items-center gap-2 text-signal">
          <ShieldCheck size={20} />
          <span className="text-sm font-semibold uppercase">Verified autonomous research</span>
        </div>
        <h2 className="mt-4 max-w-3xl text-4xl font-bold leading-tight sm:text-5xl">ResearchMind AI turns a topic into a cited professional report.</h2>
        <p className="mt-5 max-w-2xl text-slate-600 dark:text-slate-300">
          Planner, search, source evaluation, extraction, verification, gap analysis, summarization, citation, and report agents coordinate through LangGraph.
        </p>
        <button onClick={onStart} className="primary-button mt-7">
          <Play size={18} />
          Start Research
        </button>
      </div>
      <div className="grid gap-4">
        {["Planner", "Search", "Evaluator", "Extractor", "Verifier", "Gap Analysis", "Summarizer", "Citation", "Report"].map((agent, index) => (
          <div key={agent} className="flex items-center gap-4 rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-panel">
            <span className="grid h-9 w-9 place-items-center rounded-md bg-slate-900 text-sm font-semibold text-white dark:bg-signal dark:text-ink">{index + 1}</span>
            <span className="font-medium">{agent} Agent</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function ResearchPage({ topic, setTopic, depth, setDepth, citationStyle, setCitationStyle, loading, error, onSubmit }) {
  return (
    <form onSubmit={onSubmit} className="grid gap-6 lg:grid-cols-[1fr_360px]">
      <div className="rounded-lg bg-white p-6 shadow-sm dark:bg-panel">
        <label className="text-sm font-semibold" htmlFor="topic">Research Topic</label>
        <textarea id="topic" value={topic} onChange={(event) => setTopic(event.target.value)} className="input mt-3 min-h-44" required />
        {error && <p className="mt-3 rounded-md bg-red-100 px-3 py-2 text-sm text-red-700 dark:bg-red-950 dark:text-red-200">{error}</p>}
        <button className="primary-button mt-5" disabled={loading}>
          {loading ? <span className="loader" /> : <Brain size={18} />}
          {loading ? "Researching" : "Launch Agents"}
        </button>
      </div>
      <div className="rounded-lg bg-white p-6 shadow-sm dark:bg-panel">
        <label className="text-sm font-semibold" htmlFor="depth">Research Depth</label>
        <input id="depth" type="range" min="1" max="4" value={depth} onChange={(event) => setDepth(event.target.value)} className="mt-4 w-full" />
        <div className="mt-2 text-sm text-slate-500">Depth {depth}</div>
        <label className="mt-6 block text-sm font-semibold" htmlFor="citation">Citation Style</label>
        <select id="citation" value={citationStyle} onChange={(event) => setCitationStyle(event.target.value)} className="input mt-3">
          <option>APA</option>
          <option>IEEE</option>
          <option>MLA</option>
        </select>
      </div>
    </form>
  );
}

function ProgressPage({ run, loading, error }) {
  const events = run?.events || [];
  return (
    <div className="rounded-lg bg-white p-6 shadow-sm dark:bg-panel">
      {loading && <div className="mb-5 flex items-center gap-3 text-signal"><span className="loader" /> Agents are working through the graph.</div>}
      {error && <div className="mb-5 text-red-500">{error}</div>}
      <div className="space-y-4">
        {(events.length ? events : ["Planner", "Search", "Source Evaluator", "Information Extractor", "Fact Checker", "Gap Analysis", "Summarizer", "Citation", "Report Generator"].map((agent) => ({ agent, status: loading ? "running" : "pending", message: "Waiting for workflow update" }))).map((event, index) => (
          <div key={`${event.agent}-${index}`} className="flex gap-4">
            <div className="flex flex-col items-center">
              <span className={`h-4 w-4 rounded-full ${event.status === "completed" ? "bg-signal" : "bg-accent"}`} />
              <span className="h-full w-px bg-slate-200 dark:bg-slate-800" />
            </div>
            <div className="pb-5">
              <p className="font-semibold">{event.agent}</p>
              <p className="text-sm text-slate-500 dark:text-slate-400">{event.message}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function HistoryPage({ history, onOpen, refresh }) {
  return (
    <div className="rounded-lg bg-white p-6 shadow-sm dark:bg-panel">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-semibold">Research History</h3>
        <button className="secondary-button" onClick={refresh}>Refresh</button>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="text-slate-500">
            <tr><th className="py-3">Topic</th><th>Status</th><th>Updated</th><th></th></tr>
          </thead>
          <tbody>
            {history.map((item) => (
              <tr key={item.id} className="border-t border-slate-200 dark:border-slate-800">
                <td className="py-3 font-medium">Research #{item.research_id || item.id}</td>
                <td>{item.status}</td>
                <td>{new Date(item.created_at || item.updated_at).toLocaleString()}</td>
                <td className="text-right"><button className="secondary-button" onClick={() => onOpen(item.research_id || item.id)}>Open</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ReportViewer({ run, sources }) {
  const report = run?.report;
  if (!report) return <EmptyState />;
  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_360px]">
      <article className="rounded-lg bg-white p-6 shadow-sm dark:bg-panel">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <h2 className="text-2xl font-bold">{report.title}</h2>
          <a className="primary-button" href={`${API_BASE}/report/${run.reportId || report.id}/pdf`}>
            <Download size={18} />
            Download PDF
          </a>
        </div>
        <div className="mt-6 grid gap-2 rounded-lg bg-slate-100 p-4 dark:bg-slate-950">
          {report.table_of_contents.map((item) => <span key={item} className="text-sm">{item}</span>)}
        </div>
        {Object.entries(report.sections).map(([title, body]) => (
          <section key={title} className="mt-7">
            <h3 className="text-xl font-semibold text-signal">{title}</h3>
            <p className="mt-3 whitespace-pre-line leading-7 text-slate-700 dark:text-slate-300">{body}</p>
          </section>
        ))}
        <section className="mt-7">
          <h3 className="text-xl font-semibold text-signal">Conclusion</h3>
          <p className="mt-3 leading-7 text-slate-700 dark:text-slate-300">{report.conclusion}</p>
        </section>
      </article>
      <aside className="space-y-4">
        {sources.map((source) => <SourceCard key={source.url} source={source} />)}
      </aside>
    </div>
  );
}

function SourceCard({ source }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-panel">
      <div className="flex items-center justify-between gap-3">
        <BookOpen size={18} className="text-signal" />
        <span className="rounded-md bg-signal/15 px-2 py-1 text-xs font-semibold text-signal">{source.score}% trust</span>
      </div>
      <h4 className="mt-3 font-semibold">{source.title}</h4>
      {source.reason && <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">{source.reason}</p>}
      <a className="mt-2 block break-words text-sm text-signal" href={source.url} target="_blank" rel="noreferrer">{source.url}</a>
    </div>
  );
}

function SettingsPage({ apiBase, dark, setDark }) {
  return (
    <div className="rounded-lg bg-white p-6 shadow-sm dark:bg-panel">
      <h3 className="text-lg font-semibold">Settings</h3>
      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        <div>
          <label className="text-sm font-semibold">API Base URL</label>
          <input className="input mt-2" value={apiBase} readOnly />
        </div>
        <label className="flex items-center gap-3 rounded-lg border border-slate-200 p-4 dark:border-slate-800">
          <input type="checkbox" checked={dark} onChange={(event) => setDark(event.target.checked)} />
          Dark mode
        </label>
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="grid min-h-[420px] place-items-center rounded-lg bg-white p-8 text-center shadow-sm dark:bg-panel">
      <div>
        <FileText className="mx-auto text-slate-400" size={42} />
        <h3 className="mt-4 text-xl font-semibold">No report selected</h3>
        <p className="mt-2 text-slate-500">Run a research workflow or open a saved report from history.</p>
      </div>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
