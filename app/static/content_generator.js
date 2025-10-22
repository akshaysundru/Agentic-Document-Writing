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

    // Export to Word
    document.getElementById('export-btn').addEventListener('click', async () => {
        const viewPanel = document.getElementById('view-panel');
        const htmlContent = viewPanel.innerHTML;

        try {
            const response = await fetch('/export_word', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: htmlContent })
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'generated_content.docx';
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);

        } catch (err) {
            console.error('Export failed:', err);
            alert('Failed to export content to Word.');
        }
    });
});
