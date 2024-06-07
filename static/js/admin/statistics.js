// Select tag
const semesterSelect = document.getElementById("semester-select")
const facultySelect = document.getElementById("faculty-select")
const classSelect = document.getElementById("class-select")
// Faculty
const totalClassesFaculty = document.querySelector(".total-classes-faculty p")
const totalStudentsFaculty = document.querySelector(".total-students-faculty p")
const totalPointsFaculty = document.querySelector(".total-points-faculty p")
const averagePointsFaculty = document.querySelector(".average-points-faculty p")
// Class
const totalStudentsClass = document.querySelector(".total-students-class p")
const totalPointsClass = document.querySelector(".total-points-class p")
const averagePointsClass = document.querySelector(".average-points-class p")

async function fetchApiToGetStatistics(url) {
    showPreLoading();
    const response = await fetch(url, {method: 'GET', headers: {'Content-Type': 'application/json'}});
    hidePreLoading();
    return response.ok ? response.json() : new Error('API request failed');
}

window.onload = async (event) => {
    const [ctxLeft, ctxRight] = [document.getElementById("chartFaculty").getContext("2d"), document.getElementById("chartClass").getContext("2d")];
    let chartFaculty = generateChart(ctxLeft, 'bar', "Điểm rèn luyện theo khoa", labelsLeft, dataLeft, bgColorsLeft, borderColorsLeft)
    let chartClass = generateChart(ctxRight, 'bar', "Điểm rèn luyện theo lớp", labelsRight, dataRight, bgColorsRight, borderColorsRight)

    semesterSelect.addEventListener("change", async () => updateStatistics(chartClass, chartFaculty));
    facultySelect.addEventListener("change", async () => {
        const facultyId = facultySelect.value;
        const classes = await fetchApiToGetStatistics(`/api/v1/classes/?faculty_id=${facultyId}`);
        classSelect.innerHTML = '';
        classes.forEach(sclass => {
            const option = document.createElement('option');
            option.value = sclass.id;
            option.text = sclass.name;
            classSelect.appendChild(option);
        });
        await updateStatistics(chartClass, chartFaculty);
    });
    classSelect.addEventListener("change", async () => updateStatistics(chartClass));
};

async function updateStatistics(chartClass, chartFaculty = null) {
    const semesterCode = semesterSelect.value;
    const facultyId = facultySelect.value;
    const classId = classSelect.value;

    if (chartFaculty !== null) {
        const statisticsFaculty = await fetchApiToGetStatistics(`/api/v1/statistics/${semesterCode}/points/?faculty_id=${facultyId}`);
        updateChart(chartFaculty, statisticsFaculty);
        updateStatisticsFaculty(statisticsFaculty);
    }

    const statisticsClass = await fetchApiToGetStatistics(`/api/v1/statistics/${semesterCode}/points/?faculty_id=${facultyId}&class_id=${classId}`);
    updateChart(chartClass, statisticsClass);
    updateStatisticsClass(statisticsClass);
}

function updateStatisticsFaculty(statisticsFaculty) {
    totalClassesFaculty.innerHTML = statisticsFaculty.total_classes
    totalStudentsFaculty.innerHTML = statisticsFaculty.total_students
    totalPointsFaculty.innerHTML = statisticsFaculty.total_points
    averagePointsFaculty.innerHTML = statisticsFaculty.average_points
}

function updateStatisticsClass(statisticsClass) {
    totalStudentsClass.innerHTML = statisticsClass.total_students
    totalPointsClass.innerHTML = statisticsClass.total_points
    averagePointsClass.innerHTML = statisticsClass.average_points
}

function updateChart(chart, data) {
    const [labels, dataPoints, bgColors, borderColors] = [[], [], [], []];
    let color;
    for (let key in data.achievements) {
        dataPoints.push(data.achievements[key]);
        color = generateRandomColor();
        bgColors.push(color.color);
        borderColors.push(color.borderColor);
    }
    chart.data.datasets[0].data = dataPoints;
    chart.data.datasets[1].data = dataPoints;
    chart.data.datasets[0].backgroundColor = bgColors;
    chart.data.datasets[0].borderColor = borderColors;
    chart.update();
}