// Report Navigation 
function showRawData(btnElement){

    toggle_Report("row-data-container", btnElement);
}

function showConflictReport(btnElement){

    toggle_Report("conflict-report-container", btnElement);
}

function showDailyCountReport(btnElement){

    toggle_Report("dailty-count-container", btnElement);
}

function showOutHoursReport(btnElement){
    
    toggle_Report("out-hours-container", btnElement);
}


function showLOIReport(btnElement){

    toggle_Report("loi-container", btnElement);
}

function toggle_Report(activeContainerId, clickedBtn){
    const containers = [
        "row-data-container",
        "conflict-report-container",
        "dailty-count-container",
        "out-hours-container",
        "loi-container"
    ];

    containers.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            if (id === activeContainerId) {
                el.style.display = "block";
                el.classList.add("fadeIn");
            } else {
                el.style.display = "none";
            }
        }
    });

    document.querySelectorAll('#top-nav-actions .action-btn').forEach(btn => {
        btn.classList.remove('btn-inactive'); 
    });

    if (clickedBtn) {
        clickedBtn.classList.add('btn-inactive');
    }

}

/* ============================================================================================*/
// Plot LOI 
document.addEventListener('DOMContentLoaded', function() {
    // سحب الداتا اللي حطيناها في الـ window
    const data = window.loiDataFromDjango;

    if (data && data.length > 0 && !data[0].Error) {
        renderLOICharts(data);
    }    
});

function renderLOICharts(loiData) {
    const wrapper = document.getElementById('charts-wrapper');
    if (!wrapper) return;

    const projects = {};
    loiData.forEach(item => {
        const pName = item["Script Name"];
        if (!projects[pName]) {
            projects[pName] = {
                ids: [],
                avgs: [],
                globalAvg: item["Project Global Avg"]
            };
        }
        projects[pName].ids.push(item["Interviewer ID"]);
        projects[pName].avgs.push(item["Avg Interview Length"]);
    });

    Object.keys(projects).forEach(projectName => {
        const projectData = projects[projectName];
        
        const chartBox = document.createElement('div');
        chartBox.style.marginBottom = '40px';
        chartBox.style.background = '#0b1d3a';
        chartBox.style.padding = '15px';
        chartBox.style.borderRadius = '8px';

        const canvas = document.createElement('canvas');
        canvas.style.height = '350px'; // تحديد ارتفاع ثابت
        chartBox.appendChild(canvas);
        wrapper.appendChild(chartBox);

        new Chart(canvas, {
            type: 'bar',
            data: {
                labels: projectData.ids,
                datasets: [
                    {
                        label: 'Interviewer Avg (min)',
                        data: projectData.avgs,
                        backgroundColor: '#6A63FF', 
                        backgroundColor: projectData.avgs.map((val) => {
                        const globalAvg = projectData.globalAvg;
                        const diff = Math.abs(val - globalAvg) / globalAvg; 
                        
                        return diff > 0.2 ? '#ff9c9c' : '#6A63FF';
                }),
                        order: 2
                    },
                    {
                        label: 'Project Avg',
                        data: Array(projectData.ids.length).fill(projectData.globalAvg),
                        borderColor: '#F74343', // الخط الأحمر للمتوسط
                        borderWidth: 2,
                        borderDash: [8, 4],
                        type: 'line',
                        pointRadius: 0,
                        fill: false,
                        order: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: `Project: ${projectName}`,
                        color: 'white',
                        font: { size: 16 }
                    },
                    legend: { labels: { color: '#ccc' } }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: '#fff' }
                    },
                    x: {
                        ticks: { color: '#fff', rotation: 45 },
                        grid: { display: false }
                    }
                }
            }
        });
    });
}