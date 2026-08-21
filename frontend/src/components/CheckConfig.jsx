import { useState } from "react";
import { runChecks } from "../api.js";

export default function CheckConfig({ runId, columns, onResults }) {
  const [expectedColumns, setExpectedColumns] = useState(columns.join(","));
  const [ruleColumn, setRuleColumn] = useState(columns[0] || "");
  const [ruleType, setRuleType] = useState("range");
  const [min, setMin] = useState("");
  const [max, setMax] = useState("");
  const [pattern, setPattern] = useState("");
  const [enableCustomRule, setEnableCustomRule] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleRun = async () => {
    setLoading(true);
    setError("");

    try {
      let customRule = null;

      if (enableCustomRule && ruleColumn) {
        customRule =
          ruleType === "range"
            ? {
                column: ruleColumn,
                type: "range",
                min: min === "" ? null : Number(min),
                max: max === "" ? null : Number(max),
              }
            : {
                column: ruleColumn,
                type: "regex",
                pattern,
              };
      }

      const result = await runChecks({
        runId,
        expectedColumns: expectedColumns
          .split(",")
          .map((column) => column.trim())
          .filter(Boolean),
        customRule,
      });

      onResults(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Checks failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section>
      <h2>2. Configure checks</h2>

      <label>
        Expected columns (comma-separated):
        <input
          value={expectedColumns}
          onChange={(e) => setExpectedColumns(e.target.value)}
          style={{ display: "block", width: "100%", marginBottom: 12 }}
        />
      </label>

      <fieldset>
        <legend>Custom rule</legend>

        <label>
          <input
            type="checkbox"
            checked={enableCustomRule}
            onChange={(e) => setEnableCustomRule(e.target.checked)}
          />{" "}
          Enable custom rule
        </label>

        {enableCustomRule && (
          <>
            <label>
              Column:
              <select
                value={ruleColumn}
                onChange={(e) => setRuleColumn(e.target.value)}
              >
                {columns.map((column) => (
                  <option key={column} value={column}>
                    {column}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Type:
              <select
                value={ruleType}
                onChange={(e) => setRuleType(e.target.value)}
              >
                <option value="range">Range</option>
                <option value="regex">Regex</option>
              </select>
            </label>

            {ruleType === "range" ? (
              <>
                <input
                  type="number"
                  placeholder="Minimum"
                  value={min}
                  onChange={(e) => setMin(e.target.value)}
                />
                <input
                  type="number"
                  placeholder="Maximum"
                  value={max}
                  onChange={(e) => setMax(e.target.value)}
                />
              </>
            ) : (
              <input
                placeholder="Regex pattern"
                value={pattern}
                onChange={(e) => setPattern(e.target.value)}
              />
            )}
          </>
        )}
      </fieldset>

      <button onClick={handleRun} disabled={loading}>
        {loading ? "Running..." : "Run checks"}
      </button>

      {error && <p style={{ color: "crimson" }}>{error}</p>}
    </section>
  );
}
