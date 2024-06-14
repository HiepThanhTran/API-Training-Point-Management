const showPreLoading = () => {
    const loadingModal = document.getElementById('loadingModal');
    loadingModal.style.display = 'flex';
};

const hidePreLoading = () => {
    const loadingModal = document.getElementById('loadingModal');
    loadingModal.style.display = 'none';
};

const generateRandomColor = () => {
    const [r, g, b] = [Math.random() * 255, Math.random() * 255, Math.random() * 255];
    return {
        color: `rgba(${r}, ${g}, ${b}, 0.2)`,
        borderColor: `rgba(${r}, ${g}, ${b}, 1)`,
    };
};

const generateChart = (
    ctx, type, labels,
    labelOfFaculty, datadataOfFaculty, bgColorsOfFaculty, borderColorsOfFaculty,
    labelOfClass, dataOfClass, bgColorsOfClass, borderColorsOfClass
) => {
    return new Chart(ctx, {
            type: type,
            data: {
                labels: labels,
                datasets: [
                    {
                        label: labelOfFaculty,
                        data: datadataOfFaculty,
                        borderWidth: 1,
                        borderColor: borderColorsOfFaculty,
                        backgroundColor: bgColorsOfFaculty,
                    },
                    {
                        label: labelOfClass,
                        data: dataOfClass,
                        borderWidth: 1,
                        borderColor: borderColorsOfClass,
                        backgroundColor: bgColorsOfClass,
                    }
                ],
            },
            options: {
                plugins: {
                    title: {
                        display: true,
                        text: 'Thống kê điểm rèn luyện',
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => ` ${context.dataset.label}: ${context.parsed.y} điểm` || '',
                        },
                    },
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: (value, index, ticks) => value + " điểm"
                        },
                    },
                }
            },
        },
    );
};