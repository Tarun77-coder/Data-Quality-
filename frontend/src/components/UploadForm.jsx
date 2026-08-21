import { useState } from "react";
import { uploadFile } from "../api.js";

export default function UploadForm({ onUploaded }) {
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError("");
    try {
      const result = await uploadFile(file);
      onUploaded(result);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>1. Upload dataset</h2>
      <input type="file" accept=".csv,.json" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleUpload} disabled={!file || loading}>
        {loading ? "Uploading..." : "Upload"}
      </button>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}
