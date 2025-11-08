// static/js/series_results.js 

document.addEventListener('DOMContentLoaded', function () {
    const resultsData = JSON.parse(localStorage.getItem('simulationResults'));

    if (!resultsData || resultsData.type !== 'series_results') {
        document.querySelector('.results-container').innerHTML = '<h1>No series results found. Please <a href="/">run a series simulation</a> first.</h1>';
        return;
    }

    const { team_a, team_b, series_score, series_winner, games } = resultsData;
    const [scoreA, scoreB] = series_score.split(' - ').map(Number);
    
    document.getElementById('teamAName').textContent = team_a.name;
    document.getElementById('teamALogo').src = team_a.logo_url;
    document.getElementById('teamAScore').textContent = scoreA;

    document.getElementById('teamBName').textContent = team_b.name;
    document.getElementById('teamBLogo').src = team_b.logo_url;
    document.getElementById('teamBScore').textContent = scoreB;

    if (series_winner === team_a.name) {
        document.getElementById('teamA').classList.add('winner');
        document.getElementById('teamB').classList.add('loser');
    } else {
        document.getElementById('teamB').classList.add('winner');
        document.getElementById('teamA').classList.add('loser');
    }

    const detailsContainer = document.getElementById('details-content');
    if (detailsContainer && games) {
        detailsContainer.innerHTML = games.map((game, index) => {
            const gameNumber = index + 1;
            const [gameScoreA, gameScoreB] = game.final_score.split(' - ');
            const winnerSideClass = game.winner_name === team_a.name ? 'team-a-wins' : 'team-b-wins';
            
            return `
                <a href="/results/match?game=${gameNumber}" class="game-detail ${winnerSideClass}">
                    <span class="map-name">MAP: ${game.map}</span>
                    
                    <div class="game-score-container">
                        <img src="${team_a.logo_url}" alt="${team_a.name} logo">
                        <span>${gameScoreA}</span>
                        <span>-</span>
                        <span>${gameScoreB}</span>
                        <img src="${team_b.logo_url}" alt="${team_b.name} logo">
                    </div>

                    <span class="game-winner">WINNER: <strong>${game.winner_name}</strong></span>
                </a>
            `;
        }).join('');
    }
    
    const detailsBtn = document.getElementById('details-btn');
    if (detailsBtn && detailsContainer) {
        detailsBtn.addEventListener('click', () => {
            detailsContainer.classList.toggle('hidden');
            const isHidden = detailsContainer.classList.contains('hidden');
            detailsBtn.textContent = isHidden ? 'Show Details' : 'Hide Details';
        });
    }
    
    const backBtn = document.getElementById('back-btn');
    if (backBtn) {
        // AQUI ESTÁ A CORREÇÃO:
        // Em vez de voltar no histórico, redirecionamos para a página de opções.
        backBtn.addEventListener('click', () => {
            window.location.href = '/options';
        });
    }
});