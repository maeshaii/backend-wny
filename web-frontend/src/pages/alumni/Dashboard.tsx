import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface AlumniUser {
  name: string;
  course?: string;
  year_graduated?: string | number;
  profile_pic?: string;
}

const AlumniDashboard: React.FC = () => {
  const [user, setUser] = useState<AlumniUser | null>(null);
  const [showProfile, setShowProfile] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch user info from localStorage
    const userStr = localStorage.getItem('user');
    if (userStr) {
      setUser(JSON.parse(userStr));
    } else {
      // Not logged in, redirect to login
      navigate('/login');
    }
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
    navigate('/login');
  };

  return (
    <div style={{ background: '#f5f7fa', minHeight: '100vh', fontFamily: 'Arial, sans-serif' }}>
      {/* Top Bar */}
      <div style={{ background: '#174f84', padding: '16px 32px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <img src="/logo192.png" alt="WhereNaYou Logo" style={{ width: 48, height: 48, borderRadius: '50%' }} />
          <input type="text" placeholder="Search..." style={{ borderRadius: 20, border: 'none', padding: '8px 16px', width: 200 }} />
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 32 }}>
          <span style={{ color: 'white', fontSize: 20, cursor: 'pointer' }}>Home</span>
          <span style={{ color: 'white', fontSize: 20, cursor: 'pointer' }}>Messages</span>
          <span style={{ color: 'white', fontSize: 20, cursor: 'pointer' }}>Notification</span>
          <div style={{ position: 'relative' }}>
            <span style={{ color: 'white', fontSize: 20, cursor: 'pointer' }} onClick={() => setShowProfile((v) => !v)}>
              Profile ▼
            </span>
            {showProfile && (
              <div style={{ position: 'absolute', right: 0, top: 32, background: 'white', color: '#174f84', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.15)', minWidth: 120, zIndex: 10 }}>
                <div style={{ padding: 12, cursor: 'pointer' }} onClick={handleLogout}>Logout</div>
                <div style={{ padding: 12, cursor: 'pointer' }} onClick={() => setShowProfile(false)}>Close</div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div style={{ maxWidth: 1200, margin: '32px auto', display: 'flex', gap: 24 }}>
        {/* Left Sidebar */}
        <div style={{ flex: 1, maxWidth: 260, display: 'flex', flexDirection: 'column', gap: 24 }}>
          {/* Profile Card */}
          <div style={{ background: 'white', borderRadius: 16, padding: 24, boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
              <img src={user?.profile_pic || 'https://randomuser.me/api/portraits/women/44.jpg'} alt="Profile" style={{ width: 56, height: 56, borderRadius: '50%' }} />
              <div>
                <div style={{ fontWeight: 'bold', fontSize: 18 }}>{user?.name || 'Alumni User'}</div>
                <div style={{ color: '#888', fontSize: 14 }}>{user?.course || 'Bachelor of Science in IT'}</div>
                {user?.year_graduated && <div style={{ color: '#888', fontSize: 13 }}>Batch {user.year_graduated}</div>}
              </div>
            </div>
            <button style={{ marginTop: 16, background: '#f5f7fa', border: '1px solid #174f84', color: '#174f84', borderRadius: 8, padding: '6px 16px', cursor: 'pointer' }}>Edit Profile</button>
          </div>

          {/* Introduction */}
          <div style={{ background: 'white', borderRadius: 16, padding: 20, boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
            <div style={{ fontWeight: 'bold', marginBottom: 8 }}>Introduction</div>
            <button style={{ background: '#e0e7ef', border: 'none', borderRadius: 8, padding: '6px 12px', marginBottom: 8, cursor: 'pointer' }}>Add Bio</button>
            <button style={{ background: '#e0e7ef', border: 'none', borderRadius: 8, padding: '6px 12px', cursor: 'pointer' }}>Add Resume</button>
          </div>

          {/* Followers */}
          <div style={{ background: 'white', borderRadius: 16, padding: 20, boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
            <div style={{ fontWeight: 'bold', marginBottom: 8 }}>Followers</div>
            <div style={{ display: 'flex', gap: 8 }}>
              {[1,2,3,4].map((f) => (
                <div key={f} style={{ textAlign: 'center' }}>
                  <div style={{ width: 40, height: 40, background: '#e0e7ef', borderRadius: '50%', marginBottom: 4 }}></div>
                  <div style={{ fontSize: 12, color: '#888' }}>Lorem</div>
                </div>
              ))}
            </div>
            <div style={{ color: '#174f84', fontSize: 12, marginTop: 8, cursor: 'pointer' }}>See all</div>
          </div>
        </div>

        {/* Center Content */}
        <div style={{ flex: 2, display: 'flex', flexDirection: 'column', gap: 24 }}>
          {/* Banner */}
          <div style={{ background: '#f87171', height: 80, borderRadius: 16 }}></div>

          {/* Post Input */}
          <div style={{ background: 'white', borderRadius: 16, padding: 20, boxShadow: '0 2px 8px rgba(0,0,0,0.05)', marginTop: -40, zIndex: 1, position: 'relative' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <img src={user?.profile_pic || 'https://randomuser.me/api/portraits/women/44.jpg'} alt="Profile" style={{ width: 40, height: 40, borderRadius: '50%' }} />
              <input type="text" placeholder="Start a post" style={{ flex: 1, borderRadius: 20, border: '1px solid #eee', padding: '10px 16px' }} />
              <button style={{ background: '#174f84', color: 'white', border: 'none', borderRadius: 8, padding: '8px 20px', cursor: 'pointer' }}>Post</button>
            </div>
          </div>

          {/* Post Feed */}
          <div style={{ background: 'white', borderRadius: 16, padding: 20, boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
              <img src={user?.profile_pic || 'https://randomuser.me/api/portraits/women/44.jpg'} alt="Profile" style={{ width: 32, height: 32, borderRadius: '50%' }} />
              <div style={{ fontWeight: 'bold' }}>{user?.name || 'Alumni User'}</div>
            </div>
            <div style={{ fontSize: 14, color: '#333', marginBottom: 12 }}>
              Lorem ipsum dolor sit amet. Quo pariatur enim et veniam repudiandae eum quisquam voluptatem incidunt vitae aut amet. Quo pariatur enim et veniam repudiandae eum quisquam voluptatem incidunt vitae aut amet.
            </div>
            <div style={{ display: 'flex', gap: 16, fontSize: 13, color: '#888' }}>
              <span style={{ cursor: 'pointer' }}>Like</span>
              <span style={{ cursor: 'pointer' }}>Comment</span>
              <span style={{ cursor: 'pointer' }}>Report</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AlumniDashboard; 