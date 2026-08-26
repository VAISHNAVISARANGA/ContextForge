import { useEffect, useState } from "react";
import { listDocuments, uploadDocument } from "../api";

export default function DocumentUpload() {
  const [docs, setDocs] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const refresh = async () => {
    const res = await listDocuments();
    setDocs(res.data);
  };

  useEffect(() => {
    refresh();
  }, []);

  const handleFile = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    setError("");
    try {
      await uploadDocument(file);
      await refresh();
    } catch (err) {
      setError(err.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  return (
    <div className="doc-panel">
      <h3>Documents</h3>
      <label className="upload-btn">
        {uploading ? "Uploading..." : "Upload PDF/DOCX"}
        <input type="file" accept=".pdf,.docx" onChange={handleFile} hidden />
      </label>
      {error && <p className="error">{error}</p>}
      <ul>
        {docs.map((d) => (
          <li key={d.id}>
            {d.filename} <span className="chunks">({d.num_chunks} chunks)</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
