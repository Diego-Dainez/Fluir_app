/**
 * Fluir - Painel Administrativo
 * Script extraido de admin.html para arquivo separado
 */

function escapeHtml(str) {
    if (str == null) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// STATE
let surveys = [];
let currentSurveyId = null;
let dashboardData = null;
let radarChart = null;
let barChart = null;
let pendingDeleteSurveyId = null;
const ADMIN_CODE = sessionStorage.getItem('fluir_admin_code');

if (!ADMIN_CODE) window.location.href = '/';

async function init() {
    await loadSurveys();
    if (surveys.length > 0) {
        renderSurveysList();
        const storedId = sessionStorage.getItem('fluir_selected_survey');
        if (storedId && surveys.find(s => s.id === storedId)) {
            selectSurvey(storedId, false);
        }
    } else {
        document.getElementById('emptyState').classList.remove('hidden');
    }
}

async function loadSurveys() {
    try {
        const res = await fetch(`/api/admin/surveys?admin_code=${ADMIN_CODE}`);
        if (res.ok) surveys = await res.json();
    } catch (err) { console.error(err); }
}

function switchTab(tabId) {
    closeSidebarIfMobile();
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));

    document.getElementById(`tab-${tabId}`).classList.add('active');
    document.querySelector(`.nav-link[data-tab="${tabId}"]`).classList.add('active');

    const actions = document.getElementById('headerActions');
    if (tabId === 'surveys') {
        document.getElementById('pageTitle').textContent = 'Pesquisas';
        actions.innerHTML = '<button class="btn btn-primary" onclick="openNewSurveyModal()">+ Nova Pesquisa</button>';
    } else if (tabId === 'dashboard') {
        document.getElementById('pageTitle').textContent = 'Dashboard';
        if (currentSurveyId) {
            actions.innerHTML = `
                <button class="btn btn-export-ppt" onclick="exportReport('${currentSurveyId}', 'pptx')">PPT</button>
                <button class="btn btn-export-excel" onclick="exportReport('${currentSurveyId}', 'excel')">Excel</button>
            `;
            loadDashboard(currentSurveyId);
        }
    } else if (tabId === 'responses') {
        document.getElementById('pageTitle').textContent = 'Respostas Individuais';
        actions.innerHTML = '';
        if (!currentSurveyId) {
            renderTransposedTable(null);
        } else if (dashboardData && dashboardData.company_name) {
            renderTransposedTable(dashboardData);
        } else {
            renderTransposedTable({ loading: true });
            loadDashboard(currentSurveyId);
        }
    }
}

function renderSurveysList() {
    const container = document.getElementById('surveysList');
    container.innerHTML = surveys.map(s => `
        <div class="admin-card" onclick="selectSurveyAndGo('${escapeHtml(s.id)}')" style="cursor:pointer; border-left: 4px solid ${s.is_active ? 'var(--green)' : 'var(--red)'}">
            <div class="flex justify-between items-center mb-2">
                <div class="flex items-center gap-2" style="flex:1; min-width:0;">
                    <h3 id="company-name-${escapeHtml(s.id)}" style="margin:0; font-size: 1.1rem; color: var(--primary-800);">${escapeHtml(s.company_name)}</h3>
                    <button class="btn btn-ghost btn-sm" style="padding:2px 6px; font-size:0.75rem;" onclick="event.stopPropagation(); startEditCompanyName('${escapeHtml(s.id)}')" title="Editar nome">Editar</button>
                </div>
                <div class="toggle-switch" onclick="event.stopPropagation(); toggleSurveyActive('${escapeHtml(s.id)}', ${s.is_active})">
                    <input type="checkbox" ${s.is_active ? 'checked' : ''}>
                    <span class="toggle-slider"></span>
                </div>
            </div>
            <div class="text-muted" style="font-size: 0.9rem; margin-bottom: 12px;">
                Criada em: ${new Date(s.created_at).toLocaleDateString()}
            </div>
            <div class="flex justify-between items-center">
                <span class="badge ${s.respondent_count > 0 ? 'badge-primary' : 'badge-secondary'}">
                    ${s.respondent_count} respondentes
                </span>
                <span style="font-size: 0.8rem; font-family:var(--font-mono); background: var(--bg-hover); padding: 4px 8px; border-radius: 4px;">
                    ${escapeHtml(s.code)}
                </span>
            </div>
            <div class="flex gap-2 mt-3" onclick="event.stopPropagation();">
                <button class="btn btn-outline btn-sm" onclick="event.stopPropagation(); showQrModal('${escapeHtml(s.id)}')">Compartilhar</button>
                <button class="btn btn-ghost btn-sm" style="color:var(--red);" onclick="event.stopPropagation(); confirmDeleteSurvey('${escapeHtml(s.id)}')">Excluir</button>
            </div>
        </div>
    `).join('');
}

