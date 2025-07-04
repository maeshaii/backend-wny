import React, { useState, ChangeEvent, KeyboardEvent } from 'react';
import './Tracker.css';
import { FaPlusCircle } from 'react-icons/fa';
import { Link, useLocation, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from '../global/sidebar'; // ✅ Sidebar import
import Question from './questions';
import Responses from './responses';
import Setting from './settings';

const Tracker: React.FC = () => {
  const location = useLocation();

  const isActive = (path: string): boolean => location.pathname === path;
  const isQuestionPage = location.pathname === '/tracker/questions' || location.pathname === '/tracker';

  const [formTitle, setFormTitle] = useState<string>('Untitled Form');
  const [isEditingTitle, setIsEditingTitle] = useState<boolean>(false);

  const handleTitleClick = () => setIsEditingTitle(true);

  const handleTitleChange = (e: ChangeEvent<HTMLInputElement>) => {
    setFormTitle(e.target.value);
  };

  const handleTitleBlur = () => setIsEditingTitle(false);

  const handleTitleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      setIsEditingTitle(false);
    }
  };

  return (
    <div style={{ display: 'flex'}}>
      <Sidebar /> {/* ✅ Sidebar added */}

      <div className="tracker-container" style={{ flex: 1, padding: '20px' }}>
        {isQuestionPage && (
          <div className="floating-button-group">
            <button className="icon-button">
              <FaPlusCircle /> Add Question
            </button>
            <button className="icon-button">
              <FaPlusCircle /> Add Category
            </button>
          </div>
        )}

        <div className="tracker-inner">
          {/* Header */}
          <div className="tracker-header">
            {isEditingTitle ? (
              <input
                type="text"
                value={formTitle}
                onChange={handleTitleChange}
                onBlur={handleTitleBlur}
                onKeyDown={handleTitleKeyDown}
                autoFocus
                className="form-title-input"
              />
            ) : (
              <h2 className="form-title" onClick={handleTitleClick} title="Click to edit">
                {formTitle}
              </h2>
            )}

            <div className="tracker-tabs">
              <Link to="/tracker/questions" className={isActive('/tracker/questions') ? 'active' : ''}>
                Questions
              </Link>
              <Link to="/tracker/responses" className={isActive('/tracker/responses') ? 'active' : ''}>
                Responses
              </Link>
              <Link to="/tracker/settings" className={isActive('/tracker/settings') ? 'active' : ''}>
                Settings
              </Link>
            </div>
          </div>

          {/* Tab Content */}
          <Routes>
            <Route index element={<Navigate to="questions" replace />} />
            <Route path="questions" element={<Question />} />
            <Route path="responses" element={<Responses />} />
            <Route path="settings" element={<Setting />} />
          </Routes>
        </div>
      </div>
    </div>
  );
};

export default Tracker;
