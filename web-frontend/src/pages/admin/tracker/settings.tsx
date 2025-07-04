import React, { useState, ChangeEvent } from 'react';
import './Tracker.css';

interface User {
  name: string;
  email: string;
  course: string;
}

const Settings: React.FC = () => {
  const [selectedUsers, setSelectedUsers] = useState<number[]>([]);

  const allUsers: User[] = [
    { name: 'Ana Black', email: 'ana@gmail.com', course: 'BSIT' },
    { name: 'Ana Black', email: 'ana@gmail.com', course: 'BSIS' },
    { name: 'Ana Black', email: 'ana@gmail.com', course: 'BIT-CT' },
  ];

  const handleSelectAll = () => {
    if (selectedUsers.length === allUsers.length) {
      setSelectedUsers([]);
    } else {
      setSelectedUsers(allUsers.map((_, idx) => idx));
    }
  };

  const handleToggleUser = (index: number) => {
    setSelectedUsers((prev) =>
      prev.includes(index)
        ? prev.filter((i) => i !== index)
        : [...prev, index]
    );
  };

  const [message, setMessage] = useState<string>(`Hi [User's Name],

We hope you're doing well! This is a gentle reminder to complete the required Tracker Form to help us keep everything on track and up to date.

Please take a few moments to fill it out by clicking the link below:
👉 Fill Out the Tracker Form

Your timely response is greatly appreciated and helps us stay aligned and organized.
If you have any questions or need assistance, feel free to reply to this message.

Thank you!
Best regards,
CCICT`);

  const handleSend = () => {
    alert('Form message sent:\n\n' + message);
  };

  const handleMessageChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
  };

  return (
    <div className="tracker-container">
      <div className="tracker-inner">
        {/* Editable Message Card */}
        <div className="card">
          <div className="message-header">
            <h3>Please Fill Out the Tracker Form</h3>
            <button className="border-button" onClick={handleSend}>Send Form</button>
          </div>
          <hr />
          <textarea
            value={message}
            onChange={handleMessageChange}
            className="message-textarea"
          />
        </div>

        {/* Users Who Responded */}
        <div className="card">
          <div className="users-header">
            <h3>Users Who Responded</h3>
          </div>
          <table className="user-table">
            <thead>
              <tr>
                <th>Account</th>
                <th>Course</th>
              </tr>
            </thead>
            <tbody>
              {allUsers.map((user, index) => (
                <tr key={index}>
                  <td>
                    <div className="user-info">
                      <img src="https://via.placeholder.com/32" alt="avatar" />
                      <div>
                        <strong>{user.name}</strong><br />
                        <span>{user.email}</span>
                      </div>
                    </div>
                  </td>
                  <td>{user.course}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Users Who Haven't Responded */}
        <div className="card">
          <div className="users-header">
            <h3>Users Who Haven't Responded</h3>
            <button className="border-button" onClick={handleSelectAll}>
              {selectedUsers.length === allUsers.length ? 'Unselect All' : 'Select All'}
            </button>
          </div>
          <table className="user-table">
            <thead>
              <tr>
                <th>Account</th>
                <th>Course</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {allUsers.map((user, index) => (
                <tr key={index}>
                  <td>
                    <div className="user-info">
                      <img src="https://via.placeholder.com/32" alt="avatar" />
                      <div>
                        <strong>{user.name}</strong><br />
                        <span>{user.email}</span>
                      </div>
                    </div>
                  </td>
                  <td>{user.course}</td>
                  <td>
                    <input
                      type="checkbox"
                      checked={selectedUsers.includes(index)}
                      onChange={() => handleToggleUser(index)}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

      </div>
    </div>
  );
};

export default Settings;
