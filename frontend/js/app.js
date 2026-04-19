document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide Icons
    if (window.lucide) {
        lucide.createIcons();
    }

    // Splash Screen Logic
    const splash = document.getElementById('splash');
    if (splash) {
        setTimeout(() => {
            splash.style.opacity = '0';
            setTimeout(() => {
                splash.style.visibility = 'hidden';
            }, 800);
        }, 2500);
    }

    // Fetch Data from API or fallback to mock
    const txBody = document.getElementById('tx-body');
    if (txBody) {
        fetch('/api/transactions')
            .then(res => res.json())
            .then(data => {
                renderTable(data);
            })
            .catch(err => {
                console.warn('API not available, using fallback data');
                const fallback = [
                    { id: '#92841', amount: '.00', origin: 'Germany (Berlin)', score: '92', status: 'CRITICAL' },
                    { id: '#92842', amount: '.50', origin: 'USA (Austin)', score: '02', status: 'SAFE' },
                    { id: '#92843', amount: ',290.00', origin: 'Nigeria (Lagos)', score: '88', status: 'CRITICAL' },
                    { id: '#92844', amount: '.00', origin: 'UK (London)', score: '12', status: 'SAFE' },
                    { id: '#92845', amount: '.00', origin: 'Russia (Moscow)', score: '65', status: 'WARNING' }
                ];
                renderTable(fallback);
            });
    }

    function renderTable(data) {
        txBody.innerHTML = '';
        data.forEach(tx => {
            const row = document.createElement('tr');
            const statusClass = tx.status === 'SAFE' ? 'sp-safe' : 'sp-danger';
            row.innerHTML = '<td>' + tx.id + '</td>' +
                            '<td>' + tx.amount + '</td>' +
                            '<td>' + tx.origin + '</td>' +
                            '<td><span class=\"text-primary\">' + tx.score + '/100</span></td>' +
                            '<td><span class=\"status-pill ' + statusClass + '\">' + tx.status + '</span></td>';
            txBody.appendChild(row);
        });
    }

    // Charting Logic
    const canvas = document.getElementById('fraudChart');
    if (canvas && window.Chart) {
        const ctx = canvas.getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['12am', '4am', '8am', '12pm', '4pm', '8pm', '11pm'],
                datasets: [{
                    label: 'Fraud Probability',
                    data: [12, 19, 3, 5, 2, 3, 15],
                    borderColor: '#8B5CF6',
                    borderWidth: 3,
                    tension: 0.4,
                    pointRadius: 0,
                    fill: true,
                    backgroundColor: 'rgba(139, 92, 246, 0.1)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { display: false },
                    x: { grid: { display: false }, ticks: { color: '#94A3B8' } }
                },
                plugins: { legend: { display: false } }
            }
        });
    }
});

window.showDashboard = function() {
    const hero = document.getElementById('hero');
    const features = document.getElementById('features');
    const dashboard = document.getElementById('dashboard');
    if (hero) hero.style.display = 'none';
    if (features) features.style.display = 'none';
    if (dashboard) dashboard.style.display = 'block';
    
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    const dbLink = document.querySelector('a[href=\"#dashboard\"]');
    if (dbLink) dbLink.classList.add('active');
}

window.hideDashboard = function() {
    const hero = document.getElementById('hero');
    const features = document.getElementById('features');
    const dashboard = document.getElementById('dashboard');
    if (hero) hero.style.display = 'block';
    if (features) features.style.display = 'block';
    if (dashboard) dashboard.style.display = 'none';

    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    const homeLink = document.querySelector('a[href=\"#hero\"]');
    if (homeLink) homeLink.classList.add('active');
}
