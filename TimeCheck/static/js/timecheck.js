// Global Variable
let mainDf = null;      // Data sheet with all columns
let userMapping = null; // Column headers
let fieldManager = {    // Field Manager
    name: null,
    id: null,
};

let conflictMethod = null; // Conflict validation method
let conflictGap = null;    // Conflict gap threshold


// Function to display headers in the form 
async function uploadAndGetHeaders() {

    // Clear global variables
    mainDf = null;
    fieldManager.id = null;
    fieldManager.name = null;
    userMapping = null;

    const files = document.getElementById('excel-files').files;
    const managerSelect = document.getElementById("field-manager-select");

    if (managerSelect.value === "") {
        showError("Error: Select Field Manager!");
        return null;
    }
    else {
        fieldManager.id = managerSelect.value;
        fieldManager.name = managerSelect.options[managerSelect.selectedIndex].text;
    }

    if (files.length === 0) {
        showError("Error: Select File(s)!");
        return null;
    }


    let dfList = []; // to store file data frame

    for (let file of files) {

        let df = await dfd.readExcel(file);
        dfList.push(df);
    }

    if (dfList.length > 1) {
        mainDf = dfd.concat({ dfList: dfList, axis: 0 });
    }
    else {
        mainDf = dfList[0];
    }

    // Display headers
    const excelHeaders = mainDf.columns;
    displayHeaders(excelHeaders);
}
// Display headers
function displayHeaders(excelHeaders) {
    document.getElementById("step-upload").style.display = 'none';
    document.getElementById("step-mapping").style.display = 'block';

    const errorDiv = document.getElementById('error-container');
    errorDiv.style.display = 'none';
    errorDiv.innerHTML = '';

    const container = document.getElementById("mapping-container");
    container.innerHTML = '';

    const requiredFields = [
        { id: 'instance_id', label: 'Instance ID', icon: 'fa-fingerprint' },
        { id: 'interviewer_id', label: 'Interviewer ID', icon: 'fa-user-tie' },
        { id: 'script_name', label: 'Script Name', icon: 'fa-file-code' },
        { id: 'date', label: 'Interview Date', icon: 'fa-calendar-alt' },
        { id: 'start_time', label: 'Start Time', icon: 'fa-clock' },
        { id: 'end_time', label: 'End Time', icon: 'fa-history' },
        { id: 'interview_length', label: 'Total Length', icon: 'fa-hourglass-start' },
        { id: 'interview_active_length', label: 'Active Length', icon: 'fa-bolt' },
    ];

    const optionsHtml = excelHeaders.map(header =>
        `<option value="${header}">${header}</option>`
    ).join('');

    requiredFields.forEach(field => {
        const fieldHtml = `
            <div class="mapping-item">
                <label>
                    <i class="fas ${field.icon}"></i> ${field.label}
                </label>
                <select name="${field.id}" class="header-selector" required>
                    <option value="">-- Choose Column --</option>
                    ${optionsHtml}
                </select>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', fieldHtml);
    });
 
}

// Validate user selection
function validateUserMapping() {

    // Clear global variable
    userMapping = null;
    conflictMethod = null;
    conflictGap = null; 

    const form = document.getElementById("mapping-form");
    const formData = new FormData(form);
    const mapping = Object.fromEntries(formData.entries());
    const errorDiv = document.getElementById('error-container');
    errorDiv.style.display = 'none';
    errorDiv.innerHTML = '';

    const selectedExcelColumns = Object.values(mapping);

    // Update Global Variables
    userMapping = mapping;
    const techniqueElement = document.querySelector('input[name="technique"]:checked');
    conflictMethod = techniqueElement ? techniqueElement.value : 'interview-length';
    conflictGap = document.getElementById('overlap-sensitivity').value;


    const isAnyEmpty = selectedExcelColumns.some(colName => colName === "");
    if (isAnyEmpty) {
        showError("Error: Please fill all fields!");
        return null;
    }

    const hasDuplicates = new Set(selectedExcelColumns).size !== selectedExcelColumns.length;
    if (hasDuplicates) {
        showError("Error: Can't select the same header more than once!");
        return null;
    }



    // 1. Check Instance ID
    const instanceIds = mainDf[mapping['instance_id']].values;
    if (instanceIds.some(val => isNaN(val) || val === "")) {
        showError("Error: Invalid Instance ID format or empty values!");
        return null
    }

    // 2. Check Interviewer ID
    const interviewerIds = mainDf[mapping['interviewer_id']].values;
    const icRegex = /^IC\d+$/;
    for (let i = 0; i < Math.min(interviewerIds.length, 20); i++) {
        let val = String(interviewerIds[i]).trim();
        if (val === "" || val === "undefined") {
            showError(`Error: Interviewer ID is Null at row ${i + 1}!`);
            return null
        }
        if (!icRegex.test(val)) {
            showError(`Error: Invalid Interviewer ID format at row ${i + 1}!`);
            return null;
        }
    }

    // 3. Check Script Name
    const scriptNames = mainDf[mapping['script_name']].values;
    for (let i = 0; i < Math.min(scriptNames.length, 20); i++) {
        let val = String(scriptNames[i]).trim();
        if (val === "" || val === "undefined" || val === "null") {
            showError(`Error: Missing Script Name at row ${i + 1}!`);
            return null;
        }
    }

    // 4.Check Interview Data
    mainDf = formatAndReplaceColumn(mainDf, mapping['date'], "date")
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    const dates = mainDf[mapping['date']].values;
    for (let i = 0; i < Math.min(dates.length, 20); i++) {
        let currentDate = dates[i];

        if (currentDate === null || !dateRegex.test(String(currentDate))) {
            showError(`Error: Invalid Date format at row ${i + 1}. Expected YYYY-MM-DD! date is ${currentDate}`);
            return null;
        }
    }

    console.log("Check Data:", mainDf[mapping['start_time']]);

    // 5.Check Interview Start & End Time
    mainDf = formatAndReplaceColumn(mainDf, mapping['start_time'], "datetime")
    mainDf = formatAndReplaceColumn(mainDf, mapping['end_time'], "datetime")
    
    const timeRegex = /^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}$/;
    const startTimes = mainDf[mapping['start_time']].values;
    const endTimes = mainDf[mapping['end_time']].values;
    console.log("Check Data:", mainDf[mapping['start_time']]);
    for (let i = 0; i < Math.min(startTimes.length, 20); i++) {
        if (startTimes[i] === "" || endTimes[i] === "" || startTimes[i] === "undefined" || endTimes[i] === "undefined") {
            showError(`Error: Start or End Time is Null at row ${i + 1}!`);
            return null
        }
        if (!timeRegex.test(String(startTimes[i])) || !timeRegex.test(String(endTimes[i]))) {
            showError(`Error: Invalid Start or End Time format at row ${i + 1}!`);
            return null
        }
        console.log("Original:", startTimes[i], "Type:", typeof startTimes[i]);
    }

    // 6.Check Interview Length
    const length = mainDf[mapping['interview_length']].values;
    const activeLength = mainDf[mapping['interview_active_length']].values;

    for (let i = 0; i < Math.min(length.length, 20); i++) {
        let l = parseFloat(length[i]);
        let al = parseFloat(activeLength[i]);
        if (isNaN(l) || isNaN(al)) {
            showError(`Error: Invalid Length format at row ${i + 1}!`);
            return null
        }
    }

    // Hide the selection container
    document.getElementById("step-mapping").style.display = 'none';

    // Display the review and process container
    const reviewStep = document.getElementById("step-review");
    const reviewDisplay = document.getElementById("review-display");
    reviewStep.style.display = 'block';

    reviewDisplay.innerHTML = '';


    const labelsMap = {
        instance_id: { label: 'Instance ID', icon: 'fa-fingerprint' },
        interviewer_id: { label: 'Interviewer ID', icon: 'fa-user-tie' },
        script_name: { label: 'Script Name', icon: 'fa-file-code' },
        date: { label: 'Interview Date', icon: 'fa-calendar-alt' },
        start_time: { label: 'Start Time', icon: 'fa-clock' },
        end_time: { label: 'End Time', icon: 'fa-history' },
        interview_length: { label: 'Total Length', icon: 'fa-hourglass-start' },
        interview_active_length: { label: 'Active Length', icon: 'fa-bolt' },
        sensitivity: { label: 'Overlap Sensitivity (Minutes)', icon: 'fa-sliders-h' },
        technique: { label: 'Validation Technique', icon: 'fa-microchip' }
    };

    if (fieldManager.id) {
        const managerHtml = `
        <div class="review-item" style="border-left: 4px solid #3498db; background: #f8fbff;">
            <span class="review-label">
                <i class="fas fa-user-tie"></i> Field Manager
            </span>
            <span class="review-value">${fieldManager.name}</span>
        </div>
    `;
        reviewDisplay.insertAdjacentHTML('beforeend', managerHtml);
    }

    Object.keys(mapping).forEach(key => {
        const field = labelsMap[key];

        const itemHtml = `
            <div class="review-item">
            <span class="review-label">
                <i class="fas ${field.icon}"></i> ${field.label}
            </span>
            <span class="review-value">${mapping[key]}</span>
        </div>
    `;

        reviewDisplay.insertAdjacentHTML('beforeend', itemHtml);
    });

}

// Start Process and send to Back End
async function startProcessing() {

    // 1. Check for mainDf and userMapping
    if (!mainDf || !userMapping) {
        showError("Error: Please upload files and complete mapping first!");
        return;
    }

    // 2. Prepare the object to sent to Backend
    const payload = {
        field_manager_id: fieldManager.id,
        user_mapping: userMapping,
        data: dfd.toJSON(mainDf),
 
        
    };

    // 3. Get CSRF Token from the page
    const csrfElement = document.querySelector('[name=csrfmiddlewaretoken]');
    if (!csrfElement) {
        showError("Security Error: CSRF Token not found!");
        return;
    }
    const csrftoken = csrfElement.value;

    // 4. Send to Server
    try {

        const response = await fetch('/timecheck-process/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(payload)

        });

        // 5. Get response from server
        if (response.ok) {
            alert("Data has been sent to server successfully.\nCheck Time Check results page to display or downlad.");
            window.location.reload();

        }
        else {
            alert("Error while sending data.\nTry Again!");
        }
    }
    catch(error) {
        console.error('Error: ', error);
        alert("Couldn't connect to Server!")
    }
}

// Cancel Selection Btn
function cancelSelection() {

    document.getElementById("step-mapping").style.display = 'none';
    document.getElementById("step-upload").style.display = 'block';

    const container = document.getElementById("mapping-container");
    container.innerHTML = '';

    document.getElementById("excel-files").value = '';

    const errorDiv = document.getElementById('error-container');
    errorDiv.style.display = 'none';
    errorDiv.innerHTML = '';
};

// Cancel Review Btn
function cancelProcess() {

    userMapping = null;

    document.getElementById("step-review").style.display = 'none';
    document.getElementById("step-mapping").style.display = 'block';

    const errorDiv = document.getElementById('error-container');
    errorDiv.style.display = 'none';
    errorDiv.innerHTML = '';
};

// Error Massage
function showError(errorMsg) {
    const errorDiv = document.getElementById('error-container');
    errorDiv.style.display = 'block';
    errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${errorMsg}`;

}

// Convert data type to the required format
function formatAndReplaceColumn(df, columnName, type) {
    let currentValues = df[columnName].values;

    let formattedValues = currentValues.map(value => {
        let d;
        let isExcelNumber = false;

        if (typeof value === 'number' && !isNaN(value)) {
            d = new Date(Math.round((value - 25569) * 86400 * 1000));
            isExcelNumber = true; 
        }
        else if (value instanceof Date) {
            d = value;
        }
        else {
            d = new Date(value);
            isExcelNumber = false; 
        }

        if (!d || isNaN(d.getTime())) return null;

        let year = isExcelNumber ? d.getUTCFullYear() : d.getFullYear();
        let month = String((isExcelNumber ? d.getUTCMonth() : d.getMonth()) + 1).padStart(2, '0');
        let day = String(isExcelNumber ? d.getUTCDate() : d.getDate()).padStart(2, '0');

        if (type === 'date') {
            return `${year}-${month}-${day}`;
        } 
        else {
            let hours = String(isExcelNumber ? d.getUTCHours() : d.getHours()).padStart(2, '0');
            let minutes = String(isExcelNumber ? d.getUTCMinutes() : d.getMinutes()).padStart(2, '0');
            let seconds = String(isExcelNumber ? d.getUTCSeconds() : d.getSeconds()).padStart(2, '0');
            
            return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
        }
    });


    let allColumns = df.columns;
    df.addColumn(columnName, formattedValues, { inplace: true });

    return df.loc({ columns: allColumns });
}

