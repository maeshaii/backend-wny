// components/GenerateStatsModal.tsx
import React from 'react';

interface Props {
  onClose: () => void;
}

const GenerateStatsModal: React.FC<Props> = ({ onClose }) => {
  return (
    <div style={modalOverlay}>
      <div style={modalContent}>
        <h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>Generate Statistics</h2>
        <label>Year:</label>
        <select style={dropdown}>
          <option>2025</option>
          <option>2024</option>
          <option>2023</option>
        </select>
        <label>Course:</label>
        <select style={dropdown}>
          <option>BSIT</option>
          <option>BSIS</option>
          <option>BSCT</option>
        </select>
        <label>Type of Statistics:</label>
        <select style={dropdown}>
          <option>Employment Rate</option>
          <option>Salary Range</option>
        </select>
        <button onClick={onClose} style={generateButton}>Generate</button>
      </div>
    </div>
  );
};

const modalOverlay: React.CSSProperties = {
  position: 'fixed',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  backgroundColor: 'rgba(0, 0, 0, 0.5)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  zIndex: 1000
};

const modalContent: React.CSSProperties = {
  backgroundColor: 'white',
  padding: '30px',
  borderRadius: '10px',
  minWidth: '300px',
  display: 'flex',
  flexDirection: 'column',
  gap: '10px',
  alignItems: 'stretch'
};

const dropdown: React.CSSProperties = {
  padding: '8px',
  borderRadius: '8px',
  border: '1px solid #ccc'
};

const generateButton: React.CSSProperties = {
  marginTop: '15px',
  padding: '8px 12px',
  backgroundColor: '#4f46e5',
  color: 'white',
  border: 'none',
  borderRadius: '10px',
  cursor: 'pointer'
};

export default GenerateStatsModal;
