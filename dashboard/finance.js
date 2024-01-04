document.addEventListener('DOMContentLoaded', function() {
    const tickerSelect = document.getElementById('ticker-select');
    const yearSelect = document.getElementById('year-select');
    const monthSelect = document.getElementById('month-select');
    const loadDataButton = document.getElementById('load-data');
    let allData = [];
    let financeChart;

    // Charger les données et remplir les sélecteurs
    fetch('http://localhost:5000/data')
    .then(response => response.json())
    .then(data => {
        allData = data;

        // Remplir les sélecteurs
        populateSelects(allData);
        updateChart(allData); // Affiche initialement toutes les données
    })
    .catch(error => {
        console.error('Erreur lors de la récupération des données:', error);
    });

    // Remplir les sélecteurs avec des options uniques
    function populateSelects(data) {
        const tickers = [...new Set(data.map(item => item.Ticker))];
        tickerSelect.innerHTML = tickers.map(ticker => `<option value="${ticker}">${ticker}</option>`).join('');

        const years = [...new Set(data.map(item => item.Year))];
        yearSelect.innerHTML = years.map(year => `<option value="${year}">${year}</option>`).join('');

        const months = [...new Set(data.map(item => item.Month))];
        monthSelect.innerHTML = months.map(month => `<option value="${month}">${month}</option>`).join('');
    }

    // Écouteur d'événements pour le bouton de chargement
    loadDataButton.addEventListener('click', () => {
        const selectedTicker = tickerSelect.value;
        const selectedYear = parseInt(yearSelect.value);
        const selectedMonth = parseInt(monthSelect.value);

        const filteredData = allData.filter(item => 
            item.Ticker === selectedTicker && 
            item.Year === selectedYear && 
            item.Month === selectedMonth
        );

        updateChart(filteredData);
    });

    // Mettre à jour ou créer le graphique
    function updateChart(data) {
        const ctx = document.getElementById('financeChart').getContext('2d');
        if (financeChart) {
            financeChart.destroy(); // Détruire l'ancien graphique
        }
        financeChart = new Chart(ctx, {
            type: 'bar', 
            data: {
                labels: data.map(item => `${item.Month}/${item.Year}`),
                datasets: [
                    {
                        label: 'Average ROI',
                        data: data.map(item => item.AverageROI),
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1,
                        yAxisID: 'y-axis-roi'
                    },
                    {
                        label: 'Volatility',
                        data: data.map(item => item.Volatility),
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1,
                        yAxisID: 'y-axis-vol'
                    }
                ]
            },
            options: {
                scales: {
                    'y-axis-roi': {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Average ROI'
                        }
                    },
                    'y-axis-vol': {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Volatility'
                        },
                        grid: {
                            drawOnChartArea: false
                        }
                    }
                }
            }
        });
    }
});
