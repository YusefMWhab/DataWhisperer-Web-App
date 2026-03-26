// Display User Dropdown list
function toggleDropdown() {
    const dropdown = document.getElementById('userDropdown');
    const arrow = document.querySelector('.arrow-icon');

    dropdown.classList.toggle('show-dropdown');

    if (dropdown.classList.contains('show-dropdown')) {
        arrow.style.transform = 'rotate(360deg)';
    } else {
        arrow.style.transform = 'rotate(0deg)';
    }
}

// Hide User Dropdown list
window.addEventListener('click', function(e) {
    const container = document.getElementById('nav-user-info');
    const dropdown = document.getElementById('userDropdown');
    const arrow = document.querySelector('.arrow-icon');
    
    if (!container.contains(e.target)) {
        dropdown.classList.remove('show-dropdown');
        arrow.style.transform = 'rotate(0deg)';
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const logoutBtn = document.getElementById('logout-btn');

    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();

            if (confirm('Are you sure you want to Logout?')) {
                
                function getCookie(name) {
                    let cookieValue = null;
                    if (document.cookie && document.cookie !== '') {
                        const cookies = document.cookie.split(';');
                        for (let i = 0; i < cookies.length; i++) {
                            const cookie = cookies[i].trim();
                            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                break;
                            }
                        }
                    }
                    return cookieValue;
                }

                const csrftoken = getCookie('csrftoken');

                const form = document.createElement('form');
                form.method = 'POST';
                form.action = "/logout/";
                
                const csrfInput = document.createElement('input');
                csrfInput.type = 'hidden';
                csrfInput.name = 'csrfmiddlewaretoken';
                csrfInput.value = csrftoken;
                
                form.appendChild(csrfInput);
                document.body.appendChild(form);
                form.submit();
            }
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const messageBox = document.getElementById('django-messages');
    
    if (messageBox) {
        setTimeout(function() {
            messageBox.classList.add('fade-out'); 
            
            setTimeout(function() {
                messageBox.remove();
            }, 500);
            
        }, 3000);
    }
});