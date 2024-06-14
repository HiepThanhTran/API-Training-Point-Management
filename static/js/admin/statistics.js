// Select tag
const semesterSelect = document.getElementById("semester-select")
const facultySelect = document.getElementById("faculty-select")
const classSelect = document.getElementById("class-select")
// Button export
const facultyExportPDF = document.getElementById("faculty-export-pdf")
const facultyExportCSV = document.getElementById("faculty-export-csv")
const classExportPDF = document.getElementById("class-export-pdf")
const classExportCSV = document.getElementById("class-export-csv")
// Faculty
const totalClassesFaculty = document.querySelector(".total-classes-faculty p")
const totalStudentsFaculty = document.querySelector(".total-students-faculty p")
const totalPointsFaculty = document.querySelector(".total-points-faculty p")
const averagePointsFaculty = document.querySelector(".average-points-faculty p")
// Class
const totalStudentsClass = document.querySelector(".total-students-class p")
const totalPointsClass = document.querySelector(".total-points-class p")
const averagePointsClass = document.querySelector(".average-points-class p")

const fetchApi = async (url, expectedContentType = 'application/json') => {
    showPreLoading();
    try {
        const response = await fetch(url, {method: 'GET'});

        if (!response.ok) {
            throw new Error(`API request failed with status ${response.status}`);
        }

        const contentType = response.headers.get('Content-Type');
        if (contentType && contentType.includes(expectedContentType))
            if (expectedContentType === 'application/json') return response.json();
            else return {
                blob: await response.blob(),
                contentDisposition: response.headers.get('Content-Disposition')
            };
        else throw new Error(`Unsupported content type: ${contentType}`);
    } catch (error) {
        console.error(error);
        throw error;
    } finally {
        hidePreLoading();
    }
}

window.onload = (event) => {
    const ctxChartStatistics = document.getElementById("chartStatistics").getContext("2d")
    let chartStatistics = generateChart(
        ctxChartStatistics, 'bar', labelsOfFaculty || labelsOfClass,
        "Điểm rèn luyện theo khoa", dataOfFaculty, bgColorsOfFaculty, borderColorsOfFaculty,
        "Điểm rèn luyện theo lớp", dataOfClass, bgColorsOfClass, borderColorsOfClass
    )

    semesterSelect.addEventListener("change", () => updateStatistics(chartStatistics, true));
    classSelect.addEventListener("change", () => updateStatistics(chartStatistics));
    facultySelect.addEventListener("change", async () => {
        const facultyId = facultySelect.value;
        const classes = await fetchApi(`/api/v1/classes/?faculty_id=${facultyId}`);
        classSelect.innerHTML = '';
        classes.forEach(sclass => {
            const option = document.createElement('option');
            option.value = sclass.id;
            option.text = sclass.name;
            classSelect.appendChild(option);
        });
        await updateStatistics(chartStatistics, true);
    });

    facultyExportPDF.addEventListener("click", () => exportFile('pdf', true))
    facultyExportCSV.addEventListener("click", () => exportFile('csv', true))
    classExportPDF.addEventListener("click", () => exportFile('pdf'))
    classExportCSV.addEventListener("click", () => exportFile('csv'))
};

const updateStatistics = async (chartStatistics, isFaculty = false) => {
    const semesterCode = semesterSelect.value;
    const facultyId = facultySelect.value;
    const classId = classSelect.value;

    if (isFaculty === true) {
        const url = `/api/v1/statistics/${semesterCode}/points/?faculty_id=${facultyId}`
        const statisticsFaculty = await fetchApi(url);
        updateChart(chartStatistics, statisticsFaculty, isFaculty);
        updateStatisticsFaculty(statisticsFaculty);
    }

    const url = `/api/v1/statistics/${semesterCode}/points/?faculty_id=${facultyId}&class_id=${classId}`
    const statisticsClass = await fetchApi(url);
    updateChart(chartStatistics, statisticsClass);
    updateStatisticsClass(statisticsClass);
}

const updateStatisticsFaculty = (statisticsFaculty) => {
    totalClassesFaculty.innerHTML = statisticsFaculty.total_classes
    totalStudentsFaculty.innerHTML = statisticsFaculty.total_students
    totalPointsFaculty.innerHTML = statisticsFaculty.total_points
    averagePointsFaculty.innerHTML = statisticsFaculty.average_points
}

const updateStatisticsClass = (statisticsClass) => {
    totalStudentsClass.innerHTML = statisticsClass.total_students
    totalPointsClass.innerHTML = statisticsClass.total_points
    averagePointsClass.innerHTML = statisticsClass.average_points
}

const updateChart = (chart, data, isFaculty = false) => {
    const [dataPoints, bgColors, borderColors] = [[], [], []];

    for (let key in data.achievements) {
        const {color, borderColor} = generateRandomColor();
        dataPoints.push(data.achievements[key]);
        bgColors.push(color);
        borderColors.push(borderColor);
    }

    const datasetIndex = isFaculty === true ? 0 : 1;
    Object.assign(chart.data.datasets[datasetIndex], {
        data: dataPoints, backgroundColor: bgColors, borderColor: borderColors
    });
    chart.update();
}

const exportFile = async (typeFile, isFaculty = false) => {
    const semesterCode = semesterSelect.value;
    const classId = classSelect.value;

    let url = `/api/v1/statistics/${semesterCode}/export/?type=${typeFile}&class_id=${classId}`;
    if (isFaculty === true) {
        const facultyId = facultySelect.value;
        url += `&faculty_id=${facultyId}`;
    }

    let expectedContentType = 'text/csv';
    if (typeFile === 'pdf') {
        expectedContentType = 'application/pdf';
    }

    try {
        const { blob, contentDisposition} = await fetchApi(url, expectedContentType);

        let fileName = "downloaded_file";
        if (contentDisposition) {
            const match = contentDisposition.match(/filename="?(.+)"?/);
            if (match && match[1]) fileName = match[1];
        }

        const blobUrl = URL.createObjectURL(blob);

        const link = document.createElement('a');
        link.href = blobUrl;
        link.target = "_blank"
        link.download = fileName
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        URL.revokeObjectURL(blobUrl);
    } catch (error) {
        console.error("Failed to export file:", error);
    }
}
