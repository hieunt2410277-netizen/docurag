import React, { useState } from "react";

const API_BASE = "http://127.0.0.1:8000";

export default function App() {
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  async function uploadDocument() {
    if (!file) return;

    setUploadStatus("Indexing document...");

    const form = new FormData();
    form.append("file", file);

    try {
      const res = await fetch(`${API_BASE}/documents/upload`, {
        method: "POST",
        body: form,
      });

      const data = await res.json();

      if (!res.ok) throw new Error(data.detail || "Upload failed");

      setUploadStatus(
        `${data.filename} indexed successfully (${data.chunks_added} chunks).`
      );
    } catch (err) {
      setUploadStatus(`Error: ${err.message}`);
    }
  }

  async function askQuestion(e) {
    e.preventDefault();

    const q = question.trim();
    if (!q || loading) return;

    setMessages((prev) => [...prev, { role: "user", text: q }]);
    setQuestion("");
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });

      const data = await res.json();

      if (!res.ok) throw new Error(data.detail || "Chat failed");

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: data.answer,
          sources: data.sources || [],
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: `Error: ${err.message}`, sources: [] },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page">
      <section className="hero">
        <div>
          <p className="eyebrow">AI ENGINEERING PROJECT</p>
          <h1>DocuRAG</h1>
          <p className="subtitle">
            Upload a document, index it with BGE-M3 embeddings, and ask
            questions grounded in retrieved context.
          </p>
        </div>
      </section>

      <section className="card">
        <h2>1. Upload & Index</h2>
        <div className="uploadRow">
          <input
            type="file"
            accept=".pdf,.txt,.md"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
          <button onClick={uploadDocument} disabled={!file}>
            Index document
          </button>
        </div>
        {uploadStatus && <p className="status">{uploadStatus}</p>}
      </section>

      <section className="card chatCard">
        <h2>2. Ask your document</h2>

        <div className="messages">
          {messages.length === 0 && (
            <div className="empty">
              Ask a question after uploading a document.
            </div>
          )}

          {messages.map((message, idx) => (
            <div key={idx} className={`message ${message.role}`}>
              <strong>
                {message.role === "user" ? "You" : "DocuRAG"}
              </strong>
              <p>{message.text}</p>

              {message.sources?.length > 0 && (
                <details>
                  <summary>Sources ({message.sources.length})</summary>
                  <div className="sources">
                    {message.sources.map((source, sourceIdx) => (
                      <div className="source" key={sourceIdx}>
                        <strong>
                          {source.source}
                          {source.page ? ` · page ${source.page}` : ""}
                        </strong>
                        <p>{source.text}</p>
                      </div>
                    ))}
                  </div>
                </details>
              )}
            </div>
          ))}

          {loading && <div className="message assistant">Thinking...</div>}
        </div>

        <form onSubmit={askQuestion} className="chatForm">
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="What does the document say about...?"
          />
          <button type="submit" disabled={loading}>
            Ask
          </button>
        </form>
      </section>
    </main>
  );
}
