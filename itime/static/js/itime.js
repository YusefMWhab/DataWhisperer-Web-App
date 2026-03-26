document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('project-search');
    const selectElement = document.getElementById('projects-select');
    const optgroups = selectElement.getElementsByTagName('optgroup');

    selectElement.onmousedown = function(e) {
        if (e.target.tagName === 'OPTION') {
            e.preventDefault(); 
            
            const option = e.target;
            const scrollPos = selectElement.scrollTop;
            
            option.selected = !option.selected;
            
            setTimeout(() => { selectElement.scrollTop = scrollPos; }, 0);
            selectElement.focus();
        }
    };

    searchInput.addEventListener('input', function() {
        const filter = searchInput.value.toLowerCase();
        
        for (let group of optgroups) {
            const managerName = group.label.toLowerCase();
            const options = group.getElementsByTagName('option');
            let hasMatch = false;

            for (let option of options) {
                const projectName = option.text.toLowerCase();
                
                if (managerName.includes(filter) || projectName.includes(filter)) {
                    option.style.display = ""; 
                    hasMatch = true;
                } else {
                    option.style.display = "none";
                }
            }
            
            group.style.display = hasMatch ? "" : "none";
        }
    });
});


function confirmExport() {
    if (confirm("Are you sure? This will mark ALL pending records as exported and they won't appear in the next Excel download.")) {
        document.getElementById('export-form').submit();
    }
}