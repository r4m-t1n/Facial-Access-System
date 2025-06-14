async function captureImage() {
    try {
        const response = await fetch('/capture', {
            method: 'POST'
        });

        const result = await response.json();

        if (!response.ok) {
            alert(result.message);
        }
    } catch (error) {
        console.error("Error:", error);
        alert(`Error during capturing: ${error.message}`);
    }
}