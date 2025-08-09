import React, { useState, useEffect } from 'react';
import { fetchOJTByYear, exportOJTCompleted } from '../../services/api';

interface DetailsTableProps {
  onBack: () => void;
  selectedYear?: number;
}

export default function DetailsTable({ onBack, selectedYear }: DetailsTableProps) {
  const [ojtData, setOjtData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [coordinatorUsername, setCoordinatorUsername] = useState('');
  const [selectedRow, setSelectedRow] = useState<any | null>(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    // Get coordinator username from localStorage
    const user = localStorage.getItem('user');
    if (user) {
      const userData = JSON.parse(user);
      setCoordinatorUsername(userData.name || '');
    }

    const loadOJTData = async () => {
      if (selectedYear) {
        try {
          const data = await fetchOJTByYear(selectedYear.toString(), coordinatorUsername);
          setOjtData(data.ojt_data || []);
        } catch (error) {
          console.error('Error loading OJT data:', error);
          setOjtData([]);
        } finally {
          setLoading(false);
        }
      } else {
        setLoading(false);
      }
    };

    loadOJTData();
  }, [selectedYear, coordinatorUsername]);

  // Add handler for dropdown change (for demonstration, just updates local state)
  const handleStatusChange = (idx: number, newStatus: string) => {
    setOjtData((prev) => {
      const updated = [...prev];
      updated[idx] = { ...updated[idx], ojt_status: newStatus };
      return updated;
    });
  };

  // Handle export of completed OJT data
  const handleSendToAdmin = async () => {
    try {
      // Filter only completed OJT records
      const completedRecords = ojtData.filter(record => record.ojt_status === 'Completed');
      
      if (completedRecords.length === 0) {
        alert('No completed OJT records found to export.');
        return;
      }

      const result = await exportOJTCompleted(
        selectedYear?.toString(),
        completedRecords[0]?.course || 'BSIT',
        coordinatorUsername
      );

      if (result.success) {
        alert(`Successfully exported ${completedRecords.length} completed OJT records to Excel file.`);
      } else {
        alert('Failed to export data: ' + result.message);
      }
    } catch (error) {
      console.error('Export error:', error);
      alert('An error occurred while exporting the data.');
    }
  };

  // Inline styles
  const styles = {
    detailsTable: {
      margin: '40px auto',
      maxWidth: '90%',
    },
    table: {
      width: '100%',
      borderCollapse: 'collapse' as const,
      borderRadius: '8px',
      overflow: 'hidden',
      textAlign: 'left' as const,
    },
    th: {
      backgroundColor: '#5A6DFE',
      color: 'white',
      padding: '12px',
      fontWeight: '600',
    },
    td: {
      padding: '12px',
    },
    trEven: {
      padding: '12px',
      backgroundColor: '#f9f9f9',
    },
    complete: {
      padding: '12px',
      color: '#0093D9',
      fontWeight: '600',
    },
    incomplete: {
      padding: '12px',
      color: '#E95D35',
      fontWeight: '600',
    },
    tableActions: {
      marginTop: '20px',
      display: 'flex',
      justifyContent: 'space-between',
    },
    backBtn: {
      padding: '8px 20px',
      background: '#ccc',
      border: 'none',
      borderRadius: '20px',
      cursor: 'pointer',
    },
    sendBtn: {
      padding: '8px 20px',
      background: '#164B87',
      color: 'white',
      border: 'none',
      borderRadius: '20px',
      cursor: 'pointer',
    },
  };

  if (loading) {
    return (
      <div style={styles.detailsTable}>
        <div style={{ textAlign: 'center', padding: '40px' }}>
          Loading OJT data...
        </div>
      </div>
    );
  }

  return (
    <div style={styles.detailsTable}>
      <table style={styles.table}>
        <thead>
          <tr>
            <th style={styles.th}>Program Name</th>
            <th style={styles.th}>No.</th>
            <th style={styles.th}>Last Name</th>
            <th style={styles.th}>First Name</th>
            <th style={styles.th}>OJT Status</th>
          </tr>
        </thead>
        <tbody>
          {ojtData.length === 0 ? (
            <tr>
              <td colSpan={5} style={{ textAlign: 'center', padding: '20px', color: '#888' }}>
                No OJT data found for this year.
              </td>
            </tr>
          ) : (
            ojtData.map((ojt, idx) => (
              <tr key={ojt.id} style={idx % 2 === 1 ? styles.trEven : undefined} onClick={() => { setSelectedRow(ojt); setShowModal(true); }}>
                <td style={styles.td}>{ojt.course || ''}</td>
                <td style={styles.td}>{String(idx + 1).padStart(2, '0')}.</td>
                <td style={styles.td}>{ojt.last_name || ''}</td>
                <td style={styles.td}>{ojt.first_name || ''}</td>
                <td style={ojt.ojt_status === 'Completed' ? styles.complete : styles.incomplete} onClick={e => e.stopPropagation()}>
                  <select
                    value={ojt.ojt_status || 'Pending'}
                    onChange={e => handleStatusChange(idx, e.target.value)}
                    style={{ padding: '6px 12px', borderRadius: '8px', border: '1px solid #ccc' }}
                  >
                    <option value="Pending">Pending</option>
                    <option value="Incomplete">Incomplete</option>
                    <option value="Completed">Completed</option>
                  </select>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>

      <div style={styles.tableActions}>
        <button style={styles.backBtn} onClick={onBack}>Back</button>
        <button style={styles.sendBtn} onClick={handleSendToAdmin}>Send to Admin</button>
      </div>

      {/* Modal for row details */}
      {showModal && selectedRow && (
        <div style={{
          position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: 'rgba(0,0,0,0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
        }} onClick={() => setShowModal(false)}>
          <div style={{ background: 'white', borderRadius: 16, padding: 32, minWidth: 320, maxWidth: '90vw' }} onClick={e => e.stopPropagation()}>
            <h2>OJT Details</h2>
            <p><b>CTU ID:</b> {selectedRow.ctu_id || selectedRow.CTU_ID || ''}</p>
            <p><b>First Name:</b> {selectedRow.first_name || selectedRow.First_Name || selectedRow.name?.split(' ')[0] || ''}</p>
            <p><b>Middle Name:</b> {selectedRow.middle_name || selectedRow.Middle_Name || ''}</p>
            <p><b>Last Name:</b> {selectedRow.last_name || selectedRow.Last_Name || selectedRow.name?.split(' ').slice(-1)[0] || ''}</p>
            <p><b>Gender:</b> {selectedRow.gender || selectedRow.Gender || ''}</p>
            <p><b>Birthdate:</b> {selectedRow.birthdate || selectedRow.Birthdate || ''}</p>
            <p><b>Phone Number:</b> {selectedRow.phone_num || selectedRow.Phone_Number || ''}</p>
            <p><b>Address:</b> {selectedRow.address || selectedRow.Address || ''}</p>
            <p><b>Social Media:</b> {selectedRow.social_media || selectedRow.Social_Media || ''}</p>
            <p><b>Civil Status:</b> {selectedRow.civil_status || selectedRow.Civil_Status || ''}</p>
            <p><b>Age:</b> {selectedRow.age || selectedRow.Age || ''}</p>
            <p><b>Status:</b> {selectedRow.ojt_status || 'Pending'}</p>
            <button style={{ marginTop: 16, padding: '8px 24px', borderRadius: 8, background: '#5A6DFE', color: 'white', border: 'none', cursor: 'pointer' }} onClick={() => setShowModal(false)}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
}