async function startEditCompanyName(id) {
    const s = surveys.find(x => x.id === id);
    if (!s) return;
    const h3 = document.getElementById('company-name-' + id);
    if (!h3 || h3.querySelector('input')) return;
    const parent = h3.parentElement;
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'admin-input';
    input.style = 'font-size:1.1rem; padding:4px 8px; width:100%;';
    input.value = s.company_name;
    input.onblur = () => saveCompanyName(id, input, h3);
    input.onkeydown = (e) => { if (e.key === 'Enter') input.blur(); if (e.key === 'Escape') { input.value = s.company_name; input.replaceWith(h3); } };
    h3.replaceWith(input);
    input.focus();
}

async function saveCompanyName(id, input, origH3) {
    const newName = input.value.trim();
    const s = surveys.find(x => x.id === id);
    if (!s || !newName || newName === s.company_name) { input.replaceWith(origH3); return; }
    try {
        const res = await fetch('/api/admin/surveys/' + id + '/settings?admin_code=' + ADMIN_CODE, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ company_name: newName })
        });
        if (res.ok) {
            s.company_name = newName;
            origH3.textContent = newName;
            showToast('Nome atualizado.', 'success');
        }
    } catch (e) { console.error(e); }
    input.replaceWith(origH3);
}

function confirmDeleteSurvey(id) {
    const s = surveys.find(x => x.id === id);
    const companyName = s ? s.company_name : 'esta pesquisa';
    pendingDeleteSurveyId = id;
    document.getElementById('deleteConfirmMessage').textContent =
        'Tem certeza que deseja excluir a pesquisa "' + companyName + '"? Esta acao nao pode ser desfeita.';
    document.getElementById('deleteConfirmModal').classList.add('show');
}

function closeDeleteConfirmModal() {
    pendingDeleteSurveyId = null;
    document.getElementById('deleteConfirmModal').classList.remove('show');
}

async function executeDeleteSurvey() {
    const id = pendingDeleteSurveyId;
    if (!id) return;
    closeDeleteConfirmModal();
    try {
        const res = await fetch('/api/admin/surveys/delete?survey_id=' + encodeURIComponent(id) + '&admin_code=' + encodeURIComponent(ADMIN_CODE), { method: 'POST' });
        if (res.ok) {
            showToast('Pesquisa excluida.', 'success');
            if (currentSurveyId === id) {
                currentSurveyId = null;
                dashboardData = null;
                switchTab('surveys');
            }
            await loadSurveys();
            renderSurveysList();
        } else {
            const errText = await res.text();
            let msg = 'Erro ao excluir.';
            try {
                const errJson = JSON.parse(errText);
                if (errJson.detail) msg = (Array.isArray(errJson.detail) ? errJson.detail[0]?.msg : errJson.detail) || msg;
            } catch (_) {}
            showToast(msg, 'error');
        }
    } catch (e) { console.error(e); showToast('Erro ao excluir.', 'error'); }
}

