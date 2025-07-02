   document.addEventListener('DOMContentLoaded', () => {
       // Get references to DOM elements
       const interviewQuestionInput = document.getElementById('interview-question');
       const userAnswerInput = document.getElementById('user-answer');
       const getFeedbackButton = document.getElementById('get-feedback-button');
       const loadingIndicator = document.getElementById('loading-indicator');
       const feedbackArea = document.getElementById('feedback-area');
       const feedbackContent = document.getElementById('feedback-content');
       const errorMessage = document.getElementById('error-message');

       // Function to show/hide loading indicator and disable/enable button
       function setLoadingState(isLoading) {
           if (isLoading) {
               loadingIndicator.classList.remove('hidden');
               getFeedbackButton.disabled = true;
               getFeedbackButton.textContent = 'Analyzing...';
               feedbackArea.classList.add('hidden'); // Hide previous feedback
               errorMessage.classList.add('hidden'); // Hide previous errors
           } else {
               loadingIndicator.classList.add('hidden');
               getFeedbackButton.disabled = false;
               getFeedbackButton.textContent = 'Get Feedback';
           }
       }

       // Function to display an error message
       function displayError(message) {
           errorMessage.textContent = message;
           errorMessage.classList.remove('hidden');
           feedbackArea.classList.add('hidden'); // Ensure feedback is hidden on error
       }

       // Function to clear error messages
       function clearError() {
           errorMessage.classList.add('hidden');
           errorMessage.textContent = '';
       }

       // Event listener for the "Get Feedback" button
       getFeedbackButton.addEventListener('click', async () => {
           const question = interviewQuestionInput.value.trim();
           const answer = userAnswerInput.value.trim();

           clearError(); // Clear any previous errors

           if (!question || !answer) {
               displayError('Please enter both an interview question and your answer.');
               return;
           }

           setLoadingState(true); // Show loading indicator

           try {
               const response = await fetch('/get_feedback', {
                   method: 'POST',
                   headers: {
                       'Content-Type': 'application/json',
                   },
                   body: JSON.stringify({ question, answer }),
               });

               const data = await response.json();

               if (response.ok) {
                   // Display the AI feedback
                   feedbackContent.innerHTML = marked.parse(data.feedback); // Use marked.js to render markdown
                   feedbackArea.classList.remove('hidden');
               } else {
                   // Handle errors from the backend
                   displayError(data.error || 'An unknown error occurred.');
               }
           } catch (error) {
               console.error('Error fetching feedback:', error);
               displayError('Could not connect to the server. Please try again.');
           } finally {
               setLoadingState(false); // Hide loading indicator
           }
       });

       // Initialize marked.js for Markdown rendering
       // This script will be loaded from a CDN in the HTML.
       // It converts markdown strings into HTML.
       if (typeof marked === 'undefined') {
           // Fallback or error if marked.js is not loaded
           console.error("marked.js library not found. Markdown rendering will not work.");
           // You might want to dynamically load it or show a user message
       }
   });

   // Load marked.js library dynamically for Markdown rendering
   // This is crucial for displaying the AI's structured feedback nicely.
   const script = document.createElement('script');
   script.src = 'https://cdn.jsdelivr.net/npm/marked/marked.min.js';
   script.onload = () => {
       console.log('marked.js loaded.');
       // Optionally, you can set marked.js options here if needed
       // marked.setOptions({ ... });
   };
   script.onerror = () => {
       console.error('Failed to load marked.js.');
   };
   document.head.appendChild(script);
   