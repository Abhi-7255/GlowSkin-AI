document.addEventListener("DOMContentLoaded", () => {
    // ==========================================
    // 1. Creative Button Ripple Effect
    // ==========================================
    const buttons = document.querySelectorAll("button, .btn");
    
    buttons.forEach(button => {
        button.addEventListener("click", function(e) {
            let x = e.clientX - e.target.getBoundingClientRect().left;
            let y = e.clientY - e.target.getBoundingClientRect().top;
            
            let ripples = document.createElement("span");
            ripples.style.left = x + "px";
            ripples.style.top = y + "px";
            ripples.style.position = "absolute";
            ripples.style.background = "rgba(255, 255, 255, 0.5)";
            ripples.style.width = "100px";
            ripples.style.height = "100px";
            ripples.style.transform = "translate(-50%, -50%)";
            ripples.style.borderRadius = "50%";
            ripples.style.animation = "rippleEffect 0.6s linear";
            ripples.style.pointerEvents = "none";
            
            // Add relative positioning to button if it doesn't have it
            if(window.getComputedStyle(this).position === "static") {
                this.style.position = "relative";
                this.style.overflow = "hidden";
            }
            
            this.appendChild(ripples);
            setTimeout(() => { ripples.remove(); }, 600);
        });
    });

    // ==========================================
    // 2. Dynamic Input Highlighting
    // ==========================================
    const inputs = document.querySelectorAll("input, textarea");
    inputs.forEach(input => {
        input.addEventListener("focus", () => {
            if (input.parentElement) {
                input.parentElement.style.transform = "scale(1.02)";
                input.parentElement.style.transition = "transform 0.3s ease";
            }
        });
        input.addEventListener("blur", () => {
            if (input.parentElement) {
                input.parentElement.style.transform = "scale(1)";
            }
        });
    });

    // ==========================================
    // 3. Skin Analysis Form Handling (NEW)
    // ==========================================
    // Ensure these IDs match your HTML form and result container
    const form = document.getElementById('upload-form'); 
    const messageBox = document.getElementById('message-box'); 

    if (form && messageBox) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault(); // Stop the page from reloading
            
            // Show loading state
            messageBox.innerHTML = "Analyzing your photo... Please wait."; 
            messageBox.style.color = "black";
            
            const formData = new FormData(form);
            
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                // CHECK FOR ERRORS (Catches the "No Face" or "Multiple Faces" errors from app.py)
                if (!response.ok) {
                    messageBox.innerHTML = `⚠️ ${data.error}`;
                    messageBox.style.color = "red";
                    return; 
                }
                
                // SUCCESS: Display the AI predictions
                messageBox.style.color = "green";
                messageBox.innerHTML = `
                    <h3>Analysis Complete!</h3>
                    <p><strong>Skin Type:</strong> ${data.result} (${data.confidence})</p>
                    <p><strong>Description:</strong> ${data.description}</p>
                `;
                
            } catch (error) {
                console.error("Upload error:", error);
                messageBox.innerHTML = "⚠️ A network error occurred while connecting to the server.";
                messageBox.style.color = "red";
            }
        });
    }
});