import React, { useState, ChangeEvent } from 'react';
import './Tracker.css';

const Question: React.FC = () => {

  const [formTitle, setFormTitle] = useState<string>('Untitled Form');
  const [formDescription, setFormDescription] = useState<string>(
    'Lorem Ipsum is simply dummy text of the printing and typesetting industry.'
  );

  const handleTitleChange = (e: ChangeEvent<HTMLInputElement>) => {
    setFormTitle(e.target.value);
  };

  const handleDescriptionChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setFormDescription(e.target.value);
  };

  return (
    <div className="tracker-container">
      <div className="tracker-inner">
        {/* Editable Form Description */}
        <div className="card form-description">
          <input
            type="text"
            className="form-title-input"
            value={formTitle}
            onChange={handleTitleChange}
            placeholder="Form Title"
          />
          <textarea
            className="form-description-textarea"
            value={formDescription}
            onChange={handleDescriptionChange}
            placeholder="Form Description"
            rows={3}
          />
        </div>

        {/* Question Cards */}
        <div className="card question-box">
          <h3>Question 1</h3>
          <p>No. of Response</p>
        </div>

        <div className="card question-box">
          <h3>Question 2</h3>
          <p>No. of Response</p>
        </div>
      </div>
    </div>
  );
};

export default Question;
