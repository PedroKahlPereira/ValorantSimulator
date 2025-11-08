// static/js/replay.js - VERSÃO CORRIGIDA

document.addEventListener('DOMContentLoaded', function () {
    // --- Cache de Elementos do DOM ---
    const canvas = document.getElementById('replayCanvas');
    const ctx = canvas.getContext('2d');
    const teamANameEl = document.getElementById('teamAName'), teamALogoEl = document.getElementById('teamALogo'), teamAScoreEl = document.getElementById('teamAScore');
    const teamBNameEl = document.getElementById('teamBName'), teamBLogoEl = document.getElementById('teamBLogo'), teamBScoreEl = document.getElementById('teamBScore');
    const roundNumberEl = document.getElementById('roundNumber'), mapNameEl = document.getElementById('mapName');
    const teamAPanelEl = document.getElementById('teamAPanel'), teamBPanelEl = document.getElementById('teamBPanel');
    const killFeedContainerEl = document.getElementById('kill-feed-container');
    const miniMapEl = document.getElementById('miniMap');
    const mapContainerEl = document.getElementById('map-container');
    const freezeBtn = document.getElementById('freezeBtn');

    // --- Variáveis de Estado ---
    let simulationResults = null, currentRoundIndex = 0, currentEventIndex = 0;
    let playerStates = {};
    let isPaused = false, animationTimeout;
    let animationInterval = 1800;

    const MAP_IMAGE_PATHS = { "Ascent": "/static/minimaps/ascent.jpg", "Bind": "/static/minimaps/bind.jpg", "Haven": "/static/minimaps/haven.jpg", "Icebox": "/static/minimaps/icebox.jpg", "Lotus": "/static/minimaps/lotus.jpg" };

    function initializeReplay() {
        try {
            // ====================== AQUI ESTÁ A CORREÇÃO PRINCIPAL ======================
            // Buscamos os dados do localStorage com a chave padronizada 'simulationResults'.
            simulationResults = JSON.parse(localStorage.getItem('simulationResults'));
            // ===========================================================================
            
            // Adicionamos uma verificação extra para garantir que o tipo é 'replay'
            if (!simulationResults || simulationResults.type !== 'replay' || !simulationResults.rounds || simulationResults.rounds.length === 0) {
                throw new Error('Dados de replay inválidos. Volte e inicie uma nova simulação.');
            }
            
            teamANameEl.textContent = simulationResults.team_a.name;
            teamALogoEl.src = simulationResults.team_a.logo_url;
            teamBNameEl.textContent = simulationResults.team_b.name;
            teamBLogoEl.src = simulationResults.team_b.logo_url;
            mapNameEl.textContent = simulationResults.map;

            miniMapEl.onload = () => {
                canvas.width = mapContainerEl.clientWidth;
                canvas.height = mapContainerEl.clientHeight;
                setupRound();
                setTimeout(() => { processNextEvent(); }, 1500);
            };
            miniMapEl.src = MAP_IMAGE_PATHS[simulationResults.map] || '';
        } catch (error) {
            alert(`Falha no Replay: ${error.message}`);
            // Opcional: redirecionar para a home se der erro
            // window.location.href = '/';
        }
    }
    
    function setupRound() {
        const roundData = simulationResults.rounds[currentRoundIndex];
        if (!roundData) return;

        let scoreA = 0, scoreB = 0;
        for(let i = 0; i < currentRoundIndex; i++) { if(simulationResults.rounds[i].round_winner === 'team_a') scoreA++; else scoreB++; }
        teamAScoreEl.textContent = scoreA;
        teamBScoreEl.textContent = scoreB;
        roundNumberEl.textContent = roundData.round_number;

        teamAPanelEl.innerHTML = '';
        teamBPanelEl.innerHTML = '';
        killFeedContainerEl.innerHTML = '';
        currentEventIndex = 0;
        playerStates = {};
        
        const allInitialPlayers = [...roundData.initial_team_a, ...roundData.initial_team_b];
        allInitialPlayers.forEach(p => {
            const isTeamA = roundData.initial_team_a.some(player => player.name === p.name);
            const teamId = isTeamA ? 'team_a' : 'team_b';
            const originalPlayer = simulationResults[teamId].players.find(op => op.name === p.name);
            const panel = isTeamA ? teamAPanelEl : teamBPanelEl;
            panel.innerHTML += createPlayerCard(originalPlayer, p, roundData.round_attacker === teamId ? 'attacker' : 'defender');
            playerStates[p.name] = { x: -100, y: -100, alive: true, team: teamId };
        });
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
    
    function createPlayerCard(originalPlayer, livePlayer, roundRole) {
        const playerNameId = originalPlayer.name.replace(/\s+/g, '-');
        const playerPhoto = originalPlayer.img_url || originalPlayer.agent_icon_url;
        const supportStat = originalPlayer.stats.Support ? `<div class="stat-item"><span class="label">SUPPORT</span><span class="value">${originalPlayer.stats.Support}</span></div>` : '';
        return `<div class="player-card ${roundRole}" id="player-card-${playerNameId}"><div class="player-photo-wrapper"><img src="${playerPhoto}" class="player-photo"><div class="health-bar-container"><div class="health-bar" id="health-bar-${playerNameId}" style="width: 100%;"></div></div></div><div class="player-info"><span class="player-name">${originalPlayer.name}</span><span class="player-role">${originalPlayer.role}</span></div><div class="player-stats-details"><div class="stat-item"><span class="label">AIM</span><span class="value">${originalPlayer.stats.Aim}</span></div><div class="stat-item"><span class="label">HS%</span><span class="value">${originalPlayer.stats.HS}</span></div><div class="stat-item"><span class="label">CLUTCH</span><span class="value">${originalPlayer.stats.Clutch}</span></div>${supportStat}</div><div class="live-stats"><span class="kda-text" id="kda-text-${playerNameId}">${livePlayer.kills}/${livePlayer.deaths}/${livePlayer.assists}</span><span class="economy-text" id="economy-text-${playerNameId}">$${livePlayer.credits}</span></div><div class="player-weapon"><img src="/static/icons/${livePlayer.weapon.id}.png" class="weapon-icon" id="weapon-icon-${playerNameId}"></div></div>`;
    }

    function drawConfrontation(players, victimName = null) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const teamA_Color = '#4CAF50';
        const teamB_Color = '#F44336';

        players.forEach(playerName => {
            const state = playerStates[playerName];
            if (!state) return;
            const drawX = state.x * canvas.width;
            const drawY = state.y * canvas.height;
            
            ctx.fillStyle = (state.team === 'team_a') ? teamA_Color : teamB_Color;
            ctx.globalAlpha = (playerName === victimName) ? 0.4 : 1.0;
            
            ctx.beginPath();
            ctx.arc(drawX, drawY, 8, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = 'white';
            ctx.lineWidth = 2;
            ctx.stroke();
            
            ctx.globalAlpha = 1.0;
            ctx.fillStyle = 'white';
            ctx.textAlign = 'center';
            ctx.font = 'bold 12px "Roboto Condensed"';
            ctx.shadowColor = "black";
            ctx.shadowBlur = 4;
            ctx.fillText(playerName, drawX, drawY - 15);
        });
        ctx.shadowBlur = 0;
    }

    function processNextEvent() {
        clearTimeout(animationTimeout);
        if (isPaused) return;

        const round = simulationResults.rounds[currentRoundIndex];
        if (!round || currentEventIndex >= round.timeline.length) {
            setTimeout(() => {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                if (currentRoundIndex < simulationResults.rounds.length) {
                    if (round.round_winner === 'team_a') teamAScoreEl.textContent = parseInt(teamAScoreEl.textContent) + 1;
                    else teamBScoreEl.textContent = parseInt(teamBScoreEl.textContent) + 1;
                }
                currentRoundIndex++;
                if (simulationResults.rounds[currentRoundIndex]) { 
                    setupRound();
                    setTimeout(processNextEvent, 1500);
                } else { 
                    alert('Replay Finalizado!'); 
                }
            }, 3000);
            return;
        }

        const event = round.timeline[currentEventIndex];
        
        if (event.type === 'damage') {
            const { attackerName, victimName, attackerPosition, victimPosition } = event;

            if(attackerPosition) playerStates[attackerName].x = attackerPosition.x;
            if(attackerPosition) playerStates[attackerName].y = attackerPosition.y;
            if(victimPosition) playerStates[victimName].x = victimPosition.x;
            if(victimPosition) playerStates[victimName].y = victimPosition.y;

            drawConfrontation([attackerName, victimName]);
            
            const healthBar = document.getElementById(`health-bar-${victimName.replace(/\s+/g, '-')}`);
            if(healthBar) {
                setTimeout(() => {
                    const health = event.victimState.health;
                    healthBar.style.width = `${health}%`;

                    healthBar.classList.remove('low-health', 'critical-health');
                    if (health <= 20) {
                        healthBar.classList.add('critical-health');
                    } else if (health <= 50) {
                        healthBar.classList.add('low-health');
                    }
                }, 400);
            }
        }
        else if (event.type === 'kill') {
            const { killerName, victimName, weaponId, final_states, killerPosition, victimPosition } = event;

            playerStates[victimName].alive = false;
            if(killerPosition) playerStates[killerName].x = killerPosition.x;
            if(killerPosition) playerStates[killerName].y = killerPosition.y;
            if(victimPosition) playerStates[victimName].x = victimPosition.x;
            if(victimPosition) playerStates[victimName].y = victimPosition.y;

            drawConfrontation([killerName, victimName], victimName);

            const killerRole = (playerStates[killerName].team === round.round_attacker) ? 'attacker' : 'defender';
            const killerData = simulationResults[playerStates[killerName].team].players.find(p => p.name === killerName);
            const victimData = simulationResults[playerStates[victimName].team].players.find(p => p.name === victimName);
            const killFeedEntry = document.createElement('div');
            killFeedEntry.className = `kill-feed-entry ${killerRole}`;
            killFeedEntry.innerHTML = `<div class="participant killer"><img src="${killerData.agent_icon_url}" class="agent-icon-killfeed"><span class="player-name">${killerName}</span></div><div class="weapon-display"><img src="/static/icons/${weaponId}.png" class="weapon-icon killfeed"></div><div class="participant victim"><span class="player-name">${victimName}</span><img src="${victimData.agent_icon_url}" class="agent-icon-killfeed"></div>`;
            killFeedContainerEl.prepend(killFeedEntry);

            const victimCard = document.getElementById(`player-card-${victimName.replace(/\s+/g, '-')}`);
            if (victimCard) victimCard.classList.add('dead');

            setTimeout(() => {
                for (const [playerName, state] of Object.entries(final_states)) {
                    const nameId = playerName.replace(/\s+/g, '-');
                    const healthBar = document.getElementById(`health-bar-${nameId}`);
                    const kdaEl = document.getElementById(`kda-text-${nameId}`);
                    const ecoEl = document.getElementById(`economy-text-${nameId}`);
                    
                    if (healthBar) {
                        const health = state.health;
                        healthBar.style.width = `${health}%`;

                        healthBar.classList.remove('low-health', 'critical-health');
                        if (health <= 20) {
                            healthBar.classList.add('critical-health');
                        } else if (health <= 50) {
                            healthBar.classList.add('low-health');
                        }
                    }
                    if (kdaEl) kdaEl.textContent = `${state.k}/${state.d}/${state.a}`;
                    if (ecoEl) ecoEl.textContent = `$${state.credits}`;
                }
            }, 400);
        }
        
        currentEventIndex++;
        const delay = (event.type === 'kill') ? animationInterval * 1.5 : animationInterval;
        animationTimeout = setTimeout(processNextEvent, delay);
    }
    
    // --- Controles do Replay ---
    document.getElementById('speedBtn1').addEventListener('click', () => { animationInterval = 1800; });
    document.getElementById('speedBtn4').addEventListener('click', () => { animationInterval = 600; });
    freezeBtn.addEventListener('click', () => { isPaused = !isPaused; freezeBtn.textContent = isPaused ? 'RESUME' : 'PAUSE'; if (!isPaused) processNextEvent(); });
    document.getElementById('nextRoundBtn').addEventListener('click', () => {
        if (isPaused) return;
        clearTimeout(animationTimeout);
        currentEventIndex = Infinity;
        processNextEvent();
    });

    // --- Botão de Voltar (Consistência) ---
    // Adicionamos um ID 'backBtn' ao botão no HTML
    const backBtn = document.getElementById('backBtn');
    if (backBtn) {
        backBtn.addEventListener('click', () => {
            window.location.href = '/options'; // Leva para a página de opções
        });
    }

    initializeReplay();
});