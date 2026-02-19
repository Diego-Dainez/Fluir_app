/**
 * Fluir - Pesquisa de Bem-Estar
 * Script extraido de survey.html para arquivo separado
 */

const surveyCode = window.location.pathname.split('/').pop();
let pages = [];
let totalQuestions = 0;
let currentPage = -1;
let responses = {};

async function init() {
    try {
        const res = await fetch(`/api/survey/${surveyCode}/questions`);
        if (!res.ok) {
            document.body.innerHTML = '<div style="text-align:center;padding:80px 20px;"><h2>Pesquisa nao encontrada</h2><p>Esta pesquisa pode ter sido encerrada.</p></div>';
            return;
        }
        pages = await res.json();
        totalQuestions = pages.reduce((n, p) => n + p.questions.length, 0);
        buildPages();
    } catch (err) { console.error(err); }
}

function buildPages() {
    const container = document.getElementById('pagesContainer');
    pages.forEach((page, idx) => {
        const div = document.createElement('div');
        div.className = 'survey-page';
        div.id = `page-${idx}`;
        div.innerHTML = `
            <div class="page-header" style="background: ${page.color}">
                <h2>${page.name}</h2>
                <p>${page.description}</p>
                <span class="page-counter">Secao ${idx + 1} de ${pages.length}</span>
            </div>
            <div class="page-questions">
                ${page.questions.map(q => buildQuestion(q)).join('')}
            </div>
            <div class="page-nav">
                ${idx > 0 ? '<button class="btn btn-secondary" onclick="prevPage()">Anterior</button>' : '<div></div>'}
                ${idx < pages.length - 1
                    ? `<button class="btn btn-primary" id="nextBtn-${idx}" onclick="nextPage()">Proximo</button>`
                    : `<button class="btn btn-accent btn-lg" id="submitBtn" onclick="submitSurvey()">Enviar Pesquisa</button>`
                }
            </div>
        `;
        container.appendChild(div);
    });
}

function buildQuestion(q) {
    const labels = q.scale_labels;
    return `
        <div class="question-card" id="qcard-${q.id}">
            <div class="question-text">
                <span class="question-number">${q.id}</span>
                ${q.text}
            </div>
            <div class="likert-scale">
                ${[1, 2, 3, 4, 5].map(v => `
                    <div class="likert-option">
                        <input type="radio" id="q${q.id}_${v}" name="q_${q.id}" value="${v}"
                               onchange="setResponse(${q.id}, ${v})">
                        <label for="q${q.id}_${v}">
                            <span class="likert-value">${v}</span>
                            <span class="likert-label">${labels[v]}</span>
                        </label>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function startSurvey() {
    document.getElementById('introSection').classList.add('hidden');
    document.getElementById('progressBar').classList.remove('hidden');
    currentPage = 0;
    showPage(0);
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showPage(idx) {
    document.querySelectorAll('.survey-page').forEach(p => p.classList.remove('active'));
    const page = document.getElementById(`page-${idx}`);
    if (page) page.classList.add('active');
    currentPage = idx;
    updateProgress();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function nextPage() {
    const pageQuestions = pages[currentPage].questions;
    const unanswered = pageQuestions.filter(q => !responses[q.id]);
    if (unanswered.length > 0) {
        unanswered.forEach(q => {
            const card = document.getElementById(`qcard-${q.id}`);
            card.style.boxShadow = '0 0 0 2px var(--red)';
            setTimeout(() => card.style.boxShadow = '', 2000);
        });
        document.getElementById(`qcard-${unanswered[0].id}`).scrollIntoView({ behavior: 'smooth', block: 'center' });
        return;
    }
    if (currentPage < pages.length - 1) showPage(currentPage + 1);
}

function prevPage() {
    if (currentPage > 0) showPage(currentPage - 1);
}

function setResponse(qId, value) {
    responses[qId] = value;
    const card = document.getElementById(`qcard-${qId}`);
    card.classList.add('answered');
    updateProgress();
}

function updateProgress() {
    const answered = Object.keys(responses).length;
    const pct = totalQuestions ? Math.round((answered / totalQuestions) * 100) : 0;
    document.getElementById('progressLabel').textContent = `Secao ${currentPage + 1} de ${pages.length}`;
    document.getElementById('progressPercent').textContent = `${answered}/${totalQuestions} (${pct}%)`;
    document.getElementById('progressFill').style.width = `${pct}%`;
}

async function submitSurvey() {
    const answered = Object.keys(responses).length;
    if (answered < totalQuestions) {
        alert(`Por favor, responda todas as questoes. Faltam ${totalQuestions - answered} questoes.`);
        return;
    }

    const btn = document.getElementById('submitBtn');
    btn.disabled = true;
    btn.textContent = 'Enviando...';

    try {
        const res = await fetch(`/api/survey/${surveyCode}/submit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                responses: Object.fromEntries(
                    Object.entries(responses).map(([k, v]) => [String(k), v])
                )
            })
        });
        if (!res.ok) { const d = await res.json(); throw new Error(d.detail || 'Erro'); }
        const data = await res.json();

        document.getElementById('pagesContainer').classList.add('hidden');
        document.getElementById('progressBar').classList.add('hidden');
        document.getElementById('thanksTitle').textContent = data.thank_you_title || 'Obrigado!';
        document.getElementById('thanksMessage').textContent = data.thank_you_message || 'Suas respostas foram registradas.';
        document.getElementById('thanksSection').classList.remove('hidden');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
        alert('Erro ao enviar: ' + err.message);
        btn.disabled = false;
        btn.textContent = 'Enviar Pesquisa';
    }
}

init();
