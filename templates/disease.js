document.addEventListener('DOMContentLoaded', () => {
    const openCameraBtn = document.getElementById('open-camera-btn');
    const cameraView = document.getElementById('camera-view');
    const cameraStream = document.getElementById('camera-stream');
    const captureBtn = document.getElementById('capture-btn');
    const canvas = document.getElementById('canvas');
    const resultsDiv = document.getElementById('results');
    const imageInput = document.getElementById('image');
    const imagePreview = document.getElementById('image-preview');
    const predictBtn = document.getElementById('predict-btn');

    let stream = null;

    // Show image preview when a file is selected
    imageInput.addEventListener('change', () => {
        const file = imageInput.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                imagePreview.src = e.target.result;
                imagePreview.classList.remove('d-none');
                resultsDiv.innerHTML = ''; // Clear previous results
            };
            reader.readAsDataURL(file);
        }
    });

    // Open/Close Camera (use class d-none to toggle visibility)
    openCameraBtn.addEventListener('click', async () => {
        const isOpen = !cameraView.classList.contains('d-none');
        if (isOpen) {
            // Close camera
            if (stream) {
                try { stream.getTracks().forEach(track => track.stop()); } catch {}
                stream = null;
            }
            cameraView.classList.add('d-none');
            captureBtn.classList.add('d-none');
            openCameraBtn.textContent = 'Open Camera';
            return;
        }
        // Open camera
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
            cameraStream.srcObject = stream;
            cameraView.classList.remove('d-none');
            captureBtn.classList.remove('d-none');
            openCameraBtn.textContent = 'Close Camera';
        } catch (error) {
            console.error('Error accessing camera:', error);
            resultsDiv.innerHTML = `<div class="alert alert-danger"><strong>Error:</strong> Could not access the camera. Please ensure you have a camera connected and have granted permission.</div>`;
        }
    });

    // Capture Photo
    captureBtn.addEventListener('click', () => {
        if (stream) {
            const context = canvas.getContext('2d');
            canvas.width = cameraStream.videoWidth;
            canvas.height = cameraStream.videoHeight;
            context.drawImage(cameraStream, 0, 0, canvas.width, canvas.height);

            // Show preview
            const dataUrl = canvas.toDataURL('image/jpeg');
            imagePreview.src = dataUrl;
            imagePreview.classList.remove('d-none');
            resultsDiv.innerHTML = ''; // Clear previous results

            canvas.toBlob((blob) => {
                const capturedFile = new File([blob], "capture.jpg", { type: "image/jpeg", lastModified: new Date().getTime() });
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(capturedFile);
                imageInput.files = dataTransfer.files;

                // Stop camera and hide view
                try { stream.getTracks().forEach(track => track.stop()); } catch {}
                stream = null;
                cameraView.classList.add('d-none');
                captureBtn.classList.add('d-none');
                openCameraBtn.textContent = 'Open Camera';
            }, 'image/jpeg');
        }
    });

    // Predict button (no form submit)
    predictBtn.addEventListener('click', async function() {
        if (imageInput.files.length > 0) {
            const formData = new FormData();
            formData.append('image', imageInput.files[0]);
            await predictImage(formData);
        } else {
            resultsDiv.innerHTML = `<div class="alert alert-info">Please select an image to upload or use the camera.</div>`;
        }
    });

    async function predictImage(formData) {
        resultsDiv.innerHTML = '<div class="text-center"><div class="spinner-border text-success" role="status"><span class="visually-hidden">Loading...</span></div><p class="mt-2">Analyzing image...</p></div>';

        try {
            const response = await fetch('/api/disease/predict', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'An error occurred');
            }

            const data = await response.json();
            await displayResults(data);

        } catch (error) {
            console.error('Error:', error);
            
            // Handle quota exceeded error
            if (error.message && error.message.includes('429') || error.message.includes('quota')) {
                resultsDiv.innerHTML = `
                    <div class="alert alert-warning">
                        <h5><i class="fas fa-clock"></i> Daily Limit Reached</h5>
                        <p>You've used all 50 free requests for today.</p>
                        <hr>
                        <h6>What to do:</h6>
                        <ul>
                            <li>Try again tomorrow (limit resets daily)</li>
                            <li>Or upgrade to paid Gemini API plan</li>
                            <li>Paid plan gives unlimited requests</li>
                        </ul>
                        <p class="mt-3"><strong>Time until reset:</strong> About 24 hours from first request</p>
                    </div>`;
            } else {
                resultsDiv.innerHTML = `<div class="alert alert-danger"><strong>Error:</strong> ${error.message}</div>`;
            }
        }
    }

    async function displayResults(data) {
        resultsDiv.innerHTML = '';

        if (data.predictions && data.predictions.length > 0) {
            const prediction = data.predictions[0];
            const diseaseClass = prediction.class.toLowerCase().replace(/\s+/g, '_');
            
            // Use disease_details from prediction result (includes Gemini data)
            let diseaseDetails = data.disease_details || null;
            
            // Parse protection text for natural and fertilizer sections
            let naturalProtection = '';
            let fertilizerTips = '';
            if (diseaseDetails?.protection && typeof diseaseDetails.protection === 'string') {
                const protectionText = diseaseDetails.protection;
                const naturalMatch = protectionText.match(/\*\*Natural Solutions:\*\*(.*?)(?=\*\*Fertilizer Solutions:\*\*|$)/s);
                if (naturalMatch) {
                    naturalProtection = naturalMatch[1].trim();
                }
                const fertilizerMatch = protectionText.match(/\*\*Fertilizer Solutions:\*\*(.*?)$/s);
                if (fertilizerMatch) {
                    fertilizerTips = fertilizerMatch[1].trim();
                }
            }
            
            const formatPoints = (text) => {
                if (!text) return '';
                return '<ul>' + text.split('\n').map(line => line.trim().replace(/^\*\s*/, '')).filter(line => line).map(line => `<li>${line}</li>`).join('') + '</ul>';
            };

            if (diseaseDetails) {
                // Check if this is a healthy plant
                const isHealthy = data.status === 'healthy' || diseaseDetails.name.toLowerCase().includes('healthy');
                
                const resultCard = `
                    <div class="result-card">
                        <p><strong>Plant:</strong> ${data.plant_name || 'Unknown'}</p>
                        <p><strong>Disease:</strong> ${diseaseDetails.name}</p>
                        <p><strong>Confidence:</strong> ${(prediction.confidence * 100).toFixed(2)}%</p>
                        
                        <h5>What We Found</h5>
                        
                        ${diseaseDetails ? `
                        <p><strong>🍃 Plant Condition</strong></p>
                        ${formatPoints(diseaseDetails.description) || "<p>No information available.</p>"}
                        ` : ''}
                        
                        ${diseaseDetails ? `
                        <p><strong>🦠 Current Status</strong></p>
                        ${formatPoints(diseaseDetails.causes) || "<p>No information available.</p>"}
                        ` : ''}
                        
                        ${naturalProtection ? `
                        <p><strong>🌿 How to Keep Healthy (Natural Methods)</strong></p>
                        ${formatPoints(naturalProtection)}
                        ` : ''}
                        
                        ${fertilizerTips ? `
                        <p><strong>🌾 Fertilizer Instructions (What & How)</strong></p>
                        ${formatPoints(fertilizerTips)}
                        ` : ''}
                    </div>
                `;
                resultsDiv.innerHTML = resultCard;
            } else {
                resultsDiv.innerHTML = `
                    <div class="result-card">
                        <h5 class="text-success"><i class="fas fa-check-circle"></i> Plant is Healthy</h5>
                        <p>Your plant looks good. No disease found in the photo.</p>
                        <hr>
                        <h6><i class="fas fa-lightbulb"></i> Better Photo Tips</h6>
                        <ul>
                            <li>Take clear photo. Good light.</li>
                            <li>Show the sick leaf close.</li>
                            <li>Try different side.</li>
                            <li>Remove extra things from photo.</li>
                        </ul>
                        <h6><i class="fas fa-seedling"></i> Keep Your Plant Strong</h6>
                        <ul>
                            <li>Water early morning. Keep leaves dry.</li>
                            <li>Give sunlight as needed.</li>
                            <li>Remove old, dry leaves.</li>
                            <li>Use compost. Don't over-feed.</li>
                        </ul>
                    </div>
                `;
            }
        }
    }
}); 