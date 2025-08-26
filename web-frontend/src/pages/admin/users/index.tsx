// index.tsx
import React, { useState, useEffect } from 'react';
import Sidebar from '../global/sidebar';
import { fetchAlumniStatistics, fetchAlumniByYear } from '../../../services/api';

const UsersIndex: React.FC = () => {
  const [batchList, setBatchList] = useState<{ year: number; count: number }[]>([]);
  const [selectedBatch, setSelectedBatch] = useState<number | null>(null);
  const [alumni, setAlumni] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCourse, setSelectedCourse] = useState('All');
  const [selectedUser, setSelectedUser] = useState<any | null>(null);

  useEffect(() => {
    const loadBatches = async () => {
      setLoading(true);
      try {
        const data = await fetchAlumniStatistics();
        setBatchList(data.years || []);
      } catch (e) {
        setBatchList([]);
      } finally {
        setLoading(false);
      }
    };
    loadBatches();
  }, []);

  const handleBatchClick = async (year: number) => {
    setLoading(true);
    setSelectedBatch(year);
    setSearchTerm('');
    setSelectedCourse('All');
    try {
      const data = await fetchAlumniByYear(year.toString());
      setAlumni(data.alumni || []);
    } catch (e) {
      setAlumni([]);
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    setSelectedBatch(null);
    setAlumni([]);
    setSearchTerm('');
    setSelectedCourse('All');
  };

  // Get unique courses for dropdown
  const courseOptions = Array.from(new Set(alumni.map(a => a.course).filter(Boolean)));

  // Filtered alumni
  const filteredAlumni = alumni.filter((user) => {
    const matchCourse = selectedCourse === 'All' || user.course === selectedCourse;
    const matchSearch = (user.name || '').toLowerCase().includes(searchTerm.toLowerCase());
    return matchCourse && matchSearch;
  });

  const calculateAge = (birthDateStr?: string) => {
    if (!birthDateStr) return 'N/A';
    const date = new Date(birthDateStr);
    if (isNaN(date.getTime())) return 'N/A';
    const diff = Date.now() - date.getTime();
    const ageDt = new Date(diff);
    return Math.abs(ageDt.getUTCFullYear() - 1970);
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar />
      <div style={{ flexGrow: 1, padding: '20px 40px 40px', backgroundColor: '#f5f7fa', overflowY: 'auto' }}>
        {/* Header: Only show in batch card view */}
        {!selectedBatch && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '25px' }}>
            <span style={{ fontSize: '24px' }}>👥</span>
            <span style={{ fontWeight: 'bold', fontSize: '18px' }}>Users</span>
          </div>
        )}

        {/* Batch Cards View */}
        {!selectedBatch && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px' }}>
            {batchList.length === 0 && !loading && (
              <div>No alumni batches found.</div>
            )}
            {loading && <div>Loading...</div>}
            {batchList.map((batch) => (
              <div
                key={batch.year}
                onClick={() => handleBatchClick(batch.year)}
                style={{
                  width: '220px',
                  borderRadius: '20px',
                  backgroundColor: 'white',
                  overflow: 'hidden',
                  boxShadow: '0 6px 18px rgba(0, 0, 0, 0.08)',
                  transition: 'transform 0.2s ease',
                  cursor: 'pointer',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                }}
              >
                <div style={{ height: '80px', backgroundColor: '#e3e9f7', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 32, color: '#174f84' }}>
                  <span role="img" aria-label="batch">🎓</span>
                </div>
                <div style={{ backgroundColor: '#174f84', color: 'white', padding: '15px' }}>
                  <strong style={{ fontSize: '15px', display: 'block', marginBottom: '5px' }}>YEAR GRADUATED: {batch.year}</strong>
                  <div style={{ fontSize: '13px' }}>Imported: {batch.count}</div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Alumni Table View */}
        {selectedBatch && (
          <div>
            {/* Header with back button and title */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '24px' }}>
              <button
                onClick={handleBack}
                style={{
                  border: 'none',
                  background: '#174f84',
                  color: 'white',
                  borderRadius: '50%',
                  width: '40px',
                  height: '40px',
                  fontSize: '20px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 2px 8px rgba(23, 79, 132, 0.3)',
                  transition: 'all 0.2s ease',
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.transform = 'scale(1.05)';
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(23, 79, 132, 0.4)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.transform = 'scale(1)';
                  e.currentTarget.style.boxShadow = '0 2px 8px rgba(23, 79, 132, 0.3)';
                }}
              >
                ←
              </button>
              <h2 style={{ margin: 0, fontSize: '24px', fontWeight: '600', color: '#174f84' }}>BATCH {selectedBatch}</h2>
            </div>
            
            {/* Search and filter controls */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
                <input
                  type="text"
                  placeholder="🔍 Search alumni..."
                  value={searchTerm}
                  onChange={e => setSearchTerm(e.target.value)}
                  style={{
                    padding: '12px 20px',
                    borderRadius: '25px',
                    border: '2px solid #e1e5e9',
                    fontSize: '14px',
                    outline: 'none',
                    width: '280px',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                    background: '#fff',
                    transition: 'all 0.2s ease',
                  }}
                  onFocus={(e) => {
                    e.target.style.borderColor = '#174f84';
                    e.target.style.boxShadow = '0 4px 12px rgba(23, 79, 132, 0.15)';
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = '#e1e5e9';
                    e.target.style.boxShadow = '0 2px 8px rgba(0,0,0,0.05)';
                  }}
                />
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <label style={{ 
                    marginRight: '8px', 
                    fontWeight: '500',
                    fontSize: '14px', 
                    color: '#555' 
                  }}>COURSE:</label>
                  <select
                    value={selectedCourse}
                    onChange={e => setSelectedCourse(e.target.value)}
                    style={{
                      padding: '10px 16px',
                      borderRadius: '20px',
                      border: '2px solid #e1e5e9',
                      fontSize: '14px',
                      background: '#fff',
                      color: '#333',
                      fontWeight: '500',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                      cursor: 'pointer',
                      appearance: 'none',
                      outline: 'none',
                      minWidth: '120px',
                    }}
                  >
                    <option value="All">All Courses</option>
                    {courseOptions.map((course) => (
                      <option key={course} value={course}>{course}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
            
            {/* Table with optimized layout */}
            <div style={{ 
              backgroundColor: 'white', 
              borderRadius: '12px', 
              boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
              overflow: 'hidden'
            }}>
              <table style={{ 
                width: '100%', 
                borderCollapse: 'collapse',
                fontSize: '14px'
              }}>
                <thead>
                  <tr style={{ background: '#174f84', color: 'white' }}>
                    <th style={{ padding: '16px 12px', textAlign: 'left', fontWeight: '600' }}>#</th>
                    <th style={{ padding: '16px 12px', textAlign: 'left', fontWeight: '600' }}>Name</th>
                    <th style={{ padding: '16px 12px', textAlign: 'left', fontWeight: '600' }}>ID Number</th>
                    <th style={{ padding: '16px 12px', textAlign: 'left', fontWeight: '600' }}>Course</th>
                    <th style={{ padding: '16px 12px', textAlign: 'left', fontWeight: '600' }}>Batch</th>
                    <th style={{ padding: '16px 12px', textAlign: 'left', fontWeight: '600' }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {loading ? (
                    <tr>
                      <td colSpan={6} style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
                        <div style={{ fontSize: '16px' }}>Loading alumni data...</div>
                      </td>
                    </tr>
                  ) : filteredAlumni.length === 0 ? (
                    <tr>
                      <td colSpan={6} style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
                        <div style={{ fontSize: '16px' }}>No alumni found for this batch.</div>
                      </td>
                    </tr>
                  ) : (
                    filteredAlumni.map((user, index) => (
                      <tr
                        key={user.id}
                        style={{ 
                          textAlign: 'left', 
                          cursor: 'pointer', 
                          transition: 'all 0.2s ease',
                          borderBottom: '1px solid #f0f0f0'
                        }}
                        onClick={() => setSelectedUser(user)}
                        onMouseOver={e => { 
                          e.currentTarget.style.background = '#f8faff'; 
                          e.currentTarget.style.transform = 'translateX(4px)';
                        }}
                        onMouseOut={e => { 
                          e.currentTarget.style.background = ''; 
                          e.currentTarget.style.transform = 'translateX(0)';
                        }}
                      >
                        <td style={{ padding: '16px 12px', fontWeight: '500', color: '#666' }}>
                          {String(index + 1).padStart(2, '0')}
                        </td>
                        <td style={{ padding: '16px 12px', fontWeight: '500' }}>{user.name}</td>
                        <td style={{ padding: '16px 12px', fontFamily: 'monospace', color: '#555' }}>{user.ctu_id}</td>
                        <td style={{ padding: '16px 12px', color: '#174f84', fontWeight: '500' }}>{user.course}</td>
                        <td style={{ padding: '16px 12px', color: '#666' }}>{user.batch}</td>
                        <td style={{ 
                          padding: '16px 12px', 
                          fontWeight: '500',
                          color: user.status === 'Employed' ? '#059669' : 
                                 user.status === 'High Position' ? '#d97706' : 
                                 user.status === 'Absorb' ? '#0891b2' : '#dc2626'
                        }}>
                          {user.status}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Add modal after the table */}
        {selectedUser && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            background: 'rgba(0,0,0,0.7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999,
          }}>
            <div style={{ background: 'white', padding: '40px', borderRadius: '16px', minWidth: '340px', textAlign: 'center' }}>
              <h2 style={{ fontSize: '22px', fontWeight: 'bold', marginBottom: 24 }}>User Profile</h2>
              <div style={{ textAlign: 'left', marginBottom: 18 }}>
                <p><b>Name:</b> {selectedUser.name}</p>
                <p><b>ID Number:</b> {selectedUser.ctu_id}</p>
                <p><b>Course:</b> {selectedUser.course}</p>
                <p><b>Batch:</b> {selectedUser.batch}</p>
                <p><b>Status:</b> {selectedUser.status}</p>
                <p><b>Gender:</b> {selectedUser.gender || 'N/A'}</p>
                <p><b>Birthdate:</b> {selectedUser.birthdate || 'N/A'}</p>
                <p><b>Age:</b> {selectedUser.birthdate ? calculateAge(selectedUser.birthdate) : 'N/A'}</p>
                <p><b>Civil Status:</b> {selectedUser.civilStatus || 'N/A'}</p>
                <p><b>Phone Number:</b> {selectedUser.phone || 'N/A'}</p>
                <p><b>Address:</b> {selectedUser.address || 'N/A'}</p>
                <p><b>Social Media:</b> {selectedUser.socialMedia || 'N/A'}</p>
              </div>
              <button onClick={() => setSelectedUser(null)} style={{ marginTop: '20px', padding: '10px 20px', borderRadius: '8px', background: '#f26c4f', color: 'white', border: 'none', cursor: 'pointer' }}>Close</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UsersIndex;
