import React, { useState } from "react";
import { getHealth, analyzeLite } from "../services/api";

const DevPanel: React.FC = () => {
  const [healthStatus, setHealthStatus] = useState<string | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);

  const [token, setToken] = useState("ETH");
  const [timeframe, setTimeframe] = useState("4h");
  const [liteResult, setLiteResult] = useState<any>(null);
  const [liteError, setLiteError] = useState<string | null>(null);
  const [isLoadingLite, setIsLoadingLite] = useState(false);

  async function handleCheckHealth() {
    try {
      setHealthError(null);
      const data = await getHealth();
      setHealthStatus(JSON.stringify(data));
    } catch (err: any) {
      setHealthStatus(null);
      setHealthError(err.message ?? "Health check failed");
    }
  }

  async function handleAnalyzeLite() {
    try {
      setIsLoadingLite(true);
      setLiteError(null);
      const data = await analyzeLite(token, timeframe);
      setLiteResult(data);
    } catch (err: any) {
      setLiteResult(null);
      setLiteError(err.message ?? "LITE analysis failed");
    } finally {
      setIsLoadingLite(false);
    }
  }

  return (
    <div style={{ border: "1px solid #444", padding: "16px", borderRadius: "8px", marginTop: "16px" }}>
      <h2 style={{ fontSize: "18px", marginBottom: "8px" }}>Dev Panel · Backend Test</h2>

      <div style={{ marginBottom: "12px" }}>
        <button onClick={handleCheckHealth} style={{ padding: "6px 12px" }}>
          Check /health
        </button>
        <div style={{ marginTop: "8px", fontSize: "14px" }}>
          {healthStatus && <div>Health OK: <code>{healthStatus}</code></div>}
          {healthError && <div style={{ color: "red" }}>Error: {healthError}</div>}
        </div>
      </div>

      <hr style={{ margin: "12px 0" }} />

      <div>
        <h3 style={{ fontSize: "16px", marginBottom: "8px" }}>LITE Signal</h3>
        <div style={{ display: "flex", gap: "8px", marginBottom: "8px", flexWrap: "wrap" }}>
          <label>
            Token:
            <select
              value={token}
              onChange={(e) => setToken(e.target.value)}
              style={{ marginLeft: "4px" }}
            >
              <option value="ETH">ETH</option>
              <option value="BTC">BTC</option>
              <option value="SOL">SOL</option>
            </select>
          </label>

          <label>
            Timeframe:
            <select
              value={timeframe}
              onChange={(e) => setTimeframe(e.target.value)}
              style={{ marginLeft: "4px" }}
            >
              <option value="1h">1h</option>
              <option value="4h">4h</option>
            </select>
          </label>

          <button onClick={handleAnalyzeLite} style={{ padding: "6px 12px" }} disabled={isLoadingLite}>
            {isLoadingLite ? "Loading..." : "Get LITE signal"}
          </button>
        </div>

        {liteError && <div style={{ color: "red", fontSize: "14px" }}>Error: {liteError}</div>}

        {liteResult && (
          <pre
            style={{
              marginTop: "8px",
              background: "#111",
              color: "#eee",
              padding: "8px",
              borderRadius: "4px",
              maxHeight: "240px",
              overflow: "auto",
              fontSize: "12px",
            }}
          >
{JSON.stringify(liteResult, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
};

export default DevPanel;
