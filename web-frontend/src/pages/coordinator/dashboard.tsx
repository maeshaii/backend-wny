import React, { useState, useEffect } from 'react';
import Statistics from './statistics';
import DetailsTable from './detailstable'; // ✅ Your new table component
import { fetchAlumniStatistics } from '../../services/api';

export default function Dashboard() {
  const [showModal, setShowModal] = useState(false);
  const [showStats, setShowStats] = useState(false);
  const [selectedCard, setSelectedCard] = useState<number | null>(null);
  const [selectedFile, setSelectedFile] = useState('');
  const [alumniYears, setAlumniYears] = useState<{ year: number; count: number }[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadAlumniData = async () => {
      try {
        const data = await fetchAlumniStatistics();
        setAlumniYears(data.years || []);
      } catch (error) {
        console.error('Error loading alumni data:', error);
        setAlumniYears([]);
      } finally {
        setLoading(false);
      }
    };

    loadAlumniData();
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0].name);
    } else {
      setSelectedFile('');
    }
  };

  // Inline styles
  const styles = {
    container: {
      display: 'flex',
      height: '100vh',
      fontFamily: 'Arial, sans-serif',
    },
    sidebar: {
      width: '180px',
      backgroundColor: '#164B87',
      color: 'white',
      display: 'flex',
      flexDirection: 'column' as const,
      justifyContent: 'space-between',
    },
    logo: {
      margin: '20px 0',
      textAlign: 'center' as const,
      fontWeight: 'bold',
    },
    nav: {
      flex: 1,
    },
    navItem: {
      padding: '12px 20px',
      cursor: 'pointer',
    },
    navItemActive: {
      padding: '12px 20px',
      cursor: 'pointer',
      backgroundColor: '#4B6EAF',
    },
    logout: {
      background: 'none',
      border: 'none',
      color: 'white',
      margin: '20px',
      cursor: 'pointer',
    },
    main: {
      flex: 1,
      padding: '30px 50px',
      background: 'white',
    },
    header: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
    },
    actions: {
      display: 'flex',
    },
    btn: {
      marginLeft: '10px',
      padding: '6px 16px',
      borderRadius: '9999px',
      border: 'none',
      cursor: 'pointer',
    },
    statsBtn: {
      marginLeft: '10px',
      padding: '6px 16px',
      borderRadius: '9999px',
      border: 'none',
      cursor: 'pointer',
      backgroundColor: '#164B87',
      color: 'white',
    },
    importBtn: {
      marginLeft: '10px',
      padding: '6px 16px',
      borderRadius: '9999px',
      border: 'none',
      cursor: 'pointer',
      backgroundColor: '#5A6DFE',
      color: 'white',
    },
    filter: {
      display: 'inline-block',
      backgroundColor: '#5A6DFE',
      color: 'white',
      border: 'none',
      borderRadius: '9999px',
      padding: '4px 12px',
      margin: '20px 0',
      cursor: 'pointer',
    },
    cards: {
      display: 'flex',
      gap: '30px',
      flexWrap: 'wrap' as const,
    },
    card: {
      backgroundColor: '#5A6DFE',
      borderRadius: '20px',
      padding: '20px',
      width: '200px',
      color: 'white',
      textAlign: 'left' as const,
      cursor: 'pointer',
    },
    cardImage: {
      backgroundColor: 'white',
      height: '100px',
      borderRadius: '0',
      marginBottom: '12px',
    },
    cardText: {
      fontSize: '12px',
      margin: '0',
    },
    modalOverlay: {
      position: 'fixed' as const,
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      background: 'rgba(0, 0, 0, 0.4)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      zIndex: 10,
    },
    modal: {
      background: '#a2d5db',
      borderRadius: '30px',
      padding: '30px 40px',
      width: '400px',
      maxWidth: '90%',
      textAlign: 'center' as const,
    },
    modalH2: {
      marginBottom: '20px',
      fontSize: '20px',
    },
    modalLabel: {
      display: 'block',
      textAlign: 'left' as const,
      margin: '10px 0 5px',
      fontWeight: '500',
    },
    modalInput: {
      width: '90%',
      maxWidth: '300px',
      padding: '12px 20px',
      border: 'none',
      borderRadius: '30px',
      margin: '0 auto 20px',
      display: 'block',
    },
    fileLabel: {
      width: '90%',
      maxWidth: '300px',
      display: 'block',
      margin: '0 auto 20px',
      padding: '12px 20px',
      background: 'white',
      borderRadius: '30px',
      cursor: 'pointer',
      textAlign: 'left' as const,
    },
    fileInput: {
      display: 'none',
    },
    modalActions: {
      display: 'flex',
      justifyContent: 'space-between',
      marginTop: '10px',
    },
    addBtn: {
      background: '#e76f51',
      color: 'white',
      border: 'none',
      borderRadius: '10px',
      padding: '10px 30px',
      cursor: 'pointer',
    },
    cancelBtn: {
      background: '#ddd',
      border: '1px solid #333',
      borderRadius: '10px',
      padding: '10px 30px',
      cursor: 'pointer',
    },
  };

  return (
    <div style={styles.container}>
      {/* ===================== Sidebar ===================== */}
      <aside style={styles.sidebar}>
        <div style={styles.logo}>WhereNaYou</div>
        <nav style={styles.nav}>
          <ul>
            <li style={styles.navItem}>🏠 Dashboard</li>
            <li style={styles.navItemActive}>📄 Imports</li>
          </ul>
        </nav>
        <button style={styles.logout}>🔒 Logout</button>
      </aside>

      {/* ===================== Main Content ===================== */}
      <main style={styles.main}>
        <div style={styles.header}>
          <h1>Imports</h1>
          <div style={styles.actions}>
            <button
              style={styles.statsBtn}
              onClick={() => setShowStats(!showStats)}
            >
              {showStats ? 'Hide Statistics' : 'View Statistics'}
            </button>
            <button
              style={styles.importBtn}
              onClick={() => setShowModal(true)}
            >
              Import OJT
            </button>
          </div>
        </div>

        <button style={styles.filter}>BSIT</button>

        {/* ============== Cards OR Details Table OR Statistics ============== */}
        {!showStats ? (
          selectedCard ? (
            <DetailsTable onBack={() => setSelectedCard(null)} selectedYear={selectedCard} />
          ) : (
            <div style={styles.cards}>
              {loading ? (
                <div style={{ width: '100%', textAlign: 'center', padding: '20px' }}>
                  Loading alumni data...
                </div>
              ) : alumniYears.length === 0 ? (
                <div style={{ width: '100%', textAlign: 'center', padding: '20px' }}>
                  No alumni data found.
                </div>
              ) : (
                alumniYears.map((yearData) => (
                  <div
                    key={yearData.year}
                    style={styles.card}
                    onClick={() => setSelectedCard(yearData.year)}
                  >
                    <div style={styles.cardImage}></div>
                    <p style={styles.cardText}>YEAR GRADUATED: {yearData.year}</p>
                    <p style={styles.cardText}>Imported: {yearData.count}</p>
                  </div>
                ))
              )}
            </div>
          )
        ) : (
          <Statistics />
        )}
      </main>

      {/* ===================== Modal ===================== */}
      {showModal && (
        <div style={styles.modalOverlay}>
          <div style={styles.modal}>
            <h2 style={styles.modalH2}>Import OJT Data</h2>

            <label style={styles.modalLabel}>Batch Graduated</label>
            <input type="text" placeholder="Enter batch..." style={styles.modalInput} />

            <label style={styles.modalLabel}>Upload File</label>
            <label style={styles.fileLabel}>
              {selectedFile || 'Choose File'}
              <input type="file" onChange={handleFileChange} style={styles.fileInput} />
            </label>

            <div style={styles.modalActions}>
              <button style={styles.addBtn}>Add</button>
              <button
                style={styles.cancelBtn}
                onClick={() => setShowModal(false)}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
