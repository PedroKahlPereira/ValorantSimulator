// static/js/match_results.js

document.addEventListener('DOMContentLoaded', function () {
    const results = JSON.parse(localStorage.getItem('simulationResults'));
    
    if (!results) {
        document.body.innerHTML = '<h1>No results found. Please <a href="/">run a simulation</a> first.</h1>';
        return;
    }

    const params = new URLSearchParams(window.location.search);
    const gameNumber = parseInt(params.get('game'));

    if (results.type === 'single_match' || results.type === 'replay') {
        displaySingleMatch(results);
    } 
    else if (results.type === 'series_results' && gameNumber) {
        displaySeriesGame(results, gameNumber);
    } 
    else {
        document.body.innerHTML = '<h1>Invalid Data. This page is for single match results. Go to <a href="/results/series">series results</a>.</h1>';
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

function displaySingleMatch(results) {
    const { team_a, team_b, final_score, map, winner_name, stats } = results;
    populateMatchData(team_a, team_b, final_score, map, winner_name, stats);
}

function displaySeriesGame(seriesResults, gameNumber) {
    if (!seriesResults.games || gameNumber < 1 || gameNumber > seriesResults.games.length) {
        document.body.innerHTML = '<h1>Error: Invalid game number for this series.</h1>';
        return;
    }
    const gameData = seriesResults.games[gameNumber - 1];
    populateMatchData(
        seriesResults.team_a,
        seriesResults.team_b,
        gameData.final_score,
        gameData.map,
        gameData.winner_name,
        null 
    );
    const newSimLink = document.querySelector('a.btn-primary');
    if (newSimLink) { newSimLink.style.display = 'none'; }
}

function populateMatchData(team_a, team_b, final_score, map, winner_name, stats) {
    document.getElementById('mapName').textContent = map;
    document.getElementById('teamAName').textContent = team_a.name;
    document.getElementById('teamALogo').src = team_a.logo_url;
    document.getElementById('teamAScore').textContent = final_score.split(' - ')[0];
    document.getElementById('teamBName').textContent = team_b.name;
    document.getElementById('teamBLogo').src = team_b.logo_url;
    document.getElementById('teamBScore').textContent = final_score.split(' - ')[1];

    const teamADiv = document.getElementById('teamA');
    const teamBDiv = document.getElementById('teamB');
    if (winner_name === team_a.name) {
        teamADiv.classList.add('winner');
        teamBDiv.classList.add('loser');
    } else {
        teamBDiv.classList.add('winner');
        teamADiv.classList.add('loser');
    }

    const statsContainer = document.getElementById('stats-container');
    if (stats && stats.team_a && stats.team_b) {
        document.getElementById('statsTeamALogo').src = team_a.logo_url;
        document.getElementById('statsTeamAName').textContent = team_a.name;
        document.getElementById('statsTeamBLogo').src = team_b.logo_url;
        document.getElementById('statsTeamBName').textContent = team_b.name;

        document.getElementById('teamAStatsBody').innerHTML = createPlayerRows(stats.team_a);
        document.getElementById('teamBStatsBody').innerHTML = createPlayerRows(stats.team_b);
        
        statsContainer.style.display = 'block';
    } else {
        statsContainer.style.display = 'none';
    }
}

function createPlayerRows(players) {
    if (!players || players.length === 0) return '';
    const sortedPlayers = [...players].sort((a, b) => b.kills - a.kills || a.deaths - b.deaths);
    
    return sortedPlayers.map(p => 
        `<tr>
            <td>${p.name}</td>
            <td>${p.kills}</td>
            <td>${p.deaths}</td>
            <td>${p.assists}</td>
        </tr>`
    ).join('');
}