document.addEventListener('DOMContentLoaded', function () {
    let teamsData = {};
    const team1Select = document.getElementById('team1');
    const team2Select = document.getElementById('team2');
    const mapSelect = document.getElementById('map-select');
    const tournamentSelect = document.getElementById('tournament-select');
    const proceedBtn = document.getElementById('proceed-btn');

    // --- LÓGICA DO CUSTOM SELECT ---
    document.querySelectorAll('.custom-select-wrapper').forEach(wrapper => {
        const trigger = wrapper.querySelector('.custom-select-trigger');
        const options = wrapper.querySelector('.custom-options');
        const hiddenSelect = wrapper.querySelector('.hidden-select');
        const selectedText = trigger.querySelector('.selected-text');
        const selectedLogo = trigger.querySelector('.selected-logo');

        trigger.addEventListener('click', () => {
            document.querySelectorAll('.custom-select-wrapper.open').forEach(openWrapper => {
                if (openWrapper !== wrapper) { openWrapper.classList.remove('open'); }
            });
            wrapper.classList.toggle('open');
        });

        options.querySelectorAll('.custom-option').forEach(option => {
            option.addEventListener('click', () => {
                const value = option.getAttribute('data-value');
                const text = option.querySelector('span').textContent;
                const logoImg = option.querySelector('img');

                selectedText.textContent = text;
                hiddenSelect.value = value;
                
                if (selectedLogo && logoImg) {
                    selectedLogo.src = logoImg.src;
                    selectedLogo.style.display = 'block';
                }
                
                hiddenSelect.dispatchEvent(new Event('change'));
                wrapper.classList.remove('open');
            });
        });
    });
    
    window.addEventListener('click', e => {
        document.querySelectorAll('.custom-select-wrapper').forEach(wrapper => {
            if (!wrapper.contains(e.target)) { wrapper.classList.remove('open'); }
        });
    });
    
    // --- LÓGICA PRINCIPAL ---
    async function fetchData() {
        try {
            const response = await fetch('/api/teams');
            teamsData = await response.json();
            updateTeamDisplay('team1', team1Select.value);
            triggerCustomSelectUpdate(document.querySelector('#team1').closest('.custom-select-wrapper'));

            team2Select.value = Object.keys(teamsData)[1];
            updateTeamDisplay('team2', team2Select.value);
            triggerCustomSelectUpdate(document.querySelector('#team2').closest('.custom-select-wrapper'));
            
            checkProceedButton(); // Checa o estado inicial do botão
        } catch (error) { console.error("Error fetching teams data:", error); }
    }

    function updateTeamDisplay(teamId, selectedValue) {
        if (!teamsData[selectedValue]) return;
        const teamData = teamsData[selectedValue];
        const playersListEl = document.getElementById(`${teamId}Players`);
        const logoDisplayEl = document.getElementById(`${teamId}LogoDisplay`);

        logoDisplayEl.src = teamData.logo_url;
        logoDisplayEl.style.opacity = 1;

        playersListEl.innerHTML = teamData.players.map(player => `
            <div class="player-item">
                <img src="${player.img_url}" alt="${player.name}" class="player-photo-small">
                <div class="player-text">
                    <span class="player-name">${player.name}</span>
                    <span class="player-role">${player.role}</span>
                </div>
            </div>`).join('');
    }
    
    function triggerCustomSelectUpdate(wrapper) {
        const hiddenSelect = wrapper.querySelector('.hidden-select');
        const selectedOption = hiddenSelect.options[hiddenSelect.selectedIndex];
        if (!selectedOption) return;
        
        const text = selectedOption.textContent;
        const selectedLogo = wrapper.querySelector('.selected-logo');
        wrapper.querySelector('.selected-text').textContent = text;
        
        if (selectedLogo) {
            const logoSrc = selectedOption.getAttribute('data-logo');
            if (logoSrc) {
                selectedLogo.src = logoSrc;
                selectedLogo.style.display = 'block';
            }
        }
    }

    function checkProceedButton() {
        // Botão depende de TUDO: dois times DIFERENTES, mapa e torneio.
        if (mapSelect.value && tournamentSelect.value && team1Select.value && team2Select.value && team1Select.value !== team2Select.value) {
            proceedBtn.classList.remove('disabled');
        } else {
            proceedBtn.classList.add('disabled');
        }
    }

    // Adiciona os eventos de 'change' para todos os selects escondidos
    document.querySelectorAll('.hidden-select').forEach(sel => {
        sel.addEventListener('change', checkProceedButton);
    });
    team1Select.addEventListener('change', () => updateTeamDisplay('team1', team1Select.value));
    team2Select.addEventListener('change', () => updateTeamDisplay('team2', team2Select.value));

    // =======================================================
    // MUDANÇA AQUI: O botão agora só salva os dados antes de navegar
    // =======================================================
    proceedBtn.addEventListener('click', (e) => {
        if (proceedBtn.classList.contains('disabled')) {
            e.preventDefault(); // Previne a navegação se o botão estiver desabilitado
            alert("Please select two different teams, a map, and a tournament.");
            return;
        }
        // Apenas salva os dados. A navegação é feita pelo href do <a>.
        sessionStorage.setItem('selectedTeam1', team1Select.value);
        sessionStorage.setItem('selectedTeam2', team2Select.value);
        sessionStorage.setItem('selectedMap', mapSelect.value);
        sessionStorage.setItem('selectedTournament', tournamentSelect.value);
    });

    fetchData();
});