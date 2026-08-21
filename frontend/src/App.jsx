import { useEffect, useState } from "react";
import { supabase } from "./api.js";
import Auth from "./components/Auth.jsx";
import UploadForm from "./components/UploadForm.jsx";
import CheckConfig from "./components/CheckConfig.jsx";
import ResultsView from "./components/ResultsView.jsx";

export default function App() {
  const [session, setSession] = useState(null);
  const [uploadInfo, setUploadInfo] = useState(null); // { run_id, columns, row_count }
  const [results, setResults] = useState(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => setSession(data.session));
    const { data: listener } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });
    return () => listener.subscription.unsubscribe();
  }, []);

  if (!session) {
    return <Auth onAuthed={setSession} />;
  }

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: 20 }}>
      <h1>Data Quality Auditor</h1>
      <button onClick={() => supabase.auth.signOut()}>Log out</button>

      <UploadForm onUploaded={(info) => { setUploadInfo(info); setResults(null); }} />

      {uploadInfo && (
        <CheckConfig
          runId={uploadInfo.run_id}
          columns={uploadInfo.columns}
          onResults={setResults}
        />
      )}

      {results && <ResultsView results={results} runId={uploadInfo.run_id} />}
    </div>
  );
}
