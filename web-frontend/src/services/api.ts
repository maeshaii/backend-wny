import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/',
  withCredentials: true,
});

function formatBirthdateToWords(dateStr: string): string {
  if (!dateStr) return dateStr;
  let month, day, year;
  if (dateStr.includes('/')) {
    // MM/DD/YYYY
    [month, day, year] = dateStr.split('/');
  } else if (dateStr.includes('-')) {
    // YYYY-MM-DD
    [year, month, day] = dateStr.split('-');
  } else {
    return dateStr; // fallback
  }
  const months = [
    'january', 'february', 'march', 'april', 'may', 'june',
    'july', 'august', 'september', 'october', 'november', 'december'
  ];
  if (!month || !day || !year) return dateStr;
  return `${months[parseInt(month, 10) - 1]} ${parseInt(day, 10)}, ${year}`;
}

// Login API function (JWT, for all account types)
export const loginUser = async (acc_username: string, acc_password: string) => {
  console.log('Sending:', { acc_username, acc_password });
  try {
    const response = await api.post(
      'token/',
      { acc_username, acc_password }
    );
    // Save tokens and user info to localStorage
    localStorage.setItem('accessToken', response.data.access);
    localStorage.setItem('refreshToken', response.data.refresh);
    localStorage.setItem('user', JSON.stringify(response.data.user));
    return { success: true, ...response.data };
  } catch (error: any) {
    return { success: false, message: 'Invalid credentials' };
  }
};

// Import alumni accounts from Excel
export const importAlumni = async (file: File, batchYear: string, course: string) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('batch_year', batchYear);
    formData.append('course', course);

    const response = await api.post('import-alumni/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  } catch (error: any) {
    if (error.response?.data) {
      return error.response.data;
    }
    return { success: false, message: 'Network error occurred' };
  }
};

// Fetch alumni statistics (counts per year)
export const fetchAlumniStatistics = async () => {
  const response = await axios.get('http://127.0.0.1:8000/api/statistics/alumni/');
  return response.data;
};

// Fetch alumni user list
export const fetchAlumniList = async () => {
  const response = await axios.get('http://127.0.0.1:8000/api/users/alumni/');
  return response.data;
};

// Fetch alumni by year
export const fetchAlumniByYear = async (year: string) => {
  const response = await axios.get(`http://127.0.0.1:8000/api/users/alumni/?year=${year}`);
  return response.data;
};

// Fetch alumni employment statistics by year and course
export const fetchAlumniEmploymentStats = async (year = 'ALL', course = 'ALL') => {
  const response = await axios.get(`http://127.0.0.1:8000/api/statistics/alumni/?year=${year}&course=${course}`);
  return response.data;
};

export default api;
