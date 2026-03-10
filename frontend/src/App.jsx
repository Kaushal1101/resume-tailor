import { useEffect, useMemo, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const baseStyles = {
  app: {
    fontFamily: "Inter, system-ui, sans-serif",
    height: "100vh",
    display: "grid",
    gridTemplateColumns: "320px 1fr",
    margin: 0,
  },
  sidebar: {
    borderRight: "1px solid #e5e7eb",
    padding: "16px",
    overflowY: "auto",
    background: "#f8fafc",
  },
  main: {
    padding: "20px",
    overflowY: "auto",
  },
  card: {
    border: "1px solid #d1d5db",
    borderRadius: "8px",
    padding: "10px",
    marginBottom: "10px",
    background: "white",
    cursor: "pointer",
  },
  cardActive: {
    border: "2px solid #2563eb",
  },
};

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options);
  if (!response.ok) {
    let detail = "Request failed";
    try {
      const json = await response.json();
      detail = json.detail || detail;
    } catch {
      // ignore non-json response
    }
    throw new Error(detail);
  }
  return response.json();
}

export default function App() {
  const [experiences, setExperiences] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [jd, setJd] = useState("");
  const [instruction, setInstruction] = useState("Make this more impact-focused and concise.");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [rewrittenBullets, setRewrittenBullets] = useState([]);

  useEffect(() => {
    const load = async () => {
      try {
        const items = await request("/experiences");
        setExperiences(items);
        if (items.length > 0) {
          setSelectedId(items[0].id);
        }
      } catch (err) {
        setError(err.message);
      }
    };
    load();
  }, []);

  const selectedExperience = useMemo(
    () => experiences.find((item) => item.id === selectedId),
    [experiences, selectedId]
  );

  const handleRewrite = async () => {
    if (!selectedExperience) {
      setError("Select an experience first.");
      return;
    }
    if (!jd.trim()) {
      setError("Please paste a job description.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const result = await request("/rewrite", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          jd,
          experience_id: selectedExperience.id,
          rewrite_instruction: instruction,
        }),
      });
      setRewrittenBullets(result.rewritten_bullets || []);
    } catch (err) {
      setError(err.message);
      setRewrittenBullets([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={baseStyles.app}>
      <aside style={baseStyles.sidebar}>
        <h2 style={{ marginTop: 0 }}>Experiences</h2>
        <p style={{ color: "#475569", marginTop: 0 }}>
          Scroll and click a section to rewrite.
        </p>
        {experiences.map((exp) => (
          <div
            key={exp.id}
            style={{
              ...baseStyles.card,
              ...(selectedId === exp.id ? baseStyles.cardActive : {}),
            }}
            onClick={() => setSelectedId(exp.id)}
          >
            <div style={{ fontWeight: 600 }}>{exp.title}</div>
            <div style={{ color: "#475569", fontSize: 14 }}>{exp.organization}</div>
            <div style={{ color: "#64748b", fontSize: 12, marginTop: 4 }}>{exp.type}</div>
          </div>
        ))}
      </aside>

      <main style={baseStyles.main}>
        <h1 style={{ marginTop: 0 }}>Resume Workspace</h1>
        <p style={{ color: "#475569" }}>
          Paste JD, add rewrite instruction, and rewrite only the selected experience.
        </p>

        {selectedExperience && (
          <section>
            <h3>
              Selected: {selectedExperience.title} @ {selectedExperience.organization}
            </h3>
            <ul>
              {selectedExperience.bullets.map((bullet, idx) => (
                <li key={`${selectedExperience.id}-${idx}`}>{bullet}</li>
              ))}
            </ul>
          </section>
        )}

        <section style={{ marginTop: 20 }}>
          <label style={{ display: "block", fontWeight: 600, marginBottom: 8 }}>
            Job Description
          </label>
          <textarea
            value={jd}
            onChange={(event) => setJd(event.target.value)}
            rows={8}
            style={{ width: "100%", padding: 10, borderRadius: 8, border: "1px solid #cbd5e1" }}
          />
        </section>

        <section style={{ marginTop: 12 }}>
          <label style={{ display: "block", fontWeight: 600, marginBottom: 8 }}>
            Rewrite Instruction
          </label>
          <input
            type="text"
            value={instruction}
            onChange={(event) => setInstruction(event.target.value)}
            style={{ width: "100%", padding: 10, borderRadius: 8, border: "1px solid #cbd5e1" }}
          />
        </section>

        <button
          onClick={handleRewrite}
          disabled={loading}
          style={{
            marginTop: 14,
            padding: "10px 16px",
            border: "none",
            borderRadius: 8,
            background: "#2563eb",
            color: "white",
            cursor: "pointer",
          }}
        >
          {loading ? "Rewriting..." : "Rewrite Selected Experience"}
        </button>

        {error && <p style={{ color: "#dc2626" }}>{error}</p>}

        <section style={{ marginTop: 20 }}>
          <h3>Rewritten Bullets</h3>
          {rewrittenBullets.length === 0 ? (
            <p style={{ color: "#64748b" }}>No rewritten bullets yet.</p>
          ) : (
            <ol>
              {rewrittenBullets.map((bullet, idx) => (
                <li key={`rewrite-${idx}`}>{bullet}</li>
              ))}
            </ol>
          )}
        </section>
      </main>
    </div>
  );
}
