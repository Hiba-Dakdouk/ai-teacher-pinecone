// the file that talks to the backend
import axios from 'axios';

const API_URL = 'http://localhost:8000'; // Update this if your backend is running on a different URL

export const sendMessage = async (messages) => {
  
    const response = await axios.post(`${API_URL}/chat`, { messages }); // Send the messages to the backend
    return response.data.reply; // Return the reply from the backend
  
};

export const uploadDocument = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await axios.post(`${API_URL}/upload`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });   
        return response.data; // Return success message
    } catch (err) {
        console.error(err);
        throw new Error('Failed to upload document. Please try again.');
    }   
}    
