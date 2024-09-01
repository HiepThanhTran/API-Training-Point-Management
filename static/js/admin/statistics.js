const semesterSelect = document.getElementById("semester-select");
const facultySelect = document.getElementById("faculty-select");
const classSelect = document.getElementById("class-select");

const facultyExportPDF = document.getElementById("faculty-export-pdf");
const facultyExportCSV = document.getElementById("faculty-export-csv");
const classExportPDF = document.getElementById("class-export-pdf");
const classExportCSV = document.getElementById("class-export-csv");

const totalClassesFaculty = document.querySelector(".total-classes-faculty p");
const totalStudentsFaculty = document.querySelector(
    ".total-students-faculty p"
);
const totalPointsFaculty = document.querySelector(".total-points-faculty p");
const averagePointsFaculty = document.querySelector(
    ".average-points-faculty p"
);

const totalStudentsClass = document.querySelector(".total-students-class p");
const totalPointsClass = document.querySelector(".total-points-class p");
const averagePointsClass = document.querySelector(".average-points-class p");

const fetchApi = async (url, expectedContentType = "application/json") => {
    showPreLoading();
    try {
        const response = await fetch(url, {method: "GET"});
        if (!response.ok) {
            throw new Error(
                `API request failed with status ${response.status}`
            );
        }
        const contentType = response.headers.get("Content-Type");
        if (!contentType || !contentType.includes(expectedContentType)) {
            throw new Error(`Unsupported content type: ${contentType}`);
        }
        return expectedContentType === "application/json"
            ? await response.json()
            : {
                blob: await response.blob(),
                contentDisposition: response.headers.get(
                    "Content-Disposition"
                ),
            };
    } catch (error) {
        console.error(error);
        throw error;
    } finally {
        hidePreLoading();
    }
};

const updateStatistics = async (chartStatistics, isFaculty = false) => {
    const semesterCode = semesterSelect.value;
    const facultyID = facultySelect.value;
    const classID = classSelect.value;

    try {
        const url =
            `/api/v1/statistics/${semesterCode}/points/?faculty_id=${facultyID}` +
            (isFaculty ? "" : `&class_id=${classID}`);
        const statistics = await fetchApi(url);
        updateChart(chartStatistics, statistics, isFaculty);
        if (isFaculty) {
            updateStatisticsFaculty(statistics);
        } else {
            updateStatisticsClass(statistics);
        }
    } catch (error) {
        console.error("Failed to fetch statistics:", error);
    }
};

const updateStatisticsFaculty = (statisticsFaculty) => {
    totalClassesFaculty.textContent = statisticsFaculty.total_classes;
    totalStudentsFaculty.textContent = statisticsFaculty.total_students;
    totalPointsFaculty.textContent = statisticsFaculty.total_points;
    averagePointsFaculty.textContent = statisticsFaculty.average_points;
};

const updateStatisticsClass = (statisticsClass) => {
    totalStudentsClass.textContent = statisticsClass.total_students;
    totalPointsClass.textContent = statisticsClass.total_points;
    averagePointsClass.textContent = statisticsClass.average_points;
};

const updateChart = (chart, data, isFaculty = false) => {
    const dataPoints = [];
    const bgColors = [];
    const borderColors = [];

    for (let key in data.achievements) {
        const {color, borderColor} = generateRandomColor();
        dataPoints.push(data.achievements[key]);
        bgColors.push(color);
        borderColors.push(borderColor);
    }

    const datasetIndex = isFaculty ? 0 : 1;
    Object.assign(chart.data.datasets[datasetIndex], {
        data: dataPoints,
        backgroundColor: bgColors,
        borderColor: borderColors,
    });
    chart.update();
};

const exportFile = async (typeFile, isFaculty = false) => {
    const semesterCode = semesterSelect.value;
    const facultyID = facultySelect.value;
    const classID = classSelect.value;

    let url = `/api/v1/statistics/${semesterCode}/export/?type=${typeFile}`;
    url += isFaculty
        ? `&faculty_id=${facultyID}`
        : `&faculty_id=${facultyID}&class_id=${classID}`;

    let expectedContentType =
        typeFile === "pdf" ? "application/pdf" : "text/csv";

    try {
        const {blob, contentDisposition} = await fetchApi(
            url,
            expectedContentType
        );
        let fileName = "statistics_file";
        if (contentDisposition) {
            const match = contentDisposition.match(/filename="?(.+)"?/);
            if (match && match[1]) {
                fileName = match[1];
            }
        }
        const blobUrl = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = blobUrl;
        link.download = fileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(blobUrl);
    } catch (error) {
        console.error("Failed to export file:", error);
    }
};

window.onload = () => {
    const ctxChartStatistics = document
        .getElementById("chartStatistics")
        .getContext("2d");
    let chartStatistics = generateChart(
        ctxChartStatistics,
        "bar",
        labelsOfFaculty || labelsOfClass,
        "Điểm rèn luyện theo khoa",
        dataOfFaculty,
        bgColorsOfFaculty,
        borderColorsOfFaculty,
        "Điểm rèn luyện theo lớp",
        dataOfClass,
        bgColorsOfClass,
        borderColorsOfClass
    );

    semesterSelect.addEventListener("change", () =>
        updateStatistics(chartStatistics, true)
    );
    classSelect.addEventListener("change", () =>
        updateStatistics(chartStatistics)
    );
    facultySelect.addEventListener("change", async () => {
        const facultyID = facultySelect.value;
        const classes = await fetchApi(
            `/api/v1/classes/?faculty_id=${facultyID}`
        );
        classSelect.innerHTML = "";
        classes.forEach((sclass) => {
            const option = document.createElement("option");
            option.value = sclass.id;
            option.textContent = sclass.name;
            classSelect.appendChild(option);
        });
        await updateStatistics(chartStatistics, true);
    });

    facultyExportPDF.addEventListener("click", () => exportFile("pdf", true));
    facultyExportCSV.addEventListener("click", () => exportFile("csv", true));
    classExportPDF.addEventListener("click", () => exportFile("pdf"));
    classExportCSV.addEventListener("click", () => exportFile("csv"));
};
