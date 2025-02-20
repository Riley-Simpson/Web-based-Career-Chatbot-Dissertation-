document.addEventListener("DOMContentLoaded", () => {
    checkSessionStatus();

    

    window.addEventListener('beforeunload', handleWindowClose);
    window.addEventListener('unload', handleWindowClose);
});

function checkSessionStatus() {
    fetch('/issessionactive', {
        method: 'GET',
        credentials: 'include'
    })
        .then(response => {
            if (!response.ok) {
                return response.text().then(text => { throw new Error(`HTTP error! status: ${response.status}, details: ${text}`); });
            }
            return response.json();
        })
        .then(data => {
            if (data.sessionActive) {
                displaySessionActiveMessage();
            } else {
                showModal();
            }
        })
        .catch(error => {
            console.error('Error checking session status:', error);
        });
}

function handleWindowClose(event) {
    navigator.sendBeacon('/endsession');
    fetch('/endsession', {
        method: 'POST',
        credentials: 'include'
    })
        .then(response => response.json())
        .then(data => {
            console.log('Session ended:', data.sessionEnded);
        })
        .catch(error => {
            console.error('Error ending session:', error);
        });
}

function showModal() {
    document.getElementById('consent-modal').style.display = 'block';
}

function closeModal() {
    document.getElementById('consent-modal').style.display = 'none';
    startSession();
}

function startSession() {
    const sessionDuration = 10 * 60 * 1000; // 10 min in ms
    const endTime = new Date(Date.now() + sessionDuration);

    // Start the session on the server
    fetch('/startsession', {
        method: 'POST',
        credentials: 'include'
    })
        .then(response => response.json())
        .then(data => {
            if (data.sessionActive) {
                displaySessionActiveMessage();
            } else {
                showChat();
                startSessionTimer(endTime); 
            }
        })
        .catch(error => {
            console.error('Error starting session:', error);
        });
}


function checkGoogleFormSubmission() {
    localStorage.setItem('consentGiven', 'true');
    closeModal();
    showChat();
}
function displaySessionActiveMessage() {
    const consentModal = document.getElementById('consent-modal');
    consentModal.style.display = 'block';

    const modalContent = document.querySelector('.modal-content');
    modalContent.innerHTML = `
        <h2>Session Active</h2>
        <p>Another user is currently using the chatbot. Please try again later.</p>
        <button onclick="window.location.reload()">Retry</button>
    `;
}

function showChat() {
    document.getElementById('chat-box').style.display = 'block';
    document.getElementById('query-input').style.display = 'block';
    document.getElementById('send-button').style.display = 'block';
    document.getElementById('resume-upload').style.display = 'flex';
}

function sendQuery() {
    const queryInput = document.getElementById('query-input');
    const query = queryInput.value;
    if (!query) return;

    disableInputs();  // Disable inputs during processing

    addMessage(query, 'user');
    queryInput.value = '';

    const spinner = document.getElementById('loading-spinner');
    spinner.style.display = 'block';

    console.log('Sending query to backend:', query);

    const payload = JSON.stringify({ context: query });
    console.log('Payload being sent:', payload);

    fetch('/chat', {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
        },
        body: payload
    })
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                return response.text().then(text => {
                    throw new Error(`HTTP error! status: ${response.status}, details: ${text}`);
                });
            }
            return response.json();
        })
        .then(data => {
            spinner.style.display = 'none';
            if (data.response) {
                const markdown = data.response;
                addMessage(markdown, 'bot', true);
            } else {
                addMessage('Response Error: Sorry, something went wrong. Please try again.', 'bot');
            }
        })
        .catch(error => {
            spinner.style.display = 'none';
            console.error('Error in sendQuery:', error);
            addMessage('Sorry, something went wrong. Please try again.', 'bot');
        })
        .finally(() => {
            enableInputs();  
        });
}


function uploadResume() {
    const resumeInput = document.getElementById('resume-input');
    const file = resumeInput.files[0];

    if (!file) {
        addMessage('No file selected for upload.', 'bot');
        return;
    }
    disableInputs();
    
    const spinner = document.getElementById('loading-spinner');
    spinner.style.display = 'block';
    addMessage('Reading Resume...', 'bot')
    
    const formData = new FormData();
    formData.append('resume', file);

    fetch('/upload_resume', {
        method: 'POST',
        credentials: 'include',
        body: formData,
    })
        .then(response => response.json())
        .then(data => {
            spinner.style.display = 'none';
            if (response.status === 403) {
                alert(data.response);
            } else if (data.response) {
                addMessage(data.response, 'bot', true);
            } else {
                addMessage('No response received from server.', 'bot');
            }
        })
        .catch(error => {
            spinner.style.display = 'none';
            console.error('Error in uploadResume:', error);
            addMessage('Sorry, something went wrong. Please try again.', 'bot');
        })
        .finally(() => {
            enableInputs();
        });
}


