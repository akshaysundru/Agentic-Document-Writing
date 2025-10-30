document.addEventListener("DOMContentLoaded", () => {
    // Generate content
    document.querySelector('.api-call').addEventListener('click', async () => {
        const input = document.getElementById('input-box').innerText;
        const viewPanel = document.getElementById('view-panel');
        viewPanel.innerHTML = '<p><em>Generating content...</em></p>';

        try {
            const response = await fetch('/content_generation', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: input })
            });

            const data = await response.json();
            viewPanel.innerHTML = data.output || '<p><em>No output returned.</em></p>';
        } catch (error) {
            viewPanel.innerHTML = `<p class="text-danger"><strong>Error:</strong> ${error}</p>`;
        }
    });

    
});
