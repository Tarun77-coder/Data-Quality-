import { downloadResults } from "../api.js";

export default function ResultsView({ results, runId }) {
  if (!results) return null;

  const { summary, issues = [] } = results;

  return (
    <section>
      <h2>3. Results</h2>

      <h3>Summary</h3>
      <pre>{JSON.stringify(summary, null, 2)}</pre>

      <h3>Issues ({issues.length})</h3>
      {issues.length === 0 ? (
        <p>No data-quality issues were found. 🎉</p>
      ) : (
        <table border="1" cellPadding="6">
          <thead>
            <tr>
              <th>Row</th>
              <th>Column</th>
              <th>Check</th>
              <th>Detail</th>
            </tr>
          </thead>
          <tbody>
            {issues.map((issue, i) => (
              <tr key={`${issue.check}-${issue.row_index}-${issue.column}-${i}`}>
                <td>{issue.row_index ?? "-"}</td>
                <td>{issue.column ?? "-"}</td>
                <td>{issue.check}</td>
                <td>{issue.detail}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <div style={{ marginTop: 16 }}>
        <button onClick={() => downloadResults(runId, "csv")}>
          Export CSV
        </button>{" "}
        <button onClick={() => downloadResults(runId, "json")}>
          Export JSON
        </button>
      </div>
    </section>
  );
}
