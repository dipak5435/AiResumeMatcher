// File upload handler
document.getElementById('resumeFile')?.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/upload-resume', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            alert('Error uploading file: ' + error.error);
            return;
        }

        const data = await response.json();
        document.getElementById('resume').value = data.text;
    } catch (error) {
        console.error('Error:', error);
        alert('Error uploading file');
    }
});

// Form submission
document.getElementById('matchForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const resume = document.getElementById('resume').value.trim();
    const jd = document.getElementById('jd').value.trim();
    const save = document.getElementById('saveMatch')?.checked || false;

    if (!resume || !jd) {
        alert('Please fill in both resume and job description');
        return;
    }

    try {
        // Show loading state
        const btn = e.target.querySelector('button[type="submit"]');
        const originalText = btn.textContent;
        btn.textContent = 'Analyzing...';
        btn.disabled = true;

        const response = await fetch('/api/match', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ resume, jd, save })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Matching failed');
        }

        const result = await response.json();
        displayResults(result);

        btn.textContent = originalText;
        btn.disabled = false;
    } catch (error) {
        console.error('Error:', error);
        alert('Error: ' + error.message);

        const btn = e.target.querySelector('button[type="submit"]');
        btn.textContent = 'Analyze Match';
        btn.disabled = false;
    }
});

function displayResults(result) {
    // Calculate rating
    const score = result.score;
    let rating = 'Poor Fit';
    if (score >= 75) rating = 'Excellent Fit!';
    else if (score >= 60) rating = 'Good Fit';
    else if (score >= 45) rating = 'Moderate Fit';
    else if (score >= 30) rating = 'Below Average Fit';

    // Update results section
    document.getElementById('scoreValue').textContent = Math.round(score);
    document.getElementById('scoreRating').textContent = rating;
    document.getElementById('explanation').textContent = result.explanation;

    // Handle recommendations
    const recsBox = document.getElementById('recommendationsBox');
    if (result.recommendations && result.recommendations.length > 0) {
        const recsList = document.getElementById('recommendationsList');
        recsList.innerHTML = result.recommendations
            .map(rec => `<li>${rec}</li>`)
            .join('');
        recsBox.style.display = 'block';
    } else {
        recsBox.style.display = 'none';
    }

    // Show results section
    document.getElementById('resultsSection').style.display = 'block';

    // Scroll to results
    document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
}

function resetForm() {
    document.getElementById('matchForm').reset();
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('matchesList').style.display = 'none';
}

async function loadMatches() {
    try {
        const response = await fetch('/api/matches');
        if (!response.ok) throw new Error('Failed to load matches');

        const data = await response.json();
        displayMatches(data);
    } catch (error) {
        console.error('Error:', error);
        alert('Error loading matches: ' + error.message);
    }
}

function displayMatches(data) {
    const { stats, matches } = data;

    // Update stats
    const statsBox = document.getElementById('statsBox');
    statsBox.innerHTML = `
        <div class="stat-item">
            <div class="stat-value">${stats.total}</div>
            <div class="stat-label">Total Matches</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">${stats.average_score.toFixed(1)}</div>
            <div class="stat-label">Average Score</div>
        </div>
    `;

    // Update matches table
    const matchesTable = document.getElementById('matchesTable');
    if (matches.length === 0) {
        matchesTable.innerHTML = '<div style="padding: 20px; text-align: center; color: #999;">No matches saved yet</div>';
    } else {
        matchesTable.innerHTML = matches
            .map(match => `
                <div class="match-row">
                    <div class="match-info">
                        <div class="match-score">Score: ${Math.round(match.score)}/100</div>
                        <div class="match-explanation">${match.explanation}</div>
                        <div class="match-time">${new Date(match.timestamp).toLocaleString()}</div>
                    </div>
                    <div class="match-actions">
                        <button class="btn-small" onclick="viewMatch(${match.id})">View</button>
                        <button class="btn-small" onclick="deleteMatch(${match.id})">Delete</button>
                    </div>
                </div>
            `)
            .join('');
    }

    document.getElementById('matchesList').style.display = 'block';
}

async function viewMatch(id) {
    try {
        const response = await fetch(`/api/match/${id}`);
        if (!response.ok) throw new Error('Failed to load match');

        const match = await response.json();

        // Show in modal or expand (simple alert for now)
        const recommendations = match.recommendations.map(r => `• ${r}`).join('\n');
        alert(`Score: ${Math.round(match.score)}/100\n\nExplanation:\n${match.explanation}\n\nRecommendations:\n${recommendations || 'None'}`);
    } catch (error) {
        console.error('Error:', error);
        alert('Error loading match details');
    }
}

async function deleteMatch(id) {
    if (!confirm('Delete this match?')) return;

    try {
        const response = await fetch(`/api/match/${id}`, {
            method: 'DELETE'
        });

        if (!response.ok) throw new Error('Failed to delete match');

        // Reload matches
        loadMatches();
    } catch (error) {
        console.error('Error:', error);
        alert('Error deleting match');
    }
}
