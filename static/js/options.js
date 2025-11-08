// static/js/options.js

document.addEventListener('DOMContentLoaded', function () {
    // Pega as seleções que vieram da página inicial
    const team1Id = sessionStorage.getItem('selectedTeam1');
    const team2Id = sessionStorage.getItem('selectedTeam2');
    const map = sessionStorage.getItem('selectedMap');
    const tournament = sessionStorage.getItem('selectedTournament');

    const instantMatchBtn = document.getElementById('instant-match-btn');
    const seriesBtn = document.getElementById('series-btn');
    const replayBtn = document.getElementById('replay-btn');
    const changeSelectionsBtn = document.getElementById('change-selections-btn');
    const loadingOverlay = document.getElementById('loading-overlay');
    
    // Se não houver times selecionados, volta para o início
    if (!team1Id || !team2Id) {
        window.location.href = '/';
        return;
    }

    // Preenche as informações na tela
    document.getElementById('mapName').textContent = map;
    fetch('/api/teams').then(res => res.json()).then(teams => {
        if (teams[team1Id] && teams[team2Id]) {
            document.getElementById('team1Name').textContent = teams[team1Id].name;
            document.getElementById('team1Logo').src = teams[team1Id].logo_url;
            document.getElementById('team2Name').textContent = teams[team2Id].name;
            document.getElementById('team2Logo').src = teams[team2Id].logo_url;
        } else {
            // Se os times não forem encontrados, volta para o início
            window.location.href = '/';
        }
    });

    async function handleSimulation(mode) {
        if (loadingOverlay) loadingOverlay.classList.remove('hidden');

        const body = {
            team_1: team1Id, team_2: team2Id, map: map,
            simulation_mode: mode, tournament: tournament
        };

        try {
            const response = await fetch('/simulate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            if (!response.ok) throw new Error(`Server error: ${response.statusText}`);
            
            const results = await response.json();

            // AQUI ESTÁ A CORREÇÃO PRINCIPAL:
            // Salva TODOS os resultados com a mesma chave no localStorage.
            localStorage.setItem('simulationResults', JSON.stringify(results));

            // Apenas redireciona para a página correta
            if (results.type === 'replay') {
                window.location.href = '/replay';
            } else if (results.type === 'series_results') {
                window.location.href = '/results/series';
            } else {
                window.location.href = '/results/match';
            }

        } catch (error) {
            console.error('Simulation Failed:', error);
            alert('An error occurred during the simulation.');
            if (loadingOverlay) loadingOverlay.classList.add('hidden');
        }
    }

    instantMatchBtn.addEventListener('click', () => handleSimulation('single_match'));
    seriesBtn.addEventListener('click', () => handleSimulation('series'));
    replayBtn.addEventListener('click', () => handleSimulation('replay'));
    
    if (changeSelectionsBtn) {
        changeSelectionsBtn.addEventListener('click', () => { window.location.href = '/'; });
    }
});