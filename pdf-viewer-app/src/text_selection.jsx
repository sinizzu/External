// PDFViewerWithTextSelection.js
import React, { useState, useRef } from 'react';
import { Worker, Viewer } from '@react-pdf-viewer/core';
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout';
import { pdfjs } from 'react-pdf';
import '@react-pdf-viewer/core/lib/styles/index.css';
import '@react-pdf-viewer/default-layout/lib/styles/index.css';
import { usePopper } from 'react-popper';

const PDFViewerWithTextSelection = ({ file }) => {
    const defaultLayoutPluginInstance = defaultLayoutPlugin();
    const [selectionText, setSelectionText] = useState('');
    const [showPopper, setShowPopper] = useState(false);
    const [referenceElement, setReferenceElement] = useState(null);
    const [popperElement, setPopperElement] = useState(null);
    const { styles, attributes } = usePopper(referenceElement, popperElement, 
      {placement: 'top', // 팝오버가 텍스트 위에 나타나도록 설정
});
    
    pdfjs.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.js';

    const handleTextSelection = () => {
        const selection = window.getSelection();
        const selectedText = selection.toString();
        if (selectedText) {
            setSelectionText(selectedText);
            setShowPopper(true);
            const range = selection.getRangeAt(0);
            const rect = range.getBoundingClientRect();
            setReferenceElement({
                getBoundingClientRect: () => rect,
                clientWidth: rect.width,
                clientHeight: rect.height,
            });
        } else {
            setShowPopper(false);
        }
    };

    return (
        <div style={{ height: '750px' }} onMouseUp={handleTextSelection}>
            <Worker workerUrl="/pdf.worker.min.js">
                <Viewer
                    fileUrl={file}
                    plugins={[defaultLayoutPluginInstance]}
                />
            </Worker>
            {showPopper && (
                <div ref={setPopperElement} style={styles.popper} {...attributes.popper} className="popper">
                    <div className="popper-content">{selectionText}</div>
                </div>
            )}
        </div>
    );
};

export default PDFViewerWithTextSelection;
