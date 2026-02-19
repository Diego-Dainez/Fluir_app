/**
 * Fluir - Login e recuperacao de codigo
 */

document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const code = document.getElementById('adminCode').value.trim();
    const errEl = document.getElementById('loginError');
    const btn = document.getElementById('loginBtn');
    errEl.classList.remove('show');
    btn.disabled = true;
    btn.textContent = 'Entrando...';

    try {
        const res = await fetch('/api/admin/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ admin_code: code })
        });
        if (!res.ok) {
            let msg = 'Codigo invalido';
            try {
                const data = await res.json();
                const d = data.detail;
                msg = Array.isArray(d) ? (d[0]?.msg || d[0]) : (d || msg);
            } catch (_) {}
            throw new Error(msg);
        }
        const data = await res.json();
        sessionStorage.setItem('fluir_admin_code', code);
        sessionStorage.setItem('fluir_surveys', JSON.stringify(data.surveys));
        window.location.href = '/admin';
    } catch (err) {
        errEl.textContent = err.message;
        errEl.classList.add('show');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Entrar';
    }
});

if (sessionStorage.getItem('fluir_admin_code')) {
    window.location.href = '/admin';
}

document.getElementById('recoverLink').addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('recoverSection').classList.remove('hidden');
});

document.getElementById('recoverForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('recoverEmail').value.trim();
    const btn = document.getElementById('recoverBtn');
    const msgEl = document.getElementById('recoverMsg');
    msgEl.classList.add('hidden');
    btn.disabled = true;
    try {
        const res = await fetch('/api/admin/recover-code', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        const data = await res.json();
        msgEl.textContent = data.message || 'Se o email estiver cadastrado, voce recebera a chave em instantes.';
        msgEl.style.color = 'var(--green, #22c55e)';
        msgEl.classList.remove('hidden');
    } catch (err) {
        msgEl.textContent = 'Erro ao enviar. Tente novamente.';
        msgEl.style.color = 'var(--red, #ef4444)';
        msgEl.classList.remove('hidden');
    } finally {
        btn.disabled = false;
    }
});
