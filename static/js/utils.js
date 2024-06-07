const showPreLoading = () => {
    const loadingModal = document.getElementById('loadingModal');
    loadingModal.style.display = 'flex';
};

const hidePreLoading = () => {
    const loadingModal = document.getElementById('loadingModal');
    loadingModal.style.display = 'none';
};

const generateRandomColor = () => {
    let r = Math.random() * 255;
    let g = Math.random() * 255;
    let b = Math.random() * 255;
    return {
        color: `rgba(${r}, ${g}, ${b}, 0.2)`, borderColor: `rgba(${r}, ${g}, ${b}, 1)`,
    };
};

const generateChart = (ctx, type, label, labels, data, bgColors, borderColors) => {
    return new Chart(ctx, {
        type: type,
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                backgroundColor: bgColors,
                borderColor: borderColors,
                borderWidth: 1,
            }, {
                type: 'line',
                label: 'Line Dataset',
                data: data,
                fill: false,
                borderColor: 'rgb(54, 162, 235)'
            }],
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                },
            },
        },
    });
};