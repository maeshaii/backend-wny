import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Sidebar from '../global/sidebar';
import { fetchAlumniByYear, fetchTrackerResponsesByUser } from '../../../services/api';

const AlumniData: React.FC = () => {
  const { year } = useParams<{ year: string }>();
  const navigate = useNavigate();

  const [selectedCourse, setSelectedCourse] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');
  const [alumniList, setAlumniList] = useState<any[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalAlumni, setModalAlumni] = useState<any | null>(null);
  const [trackerAnswers, setTrackerAnswers] = useState<any[]>([]);
  const [trackerQuestions, setTrackerQuestions] = useState<any[]>([]);
  const [trackerAnswersMap, setTrackerAnswersMap] = useState<Record<number, any>>({});

  useEffect(() => {
    const loadAlumni = async () => {
      try {
        if (year) {
          const data = await fetchAlumniByYear(year);
          setAlumniList(data.alumni || []);
          // Fetch tracker answers for all alumni in the list
          const trackerMap: Record<number, any> = {};
          if (data.alumni && data.alumni.length > 0) {
            const qRes = await fetch('http://127.0.0.1:8000/api/tracker/questions/');
            const qData = await qRes.json();
            const trackerQuestions = qData.categories ? qData.categories.flatMap((cat: any) => cat.questions) : [];
            // Helper to get tracker answer by label for a given answers object
            const getTrackerAnswerByLabel = (answers: any, label: string) => {
              if (!trackerQuestions || !answers) return '';
              const q = trackerQuestions.find((q: any) => q.text.toLowerCase().includes(label.toLowerCase()));
              if (!q) return '';
              const ans = answers[q.id];
              if (Array.isArray(ans)) return ans.join(', ');
              return ans || '';
            };
            await Promise.all(data.alumni.map(async (alumni: any) => {
              const userId = alumni.id || alumni.user_id;
              if (userId) {
                const res = await fetchTrackerResponsesByUser(userId);
                if (res.responses && res.responses.length > 0) {
                  trackerMap[userId] = {
                    company: getTrackerAnswerByLabel(res.responses[0].answers, 'company'),
                    position: getTrackerAnswerByLabel(res.responses[0].answers, 'position'),
                    salary: getTrackerAnswerByLabel(res.responses[0].answers, 'salary'),
                  };
                }
              }
            }));
          }
          setTrackerAnswersMap(trackerMap);
        }
      } catch (e) {
        setAlumniList([]);
        setTrackerAnswersMap({});
      }
    };
    loadAlumni();
  }, [year]);

  const filteredAlumni = alumniList.filter((alumni) => {
    const programValue = alumni.program || alumni.Program_Name || alumni.course;
    const matchCourse = selectedCourse === 'All' || programValue === selectedCourse;
    const matchSearch = (alumni.name || '').toLowerCase().includes(searchTerm.toLowerCase());
    return matchCourse && matchSearch;
  });

  const openModal = async (alumni: any) => {
    setModalAlumni(alumni);
    setModalOpen(true);
    // Fetch tracker answers for this alumni
    if (alumni.id || alumni.user_id) {
      const userId = alumni.id || alumni.user_id;
      const res = await fetchTrackerResponsesByUser(userId);
      setTrackerAnswers(res.responses && res.responses.length > 0 ? res.responses[0].answers : {});
    } else {
      setTrackerAnswers([]);
    }
    // Fetch tracker questions for mapping
    const qRes = await fetch('http://127.0.0.1:8000/api/tracker/questions/');
    const qData = await qRes.json();
    setTrackerQuestions(qData.categories ? qData.categories.flatMap((cat: any) => cat.questions) : []);
  };

  const closeModal = () => {
    setModalOpen(false);
    setModalAlumni(null);
  };

  // Helper to get tracker answer by question text
  const getTrackerAnswerByLabel = (label: string) => {
    if (!trackerQuestions || !trackerAnswers) return '';
    // Try to match by question text containing the label (case-insensitive)
    const q = trackerQuestions.find((q: any) => q.text.toLowerCase().includes(label.toLowerCase()));
    if (!q) return '';
    const ans = trackerAnswers[q.id];
    if (Array.isArray(ans)) return ans.join(', ');
    return ans || '';
  };

  return (
    <div style={{ display: 'flex', height: '100vh', fontFamily: 'Arial, sans-serif' }}>
      <Sidebar />

      <div style={{ flex: 1, overflowY: 'auto' }}>
       {/* Header */}
<div
  style={{
    position: 'relative',
    backgroundColor: '#17406a',
    color: 'white',
    padding: '15px 30px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between'
  }}
>
  {/* Back Button */}
  <button
              onClick={() => navigate(-1)}
              style={{
                border: 'none',
      background: 'transparent',
      color: '#ffffff',
      fontSize: 24,
                cursor: 'pointer',
      padding: 4,
              }}
    aria-label="Back"
    title="Back"
            >
    ↶
            </button>

  {/* Centered Title */}
  <h2
    style={{
      position: 'absolute',
      left: '50%',
      transform: 'translateX(-50%)',
      margin: 0,
      color:"white"
    }}
  >
    Alumni Data
  </h2>

  {/* Search Bar */}
  <input
    type="text"
    placeholder="🔍 Search..."
    value={searchTerm}
    onChange={(e) => setSearchTerm(e.target.value)}
    style={{
      padding: '6px 12px',
      borderRadius: '6px',
      border: 'none',
      fontSize: '14px',
      width: '200px',
      zIndex: 2
    }}
  />
</div>


       {/* Batch and Course Filter in the Same Row */}
<div style={{
  padding: '20px 30px 0',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center'
}}>
  {/* Batch Label */}
  <strong style={{ fontSize: '16px' }}>BATCH {year}</strong>

  {/* Course Dropdown */}
  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
    <span style={{ fontSize: '14px' }}>COURSE:</span>
    <select
      value={selectedCourse}
      onChange={(e) => setSelectedCourse(e.target.value)}
      style={{
        padding: '6px 12px',
        borderRadius: '20px',
        backgroundColor: '#4f46e5',
        color: 'white',
        border: 'none',
        fontWeight: 'bold',
        cursor: 'pointer',
        fontSize: '14px'
      }}
    >
      <option value="All">All</option>
      <option value="BSIT">BSIT</option>
      <option value="BSIS">BSIS</option>
      <option value="BSCS">BSCS</option>
    </select>
  </div>
</div>


        {/* Table Section */}
        <div style={{ padding: '30px' }}>
          <table
            style={{
              width: '100%',
              borderCollapse: 'collapse',
              fontSize: '14px'
            }}
          >
            <thead style={{ backgroundColor: '#6a74f0', color: 'white' }}>
              <tr>
                <th style={headerCell}>#</th>
                <th style={headerCell}>Program Name</th>
                <th style={headerCell}>Last Name</th>
                <th style={headerCell}>First Name</th>
                <th style={headerCell}>Status</th>
                <th style={headerCell}>Current Job</th>
                <th style={headerCell}>Current Position</th>
                <th style={headerCell}>Salary Current</th>
              </tr>
            </thead>
            <tbody>
              {filteredAlumni.length === 0 ? (
                <tr>
                  <td colSpan={8} style={{ textAlign: 'center', padding: '20px', color: '#888' }}>
                    No alumni found.
                  </td>
                </tr>
              ) : (
                filteredAlumni.map((alumni, index) => {
                  const userId = alumni.id || alumni.user_id;
                  const tracker = trackerAnswersMap[userId] || {};
                  return (
                    <tr
                      key={alumni.id || index}
                      style={{ borderBottom: '1px solid #eee', cursor: 'pointer' }}
                      onClick={() => openModal(alumni)}
                    >
                      <td style={bodyCell}>{String(index + 1).padStart(2, '0')}</td>
                      <td style={bodyCell}>{typeof (alumni.program || alumni.Program_Name || alumni.course) === 'object' ? JSON.stringify(alumni.program || alumni.Program_Name || alumni.course) : (alumni.program || alumni.Program_Name || alumni.course || '')}</td>
                      <td style={bodyCell}>{typeof (alumni.lastName || alumni.Last_Name || (alumni.name ? alumni.name.split(' ').slice(-1)[0] : '')) === 'object' ? JSON.stringify(alumni.lastName || alumni.Last_Name || (alumni.name ? alumni.name.split(' ').slice(-1)[0] : '')) : (alumni.lastName || alumni.Last_Name || (alumni.name ? alumni.name.split(' ').slice(-1)[0] : '') || '')}</td>
                      <td style={bodyCell}>{typeof (alumni.firstName || alumni.First_Name || (alumni.name ? alumni.name.split(' ')[0] : '')) === 'object' ? JSON.stringify(alumni.firstName || alumni.First_Name || (alumni.name ? alumni.name.split(' ')[0] : '')) : (alumni.firstName || alumni.First_Name || (alumni.name ? alumni.name.split(' ')[0] : '') || '')}</td>
                      <td style={bodyCell}>{typeof (alumni.status || alumni.Status || alumni.user_status) === 'object' ? JSON.stringify(alumni.status || alumni.Status || alumni.user_status) : (alumni.status || alumni.Status || alumni.user_status || '')}</td>
                      <td style={bodyCell}>{typeof (alumni.company_name_current || alumni['Company name current'] || alumni.company || tracker.company) === 'object' ? JSON.stringify(alumni.company_name_current || alumni['Company name current'] || alumni.company || tracker.company) : (alumni.company_name_current || alumni['Company name current'] || alumni.company || tracker.company || '')}</td>
                      <td style={bodyCell}>{typeof (alumni.position_current || alumni['Position current'] || tracker.position) === 'object' ? JSON.stringify(alumni.position_current || alumni['Position current'] || tracker.position) : (alumni.position_current || alumni['Position current'] || tracker.position || '')}</td>
                      <td style={bodyCell}>{typeof (alumni.salary_current || alumni['Salary current'] || tracker.salary) === 'object' ? JSON.stringify(alumni.salary_current || alumni['Salary current'] || tracker.salary) : (alumni.salary_current || alumni['Salary current'] || tracker.salary || '')}</td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
        {/* Modal for full details */}
        {modalOpen && modalAlumni && (
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
            <div style={{ 
              background: 'white', 
              padding: '32px', 
              borderRadius: '20px', 
              width: '90%',
              maxWidth: '900px',
              maxHeight: '95vh',
              boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
              position: 'relative',
              overflow: 'hidden'
            }}>
              {/* Close button */}
              <button 
                onClick={closeModal} 
                style={{ 
                  position: 'absolute',
                  top: '16px',
                  right: '20px',
                  background: 'none',
                  border: 'none',
                  fontSize: '24px',
                  cursor: 'pointer',
                  color: '#999',
                  width: '32px',
                  height: '32px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  borderRadius: '50%',
                  transition: 'all 0.2s ease'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.background = '#f0f0f0';
                  e.currentTarget.style.color = '#666';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.background = 'none';
                  e.currentTarget.style.color = '#999';
                }}
              >
                ×
              </button>
              
              {/* Header */}
              <div style={{ textAlign: 'center', marginBottom: '24px', paddingRight: '40px' }}>
                <h2 style={{ 
                  fontSize: '28px', 
                  fontWeight: '700', 
                  margin: '0 0 8px 0',
                  color: '#174f84'
                }}>
                  Alumni Details
                </h2>
                <div style={{ 
                  width: '60px', 
                  height: '4px', 
                  background: '#174f84', 
                  borderRadius: '2px',
                  margin: '0 auto'
                }}></div>
              </div>
              
              {/* Profile content in grid layout */}
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                gap: '20px',
                maxHeight: 'calc(95vh - 120px)',
                overflowY: 'auto',
                paddingRight: '8px'
              }}>
                {/* Personal Information */}
                <div style={{ background: '#f8faff', padding: '20px', borderRadius: '12px', border: '1px solid #e1e5e9' }}>
                  <h3 style={{ 
                    fontSize: '18px', 
                    fontWeight: '600', 
                    margin: '0 0 16px 0',
                    color: '#174f84',
                    borderBottom: '2px solid #174f84',
                    paddingBottom: '8px'
                  }}>
                    Personal Information
                  </h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {[
                      ['CTU ID', modalAlumni.ctu_id || modalAlumni.CTU_ID || getTrackerAnswerByLabel('ctu id')],
                      ['First Name', modalAlumni.firstName || modalAlumni.First_Name || modalAlumni.first_name || (modalAlumni.name ? modalAlumni.name.split(' ')[0] : '') || getTrackerAnswerByLabel('first name')],
                      ['Middle Name', modalAlumni.middleName || modalAlumni.Middle_Name || modalAlumni.middle_name || (modalAlumni.name && modalAlumni.name.split(' ').length > 2 ? modalAlumni.name.split(' ').slice(1, -1).join(' ') : '') || getTrackerAnswerByLabel('middle name')],
                      ['Last Name', modalAlumni.lastName || modalAlumni.Last_Name || modalAlumni.last_name || (modalAlumni.name ? modalAlumni.name.split(' ').slice(-1)[0] : '') || getTrackerAnswerByLabel('last name')],
                      ['Gender', modalAlumni.gender || modalAlumni.Gender || getTrackerAnswerByLabel('gender')],
                      ['Birthdate', modalAlumni.birthdate || modalAlumni.Birthdate || modalAlumni.birth_date || getTrackerAnswerByLabel('birthdate')],
                      ['Age', modalAlumni.age || modalAlumni.Age || getTrackerAnswerByLabel('age')],
                      ['Civil Status', modalAlumni.civil_status || modalAlumni.Civil_Status || getTrackerAnswerByLabel('civil status')],
                    ].map(([label, value]) => (
                      <div key={label} style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span style={{ fontWeight: '500', color: '#555' }}>{label}:</span>
                        <span style={{ fontWeight: '600', color: '#333', maxWidth: '150px', textAlign: 'right' }}>
                          {value === undefined || value === null || value === '' ? 'No answer' : (typeof value === 'object' ? JSON.stringify(value) : value)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
                
                {/* Contact Information */}
                <div style={{ background: '#f8faff', padding: '20px', borderRadius: '12px', border: '1px solid #e1e5e9' }}>
                  <h3 style={{ 
                    fontSize: '18px', 
                    fontWeight: '600', 
                    margin: '0 0 16px 0',
                    color: '#174f84',
                    borderBottom: '2px solid #174f84',
                    paddingBottom: '8px'
                  }}>
                    Contact Information
                  </h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {[
                      ['Phone Number', modalAlumni.phone_num || modalAlumni.Phone_Number || modalAlumni.phone || getTrackerAnswerByLabel('phone')],
                      ['Address', modalAlumni.address || modalAlumni.Address || getTrackerAnswerByLabel('address')],
                      ['Social Media', modalAlumni.social_media || modalAlumni.Social_Media || getTrackerAnswerByLabel('social')],
                      ['Email', modalAlumni.email || modalAlumni.Email || getTrackerAnswerByLabel('email')],
                    ].map(([label, value]) => (
                      <div key={label} style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span style={{ fontWeight: '500', color: '#555' }}>{label}:</span>
                        <span style={{ fontWeight: '600', color: '#333', maxWidth: '150px', textAlign: 'right' }}>
                          {value === undefined || value === null || value === '' ? 'No answer' : (typeof value === 'object' ? JSON.stringify(value) : value)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
                
                {/* Academic Information */}
                <div style={{ background: '#f8faff', padding: '20px', borderRadius: '12px', border: '1px solid #e1e5e9' }}>
                  <h3 style={{ 
                    fontSize: '18px', 
                    fontWeight: '600', 
                    margin: '0 0 16px 0',
                    color: '#174f84',
                    borderBottom: '2px solid #174f84',
                    paddingBottom: '8px'
                  }}>
                    Academic Information
                  </h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {[
                      ['Program Name', modalAlumni.program || modalAlumni.Program_Name || modalAlumni.course || getTrackerAnswerByLabel('program')],
                      ['Status', modalAlumni.status || modalAlumni.Status || modalAlumni.user_status || getTrackerAnswerByLabel('status')],
                    ].map(([label, value]) => (
                      <div key={label} style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span style={{ fontWeight: '500', color: '#555' }}>{label}:</span>
                        <span style={{ fontWeight: '600', color: '#174f84' }}>
                          {value === undefined || value === null || value === '' ? 'No answer' : (typeof value === 'object' ? JSON.stringify(value) : value)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
                
                {/* Employment Information */}
                <div style={{ background: '#f8faff', padding: '20px', borderRadius: '12px', border: '1px solid #e1e5e9' }}>
                  <h3 style={{ 
                    fontSize: '18px', 
                    fontWeight: '600', 
                    margin: '0 0 16px 0',
                    color: '#174f84',
                    borderBottom: '2px solid #174f84',
                    paddingBottom: '8px'
                  }}>
                    Employment Information
                  </h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {[
                      ['Company Name', modalAlumni.company_name_current || modalAlumni['Company name current'] || modalAlumni.company || getTrackerAnswerByLabel('company') || getTrackerAnswerByLabel('employer') || getTrackerAnswerByLabel('current company')],
                      ['Position', modalAlumni.position_current || modalAlumni['Position current'] || getTrackerAnswerByLabel('position')],
                      ['Sector', modalAlumni.sector_current || modalAlumni['Sector current'] || getTrackerAnswerByLabel('sector')],
                      ['Duration', modalAlumni.employment_duration_current || modalAlumni['Employment duration current'] || modalAlumni.employment_duration || getTrackerAnswerByLabel('employment duration') || getTrackerAnswerByLabel('how long') || getTrackerAnswerByLabel('duration')],
                      ['Salary', modalAlumni.salary_current || modalAlumni['Salary current'] || getTrackerAnswerByLabel('salary')],
                    ].map(([label, value]) => (
                      <div key={label} style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span style={{ fontWeight: '500', color: '#555' }}>{label}:</span>
                        <span style={{ fontWeight: '600', color: '#333', maxWidth: '150px', textAlign: 'right' }}>
                          {value === undefined || value === null || value === '' ? 'No answer' : (typeof value === 'object' ? JSON.stringify(value) : value)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
                
                {/* Additional Information */}
                <div style={{ background: '#f8faff', padding: '20px', borderRadius: '12px', border: '1px solid #e1e5e9' }}>
                  <h3 style={{ 
                    fontSize: '18px', 
                    fontWeight: '600', 
                    margin: '0 0 16px 0',
                    color: '#174f84',
                    borderBottom: '2px solid #174f84',
                    paddingBottom: '8px'
                  }}>
                    Additional Information
                  </h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {[
                      ['Supporting Document', modalAlumni.supporting_document_current || modalAlumni['Supporting document current'] || getTrackerAnswerByLabel('supporting document')],
                      ['Awards/Recognition', modalAlumni.awards_recognition_current || modalAlumni['Awards recognition current'] || getTrackerAnswerByLabel('awards')],
                      ['Unemployment Reason', modalAlumni.unemployment_reason || modalAlumni['Unemployment reason'] || getTrackerAnswerByLabel('unemployment')],
                      ['Further Study', modalAlumni.pursue_further_study || modalAlumni['Pursue further study'] || getTrackerAnswerByLabel('further study')],
                      ['Date Started', modalAlumni.date_started || modalAlumni['Date started'] || getTrackerAnswerByLabel('date started')],
                      ['School/Institution', modalAlumni.school_name || modalAlumni['School name'] || modalAlumni.institution || modalAlumni.university || getTrackerAnswerByLabel('school') || getTrackerAnswerByLabel('institution') || getTrackerAnswerByLabel('university')],
                    ].map(([label, value]) => (
                      <div key={label} style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span style={{ fontWeight: '500', color: '#555' }}>{label}:</span>
                        <span style={{ fontWeight: '600', color: '#333', maxWidth: '150px', textAlign: 'right' }}>
                          {value === undefined || value === null || value === '' ? 'No answer' : (typeof value === 'object' ? JSON.stringify(value) : value)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const headerCell: React.CSSProperties = {
  padding: '10px',
  textAlign: 'left',
  fontWeight: 'bold'
};

const bodyCell: React.CSSProperties = {
  padding: '10px',
  textAlign: 'left'
};

export default AlumniData;
