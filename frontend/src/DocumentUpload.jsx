import { uploadDocument } from "./api";
import { useState } from 'react'


export default function DocumentUpload({ onDocumentLoaded, onDocumentCleared }) {
    const [status, setStatus] = useState('idle');
    const [error, setError] = useState(null);
    const [filename, setFilename] = useState(null);    

    async function handleFileChange(e) {

        const file = e.target.files[0]
        if (!file) return
        
        
        try {
            setError(null);
            setStatus('uploading');
            const response = await uploadDocument(file);
            setFilename(file.name);
            setStatus('loaded');
            onDocumentLoaded(file.name) // calls handleDocumentLoaded() in App.jsx
        } catch (err) {
            setError(err.message);
            setStatus('error');
        }
    }

    async function handleClear() {
        setStatus('idle');
        setError(null);
        setFilename(null);
        onDocumentCleared();
    }

    return (
        <div className="document-upload">
            <h2>Upload a Document</h2>  
            {status === 'idle' && (
                <label className="upload-btn">
                    📎 Upload PDF
                    <input type="file" accept=".pdf" onChange={handleFileChange} style={{display:'none'}} />
                </label>
            )}
            {status === 'uploading' && <span>⏳ Parsing PDF...</span>}
            {status === 'loaded' && (
                <span>
                    📄 {filename}
                    <button onClick={handleClear}>✕</button>
                </span>
            )}
            {status === 'error' && (
                <span>
                    ⚠️ {error}
                    <button onClick={() => setStatus('idle')}>Retry</button>
                </span>
            )}
                    </div>
    );

}