async function toggleSurveyActive(id, currentStatus) {
    try {
        const res = await fetch(`/api/admin/surveys/${id}/settings?admin_code=${ADMIN_CODE}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ is_active: !currentStatus })
        });
        if (res.ok) {
            showToast('Status atualizado!', 'success');
            await loadSurveys();
            renderSurveysList();
        }
    } catch (e) { console.error(e); }
}

function selectSurveyAndGo(id) {
    selectSurvey(id, true);
}

function selectSurvey(id, navigate = true) {
    currentSurveyId = id;
    sessionStorage.setItem('fluir_selected_survey', id);

    document.getElementById('nav-dashboard').style.display = 'flex';
    document.getElementById('nav-responses').style.display = 'flex';

    if (navigate) switchTab('dashboard');
}

async function loadDashboard(id) {
    try {
        document.getElementById('recsContent').innerHTML = '<p class="text-muted">Gerando análise com IA...</p>';

        const res = await fetch(`/api/admin/surveys/${id}/dashboard?admin_code=${ADMIN_CODE}`);
        if (!res.ok) return;
        dashboardData = await res.json();

        renderKPIs(dashboardData.kpis);
        renderRecommendationsConsolidated(dashboardData.recommendations_prose, dashboardData.recommendations);
        renderCharts(dashboardData);
        renderTransposedTable(dashboardData);
    } catch (err) { console.error(err); }
}

function renderKPIs(kpis) {
    const container = document.getElementById('kpiGrid');
    container.innerHTML = Object.values(kpis).map(k => `
        <div class="kpi-card ${escapeHtml(k.color)}">
            <div class="kpi-label">${escapeHtml(k.label)}</div>
            <div class="kpi-value ${escapeHtml(k.color)}">${escapeHtml(String(k.value))}</div>
            <div class="kpi-status">${escapeHtml(k.status)}</div>
        </div>
    `).join('');
}

function renderRecommendationsConsolidated(recommendationsProse, structuredRecs) {
    const container = document.getElementById('recsContent');
    const prose = recommendationsProse || {};

    const imediata = (prose.imediata || '').trim();
    const curto = (prose.curto_prazo || '').trim();
    const medio = (prose.medio_prazo || '').trim();

    if (!imediata && !curto && !medio && structuredRecs && structuredRecs.length > 0) {
        const labels = { imediata: 'Acoes imediatas', curto: 'Curto prazo', medio: 'Medio prazo' };
        const byPriority = { imediata: [], curto: [], medio: [] };
        structuredRecs.forEach(r => {
            const p = (r.priority || 'medio').toLowerCase();
            const key = p.includes('imediat') ? 'imediata' : p.includes('curto') ? 'curto' : 'medio';
            if (byPriority[key]) byPriority[key].push(r);
        });
        let html = '';
        ['imediata', 'curto', 'medio'].forEach(k => {
            const items = byPriority[k];
            if (items.length) {
                html += `<div class="recs-section"><div class="recs-section-title ${k}">${escapeHtml(labels[k])}</div>`;
                items.forEach(r => {
                    const t = (r.title || '').trim();
                    const d = (r.description || '').trim();
                    html += `<p class="recs-text">${escapeHtml(t)}${d ? ': ' + escapeHtml(d) : ''}</p>`;
                });
                html += '</div>';
            }
        });
        container.innerHTML = html || '<p class="text-muted">Nenhuma recomendacao gerada.</p>';
        return;
    }

    if (!imediata && !curto && !medio) {
        container.innerHTML = '<p class="text-muted">Nenhuma recomendacao gerada. Complete a pesquisa com respondentes para obter analise.</p>';
        return;
    }

    let html = '';

    if (imediata) {
        html += `<div class="recs-section">
            <div class="recs-section-title imediata">Acoes de aplicacao imediata</div>
            <p class="recs-text">${escapeHtml(imediata)}</p>
        </div>`;
    }
    if (curto) {
        html += `<div class="recs-section">
            <div class="recs-section-title curto">Acoes de curto prazo</div>
            <p class="recs-text">${escapeHtml(curto)}</p>
        </div>`;
    }
    if (medio) {
        html += `<div class="recs-section">
            <div class="recs-section-title medio">Acoes de medio prazo</div>
            <p class="recs-text">${escapeHtml(medio)}</p>
        </div>`;
    }

    container.innerHTML = html;
}

function renderCharts(data) {
    const dimTbody = document.querySelector('#dimensionsTable tbody');
    if (!data || !data.dim_scores || data.dim_scores.length === 0) {
        if (dimTbody) dimTbody.innerHTML = '<tr><td colspan="6" class="text-muted" style="text-align:center; padding:24px;">Nenhum dado disponivel.</td></tr>';
        return;
    }

    const catMap = {};
    data.dim_scores.forEach(d => {
        const cat = d.category;
        if (!catMap[cat]) catMap[cat] = { sum: 0, count: 0, name: cat, type: d.type };
        catMap[cat].sum += d.score;
        catMap[cat].count++;
    });

    const LOWER = 2.33, UPPER = 3.66;
    const getCatStatus = (avg, type) => {
        if (type === 'risk') return avg < LOWER ? 'green' : avg > UPPER ? 'red' : 'yellow';
        return avg > UPPER ? 'green' : avg < LOWER ? 'red' : 'yellow';
    };
    const statusColors = { green: '#6B9F7E', yellow: '#D4A843', red: '#C46B6B' };

    const radarLabels = Object.keys(catMap);
    const radarValues = radarLabels.map(k => parseFloat((catMap[k].sum / catMap[k].count).toFixed(2)));
    const radarPointColors = radarLabels.map(k => {
        const avg = catMap[k].sum / catMap[k].count;
        return statusColors[getCatStatus(avg, catMap[k].type)];
    });

    const ctxRadar = document.getElementById('radarChart').getContext('2d');
    if (radarChart) radarChart.destroy();
    radarChart = new Chart(ctxRadar, {
        type: 'radar',
        data: {
            labels: radarLabels,
            datasets: [{
                label: 'Media por Categoria',
                data: radarValues,
                backgroundColor: 'rgba(107, 130, 168, 0.15)',
                borderColor: '#6B82A8',
                pointBackgroundColor: radarPointColors,
                pointBorderColor: radarPointColors,
                pointBorderWidth: 2
            }]
        },
        options: {
            maintainAspectRatio: false,
            scales: {
                r: {
                    min: 0,
                    max: 5,
                    ticks: { display: false, font: { size: 12 } },
                    pointLabels: { font: { size: 13 } }
                }
            },
            plugins: { legend: { display: false } }
        }
    });

    const labels26 = data.dim_scores.map(d => d.name);
    const values26 = data.dim_scores.map(d => d.score);
    const colors26 = data.dim_scores.map(d => {
        if (d.status === 'green') return '#6B9F7E';
        if (d.status === 'yellow') return '#D4A843';
        return '#C46B6B';
    });

    const ctxBar = document.getElementById('barChart').getContext('2d');
    if (barChart) barChart.destroy();
    barChart = new Chart(ctxBar, {
        type: 'bar',
        data: {
            labels: labels26,
            datasets: [{
                label: 'Score',
                data: values26,
                backgroundColor: colors26,
                borderRadius: 4
            }]
        },
        options: {
            indexAxis: 'y',
            scales: {
                x: { min: 0, max: 5, ticks: { font: { size: 13 } } },
                y: { ticks: { font: { size: 13 }, autoSkip: false } }
            },
            plugins: { legend: { display: false } },
            maintainAspectRatio: false
        }
    });

    if (dimTbody) {
        const statusLabels = { green: 'Favoravel', yellow: 'Atencao', red: 'Critico' };
        dimTbody.innerHTML = (data.dim_scores || []).map((d, i) => {
            const tipo = d.type === 'risk' ? 'Risco' : 'Recurso';
            const statusLabel = statusLabels[d.status] || '';
            const bg = d.status === 'green' ? 'var(--sage-100)' : d.status === 'yellow' ? 'var(--yellow-bg)' : 'var(--red-bg)';
            return `<tr><td>${i + 1}</td><td><strong>${escapeHtml(d.name)}</strong></td><td style="text-align:center">${d.score.toFixed(2)}</td><td style="background:${bg}">${escapeHtml(statusLabel)}</td><td>${escapeHtml(tipo)}</td><td class="text-muted">${escapeHtml(d.category)}</td></tr>`;
        }).join('');
    }
}

function renderTransposedTable(data) {
    const table = document.getElementById('responsesTable');
    if (!table) return;
    const thead = table.querySelector('thead tr');
    const tbody = table.querySelector('tbody');
    if (!thead || !tbody) return;

    thead.innerHTML = '<th>Dimensao</th><th>Categoria</th><th>Media</th>';
    tbody.innerHTML = '';

    if (!data) {
        const tr = document.createElement('tr');
        tr.innerHTML = '<td colspan="3" class="text-muted" style="text-align:center; padding:24px;">Selecione uma pesquisa no Dashboard primeiro.</td>';
        tbody.appendChild(tr);
        return;
    }
    if (data.loading) {
        const tr = document.createElement('tr');
        tr.innerHTML = '<td colspan="3" class="text-muted" style="text-align:center; padding:24px;">Carregando respostas...</td>';
        tbody.appendChild(tr);
        return;
    }
    if (!data.respondents || data.respondents.length === 0) {
        const tr = document.createElement('tr');
        tr.innerHTML = '<td colspan="3" class="text-muted" style="text-align:center; padding:24px;">Nenhum respondente nesta pesquisa.</td>';
        tbody.appendChild(tr);
        return;
    }

    const padLen = Math.max(3, String(data.respondents.length).length);
    data.respondents.forEach((r, i) => {
        const th = document.createElement('th');
        th.textContent = 'R_' + String(i + 1).padStart(padLen, '0');
        th.style.textAlign = 'center';
        th.title = 'Respondente ' + (i + 1) + (r.display_id ? ' (ID: ' + r.display_id + ')' : '');
        thead.appendChild(th);
    });

    if (!data.dim_scores || data.dim_scores.length === 0) {
        const tr = document.createElement('tr');
        tr.innerHTML = '<td colspan="' + (3 + data.respondents.length) + '" class="text-muted" style="text-align:center; padding:24px;">Dados de dimensoes indisponiveis.</td>';
        tbody.appendChild(tr);
        return;
    }
    data.dim_scores.forEach(dim => {
        const tr = document.createElement('tr');

        tr.innerHTML = `
            <td><strong>${escapeHtml(dim.name)}</strong></td>
            <td class="text-muted" style="font-size:0.8rem">${escapeHtml(dim.category)}</td>
            <td class="score-cell" style="background:${getStatusColor(dim.status, true)}">${escapeHtml(String(dim.score.toFixed(1)))}</td>
        `;

        data.respondents.forEach(resp => {
            const score = resp.scores[dim.dimension_id];
            const scoreVal = score !== undefined ? score.toFixed(1) : '-';
            const status = resp.statuses ? resp.statuses[dim.dimension_id] : 'yellow';

            const td = document.createElement('td');
            td.className = 'score-cell';
            if (score !== undefined) {
                td.textContent = scoreVal;
                td.style.backgroundColor = getStatusColor(status, true);
            } else {
                td.textContent = '-';
            }
            tr.appendChild(td);
        });

        tbody.appendChild(tr);
    });
}

function getStatusColor(status, isBg) {
    const map = {
        green: isBg ? 'var(--sage-100)' : 'var(--green)',
        yellow: isBg ? 'var(--yellow-bg)' : 'var(--yellow)',
        red: isBg ? 'var(--red-bg)' : 'var(--red)'
    };
    return map[status] || 'transparent';
}

function showToast(msg, type = 'info') {
    const el = document.getElementById('toast');
    el.className = `toast ${type}`;
    document.getElementById('toastMsg').textContent = msg;
    el.classList.remove('hidden');
    setTimeout(() => el.classList.add('hidden'), 3000);
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const isMobile = window.innerWidth <= 768;
    if (sidebar.classList.contains('open')) {
        sidebar.classList.remove('open');
        document.body.classList.add('sidebar-closed');
        if (isMobile) {
            overlay.classList.add('hidden');
            overlay.setAttribute('aria-hidden', 'true');
        }
    } else {
        sidebar.classList.add('open');
        document.body.classList.remove('sidebar-closed');
        if (isMobile) {
            overlay.classList.remove('hidden');
            overlay.setAttribute('aria-hidden', 'false');
        }
    }
}

function closeSidebarIfMobile() {
    if (window.innerWidth <= 768) {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebarOverlay');
        sidebar.classList.remove('open');
        document.body.classList.remove('sidebar-closed');
        overlay.classList.add('hidden');
        overlay.setAttribute('aria-hidden', 'true');
    }
}

window.addEventListener('resize', function () {
    if (window.innerWidth > 768) {
        const sidebar = document.getElementById('sidebar');
        if (sidebar.classList.contains('open')) {
            document.body.classList.remove('sidebar-closed');
        } else {
            document.body.classList.add('sidebar-closed');
        }
        document.getElementById('sidebarOverlay').classList.add('hidden');
    } else {
        document.body.classList.remove('sidebar-closed');
    }
});

function logout() {
    sessionStorage.clear();
    window.location.href = '/';
}

function openNewSurveyModal() {
    document.getElementById('newSurveyModal').classList.add('show');
    document.getElementById('newCompanyName').focus();
}

function closeModal(id) {
    document.getElementById(id).classList.remove('show');
}

document.getElementById('newSurveyForm').onsubmit = async (e) => {
    e.preventDefault();
    const name = document.getElementById('newCompanyName').value;
    try {
        const res = await fetch('/api/admin/surveys', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ company_name: name, admin_code: ADMIN_CODE })
        });
        if (res.ok) {
            closeModal('newSurveyModal');
            showToast('Pesquisa criada!', 'success');
            init();
        }
    } catch (e) { console.error(e); }
};

init();

async function showQrModal(id) {
    try {
        const res = await fetch(`/api/admin/surveys/${id}/qrcode?admin_code=${ADMIN_CODE}&base_url=${window.location.origin}`);
        const data = await res.json();
        document.getElementById('qrImage').src = data.qr_base64;
        document.getElementById('qrUrl').textContent = data.survey_url;
        document.getElementById('qrModal').classList.add('show');
    } catch (e) { console.error(e); }
}

async function copyLink() {
    const text = document.getElementById('qrUrl').textContent;
    await navigator.clipboard.writeText(text);
    showToast('Link copiado!', 'success');
}

function exportReport(id, type) {
    window.open(`/api/admin/surveys/${id}/export/${type}?admin_code=${ADMIN_CODE}`, '_blank');
}