/**
* 
* 
* @return { Promise } 
*/
function uploadResume() {
    const resumeInput = document.getElementById('resume-input');
    const file = resumeInput.files[0];

    if (!file) {
        console.log('No file selected for upload.');
        addMessage('No file selected for upload.', 'bot');
        return;
    }
    disableInputs();
    const spinner = document.getElementById('loading-spinner');
    spinner.style.display = 'block';

    const formData = new FormData();
    formData.append('resume', file);

    console.log('Uploading resume...');
    addMessage('Reading resume...', 'bot');

    fetch('/upload_resume', {
        method: 'POST',
        body: formData,
    })
        .then(response => {
            console.log('Response status:', response.status);

            // If the response is not okay, throw an error
            if (!response.ok) {
                return response.text().then(text => {
                    throw new Error(`HTTP error! status: ${response.status}, details: ${text}`);
                });
            }

            // Return the JSON data from the response
            return response.json();
        })
        .then(data => {
            spinner.style.display = 'none'; // Hide the spinner
            console.log('Chat response data:', data);

            // Directly check for the presence of the response field
            if (data.response) {
                const markdown = data.response;
                addMessage(markdown, 'bot', true);
            } else {
                addMessage('No response received from server.', 'bot');
                console.error('No response field in returned data:', data);
            }
        })
        .catch(error => {
            spinner.style.display = 'none'; // Hide the spinner
            console.error('Error in uploadResume:', error);
            addMessage('Sorry, something went wrong. Please try again.', 'bot');
        })
        .finally(() => {
            enableInputs();
        });
}



function disableInputs() {
    document.getElementById('query-input').disabled = true;
    document.getElementById('send-button').disabled = true;
    document.getElementById('resume-input').disabled = true;
    document.getElementById('resume-upload-button').disabled = true;
}

function enableInputs() {
    document.getElementById('query-input').disabled = false;
    document.getElementById('send-button').disabled = false;
    document.getElementById('resume-input').disabled = false;
    document.getElementById('resume-upload-button').disabled = false;
}

function addMessage(text, sender, isMarkdown = false) {
    const messagesDiv = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);

    if (isMarkdown) {
        messageDiv.innerHTML = marked.parse(text);
    } else {
        messageDiv.textContent = text;
    }

    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function disableBackdoor() {
    localStorage.removeItem('backdoor');
    localStorage.removeItem('sessionEnded');
    window.location.reload();
}

function enableBackdoor() {
    localStorage.setItem('backdoor', 'true');
    localStorage.removeItem('endTime');
}

function endChatSession() {
    addMessage('You have used your allocated time, thank you for your time :)', 'bot');

    localStorage.setItem('sessionEnded', 'true');
    localStorage.removeItem('endTime');
    localStorage.removeItem('sessionActive');  // Mark session as inactive

    setTimeout(() => {
        document.getElementById('chat-box').style.display = 'none';
        document.getElementById('query-input').style.display = 'none';
        document.querySelector('button[onclick="sendQuery()"]').style.display = 'none';
        document.getElementById('resume-upload').style.display = 'none';
        document.getElementById('feedback-form').style.display = 'block';

        const timerDisplay = document.getElementById('timer');
        // Removes the timer display.
        if (timerDisplay) {
            timerDisplay.remove();
        }
    }, 5000);
}

function startSessionTimer(endTime) {
    // Create the timer display element if it doesn't exist
    let timerDisplay = document.getElementById('timer');
    if (!timerDisplay) {
        timerDisplay = document.createElement('div');
        timerDisplay.id = 'timer';
        timerDisplay.style.position = 'absolute';
        timerDisplay.style.bottom = '10px';
        timerDisplay.style.right = '10px';
        timerDisplay.style.backgroundColor = '#f9f9f9';
        timerDisplay.style.padding = '10px';
        timerDisplay.style.borderRadius = '5px';
        timerDisplay.style.border = '1px solid #ddd';
        document.body.appendChild(timerDisplay);
    }

    // Calculate and update the timer every second
    const interval = setInterval(() => {
        const now = new Date().getTime();
        const timeLeft = new Date(endTime).getTime() - now;

        if (timeLeft <= 0) {
            clearInterval(interval);
            endChatSession();
            timerDisplay.textContent = "Session ended";
            return;
        }

        const minutesLeft = Math.floor(timeLeft / 1000 / 60);
        const secondsLeft = Math.floor((timeLeft / 1000) % 60);
        timerDisplay.textContent = `Time left: ${minutesLeft}:${secondsLeft < 10 ? '0' : ''}${secondsLeft}`;
    }, 1000);
}
