import React, { useState } from 'react';
import PDFViewerWithTextSelection from './text_selection';
import './index.css';

function App() {
  const [file, setFile] = useState(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setFile(URL.createObjectURL(file));
    }
  };

  return (
    <div>
      <h1>PDF Viewer with Text Selection</h1>
      <input type="file" accept="application/pdf" onChange={handleFileChange} />
      {file && <PDFViewerWithTextSelection file={file} />}
    </div>
  );
}

export default App;
