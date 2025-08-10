import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import AlumniTopBar from './AlumniTopBar';
import ctulogo from '../../images/ctulogo.png';


interface AlumniUser {
  name: string;
  course?: string;
  year_graduated?: string | number;
  profile_pic?: string;
  location?: string;
  university?: string;
  bio?: string;
  resume?: string;
}

const AlumniProfile: React.FC = () => {
  const [user, setUser] = useState<AlumniUser | null>(null);
  const [showProfile, setShowProfile] = useState(false);
  const navigate = useNavigate();
  const { id } = useParams();
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [editProfilePic, setEditProfilePic] = useState<string | undefined>(user?.profile_pic);
  const [editBio, setEditBio] = useState<string>(user?.bio || '');
  // Remove all state and handlers related to resume (editResume, resumeFile, handleResumeChange, handleRemoveResume)
  // Remove the Resume section from the modal UI
  // Leave a comment where the resume section would go for future implementation
  const [profilePicFile, setProfilePicFile] = useState<File | null>(null);

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
    navigate('/login');
  };

  useEffect(() => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      const userObj = JSON.parse(userStr);
      setUser(userObj);
    } else {
      navigate('/login');
    }
  }, [navigate, id]);

  const handleEditProfile = () => {
    setEditProfilePic(user?.profile_pic);
    setEditBio(user?.bio || '');
    // setEditResume(user?.resume); // This line is removed
    setEditModalOpen(true);
  };

  const handleProfilePicChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    console.log('Selected file:', file);
    if (file) {
      setProfilePicFile(file);
      const reader = new FileReader();
      reader.onload = (ev) => setEditProfilePic(ev.target?.result as string);
      reader.readAsDataURL(file);
    }
  };

  // const handleResumeChange = (e: React.ChangeEvent<HTMLInputElement>) => { // This function is removed
  //   const file = e.target.files?.[0];
  //   if (file && file.type === 'application/pdf') {
  //     setResumeFile(file);
  //     const reader = new FileReader();
  //     reader.onload = (ev) => setEditResume(ev.target?.result as string);
  //     reader.readAsDataURL(file);
  //   }
  // };

  const handleRemoveProfilePic = () => {
    setEditProfilePic(undefined);
    setProfilePicFile(null);
  };

  // const handleRemoveResume = () => { // This function is removed
  //   setEditResume(undefined);
  //   setResumeFile(null);
  // };

  const handleSave = async () => {
    const formData = new FormData();
    if (profilePicFile) {
      formData.append('profile_pic', profilePicFile);
    }
    formData.append('bio', editBio);

    const userObj = JSON.parse(localStorage.getItem('user') || '{}');
    const userId = userObj.user_id || userObj.id;
    if (!userId) {
      alert('User ID not found. Please log in again.');
      return;
    }

    const url = `http://127.0.0.1:8000/api/shared/profile/update/?user_id=${userId}`;
    console.log('Sending PUT to:', url);
    try {
      const response = await fetch(url, {
        method: 'PUT',
        body: formData,
      });
      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
        localStorage.setItem('user', JSON.stringify(data.user));
        setEditModalOpen(false);
        window.location.reload();
      } else {
        const err = await response.json();
        alert('Failed to update profile: ' + (err.message || 'Unknown error'));
      }
    } catch (error) {
      alert('Network error: ' + error);
    }
  };

  return (
    <div style={{ background: '#f5f7fa', minHeight: '100vh', fontFamily: 'Arial, sans-serif' }}>
      <AlumniTopBar 
        showProfile={showProfile} 
        setShowProfile={setShowProfile} 
        handleLogout={handleLogout} 
      />

      {/* Main Content */}
      <div style={{ maxWidth: 1200, margin: '0 auto', display: 'flex', gap: 24, padding: '24px' }}>
        {/* Left Sidebar */}
        <div style={{ flex: 1, maxWidth: 280 }}>
          {/* Introduction */}
          <div style={{ 
            background: 'white', 
            borderRadius: 12, 
            padding: 20, 
            boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
            border: '1px solid #e0e0e0',
            marginBottom: 16
          }}>
            <div style={{ fontWeight: 'bold', marginBottom: 16, fontSize: 16 }}>Introduction</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              <button style={{ 
                background: 'white', 
                border: '1px solid #e0e0e0', 
                borderRadius: 8, 
                padding: '8px 16px', 
                cursor: 'pointer',
                fontSize: 14
              }}>
                Add Bio
              </button>
              <button style={{ 
                background: 'white', 
                border: '1px solid #e0e0e0', 
                borderRadius: 8, 
                padding: '8px 16px', 
                cursor: 'pointer',
                fontSize: 14
              }}>
                Add Resume
              </button>
            </div>
          </div>

          {/* Followers */}
          <div style={{ 
            background: 'white', 
            borderRadius: 12, 
            padding: 20, 
            boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
            border: '1px solid #e0e0e0'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <div style={{ fontWeight: 'bold', fontSize: 16 }}>Followers</div>
              <div style={{ color: '#174f84', fontSize: 12, cursor: 'pointer' }}>See all</div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {/* First Row */}
              <div style={{ display: 'flex', gap: 8 }}>
                {[1, 2, 3].map((f) => (
                  <div key={f} style={{ textAlign: 'center', flex: 1 }}>
                    <img
                      src={`https://randomuser.me/api/portraits/men/${f * 5}.jpg`}
                      alt="Follower"
                      style={{
                        width: 40,
                        height: 40,
                        borderRadius: '50%',
                        objectFit: 'cover',
                        marginBottom: 4
                      }}
                    />
                    <div style={{ fontSize: 12, color: '#666' }}>lorem</div>
                  </div>
                ))}
              </div>
              {/* Second Row */}
              <div style={{ display: 'flex', gap: 8 }}>
                {[4, 5, 6].map((f) => (
                  <div key={f} style={{ textAlign: 'center', flex: 1 }}>
                    <img
                      src={`https://randomuser.me/api/portraits/women/${f * 4}.jpg`}
                      alt="Follower"
                      style={{
                        width: 40,
                        height: 40,
                        borderRadius: '50%',
                        objectFit: 'cover',
                        marginBottom: 4
                      }}
                    />
                    <div style={{ fontSize: 12, color: '#666' }}>lorem</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

        </div>

        {/* Center Content */}
        <div style={{ flex: 2 }}>
          {/* Orange Banner */}
          <div style={{ 
            background: '#ff6b35', 
            height: 160, 
            width: '100%',
            borderRadius: 12,
            position: 'relative',
            marginBottom: 60
          }}>
            {/* Edit Profile Button */}
            <div style={{ position: 'absolute', top: 16, right: 16, display: 'flex', alignItems: 'center', gap: 4, fontSize: 12, color: 'white', cursor: 'pointer', background: 'rgba(0,0,0,0.2)', padding: '6px 12px', borderRadius: 6 }} onClick={handleEditProfile}>
              <span>Edit Profile</span>
              <span>✏️</span>
            </div>
          </div>

          {/* Profile Info Section */}
          <div style={{ 
            position: 'relative',
            marginTop: -80,
            marginBottom: 24
          }}>
            <div style={{ 
              background: 'white', 
              borderRadius: 12, 
              padding: '60px 20px 20px 20px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
              border: '1px solid #e0e0e0',
              textAlign: 'center'
            }}>
              <img 
                src={user?.profile_pic || ctulogo} 
                alt="Profile" 
                style={{ 
                  width: 80, 
                  height: 80, 
                  borderRadius: '50%', 
                  border: '3px solid white',
                  marginBottom: 12,
                  marginTop: -60
                }} 
              />
              <div style={{ fontWeight: 'bold', fontSize: 18, color: '#333', marginBottom: 4, textTransform: 'uppercase' }}>
                {user?.name || 'JEFFREY BATUCAN'}
              </div>
              <div style={{ fontSize: 14, color: '#666' }}>
                {user?.university || 'Cebu Technological University'}
              </div>
            </div>
          </div>

          {/* Start a Post */}
          <div style={{ 
            background: 'white', 
            borderRadius: 12, 
            padding: 20, 
            boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
            border: '1px solid #e0e0e0',
            marginBottom: 16
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <img 
                src={user?.profile_pic || ctulogo} 
                alt="Profile" 
                style={{ width: 40, height: 40, borderRadius: '50%' }} 
              />
              <input 
                type="text" 
                placeholder="Start a post" 
                style={{ 
                  flex: 1, 
                  borderRadius: 20, 
                  border: '1px solid #e0e0e0', 
                  padding: '10px 16px',
                  fontSize: 14
                }} 
              />
            </div>
          </div>

          {/* Social Media Post */}
          <div style={{ 
            background: 'white', 
            borderRadius: 12, 
            padding: 20, 
            boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
            border: '1px solid #e0e0e0'
          }}>
            {/* Post Header */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
              <img 
                src={user?.profile_pic || ctulogo} 
                alt="Profile" 
                style={{ width: 40, height: 40, borderRadius: '50%' }} 
              />
              <div>
                <div style={{ fontWeight: 'bold', fontSize: 14, color: '#333', textTransform: 'uppercase' }}>
                  {user?.name || 'LYKA BAUTISTA'}
                </div>
                <div style={{ fontSize: 12, color: '#666', display: 'flex', alignItems: 'center', gap: 4 }}>
                  <span>3,000,000 Followers</span>
                  <span>•</span>
                  <span>2 d</span>
                  <span>🌐</span>
                </div>
              </div>
            </div>

            {/* Post Content */}
            <div style={{ fontSize: 14, color: '#333', marginBottom: 16, lineHeight: 1.5 }}>
              Lorem ipsum dolor sit amet. Quo asperiores enim ut veniam repudiandae eum quisquam voluptatem non dolore veritatis eos quia suscipit sed facere alias nam voluptate quia. Ut neque ipsam sed explicabo nemo ut sapiente consectetur qui omnis ducimus qui voluptatem iusto? Id enim quia quo quam consequatur sit nulla delectus aut accusamus velit est animi sint eos consequatur nemo sit facilis ipsam. Est dolores tenetur in dignissimos velit At rerum minus qui velit autern qui officia sint!
            </div>

            {/* Post Actions */}
            <div style={{ display: 'flex', gap: 24, fontSize: 13, color: '#666' }}>
              <span style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4 }}>
                ❤️ Like
              </span>
              <span style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4 }}>
                💬 Comment
              </span>
              <span style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4 }}>
                🔄 Repost
              </span>
            </div>
          </div>
        </div>

        
      </div>

      {/* Edit Profile Modal */}
      {editModalOpen && (
        <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: 'rgba(0,0,0,0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: '#fff', borderRadius: 12, boxShadow: '0 2px 16px rgba(0,0,0,0.18)', padding: 32, minWidth: 340, maxWidth: 480, width: '90%', position: 'relative' }}>
            <button onClick={() => setEditModalOpen(false)} style={{ position: 'absolute', top: 16, right: 16, background: 'none', border: 'none', fontSize: 22, cursor: 'pointer', color: '#888' }} title="Close">×</button>
            <h2 style={{ marginBottom: 16 }}>Edit Profile</h2>
            {/* Profile Pic */}
            <div style={{ marginBottom: 16 }}>
              <label style={{ fontWeight: 600 }}>Profile Picture</label><br />
              <img src={editProfilePic || ctulogo} alt="Profile Preview" style={{ width: 80, height: 80, borderRadius: '50%', border: '2px solid #eee', margin: '8px 0' }} />
              <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                <input type="file" accept="image/*" onChange={handleProfilePicChange} />
                <button onClick={handleRemoveProfilePic} style={{ background: '#eee', border: 'none', borderRadius: 6, padding: '4px 10px', cursor: 'pointer' }}>Remove</button>
              </div>
            </div>
            {/* Bio */}
            <div style={{ marginBottom: 16 }}>
              <label style={{ fontWeight: 600 }}>Bio</label><br />
              <textarea value={editBio} onChange={e => setEditBio(e.target.value)} rows={3} style={{ width: '100%', borderRadius: 6, border: '1px solid #ccc', padding: 8, marginTop: 4 }} />
              <button onClick={() => setEditBio('')} style={{ background: '#eee', border: 'none', borderRadius: 6, padding: '4px 10px', cursor: 'pointer', marginTop: 4 }}>Clear Bio</button>
            </div>
            {/* Resume (PDF) - Feature coming soon */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
              <button onClick={() => setEditModalOpen(false)} style={{ background: '#eee', border: 'none', borderRadius: 6, padding: '8px 20px', cursor: 'pointer' }}>Cancel</button>
              <button onClick={handleSave} style={{ background: '#174f84', color: '#fff', border: 'none', borderRadius: 6, padding: '8px 20px', cursor: 'pointer' }}>Save</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AlumniProfile; 