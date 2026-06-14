/* ==========================================================================
   LendAHand Client-side Controller - Theme, Modals, Wizard Forms, AJAX & Toast Alerts
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initModals();
    initTagSelectors();
});

// ==================== THEME CONTROLLER ====================
function initTheme() {
    const themeToggleBtn = document.getElementById('theme-toggle');
    if (!themeToggleBtn) return;
    
    // Check saved theme or system preference
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    let currentTheme = 'dark'; // Default to premium dark theme
    if (savedTheme) {
        currentTheme = savedTheme;
    } else if (!systemPrefersDark) {
        currentTheme = 'light';
    }
    
    document.documentElement.setAttribute('data-theme', currentTheme);
    
    themeToggleBtn.addEventListener('click', () => {
        const targetTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', targetTheme);
        localStorage.setItem('theme', targetTheme);
        showToast(`Swapped to ${targetTheme} theme`, 'info');
    });
}

// ==================== TOAST SYSTEM ====================
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    // Choose icon based on type
    let icon = '✓';
    if (type === 'error') icon = '✕';
    if (type === 'info') icon = 'ℹ';
    
    toast.innerHTML = `
        <div class="toast-icon">${icon}</div>
        <div class="toast-message">${message}</div>
    `;
    
    container.appendChild(toast);
    
    // Auto remove toast
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease forwards';
        toast.addEventListener('animationend', () => {
            toast.remove();
        });
    }, 4000);
}

// ==================== INTERACTIVE MODALS ====================
let currentSelectedOpportunityId = null;

function initModals() {
    const oppModal = document.getElementById('opp-modal');
    if (!oppModal) return;
    
    const closeBtns = document.querySelectorAll('.close-btn');
    
    // Close modal event
    closeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            oppModal.classList.remove('active');
            closeHoursModal();
        });
    });
    
    // Close on backdrop click
    window.addEventListener('click', (e) => {
        if (e.target === oppModal) {
            oppModal.classList.remove('active');
        }
        const hoursModal = document.getElementById('hours-modal');
        if (e.target === hoursModal) {
            closeHoursModal();
        }
    });
    
    // Modal Apply action button
    const applyBtn = document.getElementById('modal-apply-btn');
    if (applyBtn) {
        applyBtn.addEventListener('click', () => {
            if (currentSelectedOpportunityId) {
                applyForOpportunity(currentSelectedOpportunityId);
            }
        });
    }
}

function openOpportunityModal(id) {
    const modal = document.getElementById('opp-modal');
    const loader = document.getElementById('modal-loader');
    const body = document.getElementById('modal-body');
    if (!modal) return;
    
    currentSelectedOpportunityId = id;
    modal.classList.add('active');
    loader.classList.remove('hidden');
    body.classList.add('hidden');
    
    // Get info from local data store
    const opp = seedOpportunities[id];
    if (!opp) {
        showToast('Error loading opportunity details.', 'error');
        modal.classList.remove('active');
        return;
    }
    
    // Populate modal details
    document.getElementById('modal-title').innerText = opp.title;
    document.getElementById('modal-desc').innerText = opp.description;
    
    const catBadge = document.getElementById('modal-category');
    catBadge.innerText = opp.category;
    catBadge.className = `opp-category-tag ${opp.category.toLowerCase().replace(' ', '-')}`;
    
    document.getElementById('modal-date').innerText = opp.date;
    document.getElementById('modal-time').innerText = opp.time;
    document.getElementById('modal-location').innerText = opp.location;
    document.getElementById('modal-skills').innerText = opp.skills || 'None specific';
    document.getElementById('modal-slots').innerText = opp.slots;
    
    // Check if full
    const applyBtn = document.getElementById('modal-apply-btn');
    if (applyBtn) {
        if (opp.filled >= opp.max) {
            applyBtn.innerText = 'Opportunity Full';
            applyBtn.disabled = true;
            applyBtn.style.opacity = '0.5';
        } else {
            applyBtn.innerText = 'Confirm Application';
            applyBtn.disabled = false;
            applyBtn.style.opacity = '1';
        }
    }
    
    loader.classList.add('hidden');
    body.classList.remove('hidden');
}

// ==================== AUTHENTICATION & MULTI-STEP FORM ====================
function switchAuthMode(mode) {
    const tabLogin = document.getElementById('tab-login');
    const tabRegister = document.getElementById('tab-register');
    const loginWrapper = document.getElementById('login-form-wrapper');
    const registerWrapper = document.getElementById('register-form-wrapper');
    
    if (!tabLogin || !tabRegister) return;
    
    if (mode === 'login') {
        tabLogin.classList.add('active');
        tabRegister.classList.remove('active');
        loginWrapper.classList.remove('hidden');
        registerWrapper.classList.add('hidden');
    } else {
        tabLogin.classList.remove('active');
        tabRegister.classList.add('active');
        loginWrapper.classList.add('hidden');
        registerWrapper.classList.remove('hidden');
    }
}

let regStep = 1;

function nextRegisterStep() {
    // Validate Step 1 before proceeding
    const name = document.getElementById('reg-name').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-password').value;
    const phone = document.getElementById('reg-phone').value.trim();
    const age = document.getElementById('reg-age').value;
    
    if (!name || !email || !password) {
        showToast('Please fill in name, email, and password.', 'error');
        return;
    }
    
    if (password.length < 6) {
        showToast('Password must be at least 6 characters.', 'error');
        return;
    }
    
    if (age && parseInt(age) < 14) {
        showToast('Minimum age limit is 14.', 'error');
        return;
    }
    
    // Switch to step 2
    regStep = 2;
    document.getElementById('reg-step-1').classList.add('hidden');
    document.getElementById('reg-step-2').classList.remove('hidden');
    
    // Update step headers
    document.querySelector('.step.step-2').classList.add('active');
}

function prevRegisterStep() {
    regStep = 1;
    document.getElementById('reg-step-1').classList.remove('hidden');
    document.getElementById('reg-step-2').classList.add('hidden');
    document.querySelector('.step.step-2').classList.remove('active');
}

function initTagSelectors() {
    const selectors = ['skills-selector', 'interests-selector', 'days-selector'];
    
    selectors.forEach(id => {
        const container = document.getElementById(id);
        if (!container) return;
        
        const tags = container.querySelectorAll('.selectable-tag');
        tags.forEach(tag => {
            tag.addEventListener('click', () => {
                tag.classList.toggle('selected');
            });
        });
    });
}

// Gather selected values from a tag container
function getSelectedTags(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return [];
    
    const selected = container.querySelectorAll('.selectable-tag.selected');
    return Array.from(selected).map(tag => tag.getAttribute('data-val'));
}

// Handle Register submit
async function handleRegister(e) {
    e.preventDefault();
    
    const name = document.getElementById('reg-name').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-password').value;
    const phone = document.getElementById('reg-phone').value.trim();
    const age = document.getElementById('reg-age').value;
    
    const skills = getSelectedTags('skills-selector');
    const interests = getSelectedTags('interests-selector');
    const availability = getSelectedTags('days-selector');
    
    const payload = {
        name, email, password, phone, age, skills, interests, availability
    };
    
    try {
        const res = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await res.json();
        if (data.success) {
            showToast('Account created successfully!', 'success');
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1000);
        } else {
            showToast(data.message || 'Registration failed.', 'error');
        }
    } catch (err) {
        showToast('Network error, please try again.', 'error');
    }
}

// Handle Login submit
async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;
    
    try {
        const res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await res.json();
        if (data.success) {
            showToast('Welcome back!', 'success');
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1000);
        } else {
            showToast(data.message || 'Invalid email or password.', 'error');
        }
    } catch (err) {
        showToast('Network error, please try again.', 'error');
    }
}

// ==================== VOLUNTEER ACTIONS ====================
async function applyForOpportunity(oppId) {
    try {
        const res = await fetch(`/api/apply/${oppId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await res.json();
        if (data.success) {
            showToast(data.message, 'success');
            document.getElementById('opp-modal').classList.remove('active');
            
            // Reload if on opportunities page to update slot counters
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showToast(data.message || 'Could not apply.', 'error');
        }
    } catch (err) {
        showToast('Error sending application.', 'error');
    }
}

async function cancelRegistration(appId) {
    if (!confirm('Are you sure you want to cancel your registration for this shift?')) return;
    
    try {
        const res = await fetch(`/api/cancel-apply/${appId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await res.json();
        if (data.success) {
            showToast(data.message, 'success');
            
            // Fade out item row
            const itemRow = document.getElementById(`app-row-${appId}`);
            if (itemRow) {
                itemRow.style.transition = 'opacity 0.3s ease';
                itemRow.style.opacity = '0';
                setTimeout(() => {
                    itemRow.remove();
                    // If no shifts remain, reload to display empty placeholder
                    window.location.reload();
                }, 300);
            } else {
                window.location.reload();
            }
        } else {
            showToast(data.message || 'Could not cancel shift.', 'error');
        }
    } catch (err) {
        showToast('Network error cancellation failed.', 'error');
    }
}

// ==================== COORDINATOR/ADMIN ACTIONS ====================
async function handleCreateOpportunity(e) {
    e.preventDefault();
    
    const title = document.getElementById('opp-title').value.trim();
    const category = document.getElementById('opp-category').value;
    const date = document.getElementById('opp-date').value;
    const time = document.getElementById('opp-time').value.trim();
    const location = document.getElementById('opp-location').value.trim();
    const skills = document.getElementById('opp-skills').value.trim();
    const max_slots = document.getElementById('opp-max-slots').value;
    const description = document.getElementById('opp-desc').value.trim();
    
    const payload = {
        title, category, date, time, location, skills, max_slots, description
    };
    
    try {
        const res = await fetch('/api/admin/opportunity', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await res.json();
        if (data.success) {
            showToast(data.message, 'success');
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showToast(data.message || 'Could not create event.', 'error');
        }
    } catch (err) {
        showToast('Network error, please try again.', 'error');
    }
}

async function updateAppStatus(appId, newStatus) {
    try {
        const res = await fetch(`/api/admin/application/${appId}/status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
        
        const data = await res.json();
        if (data.success) {
            showToast(data.message, 'success');
            
            // Dynamically update status elements in the row
            const badge = document.getElementById(`status-badge-${appId}`);
            if (badge) {
                badge.innerText = newStatus;
                badge.className = `status-badge ${newStatus.toLowerCase()}`;
            }
            
            // Dynamically update actions buttons cell
            const actionsCell = document.getElementById(`action-cell-${appId}`);
            if (actionsCell) {
                if (newStatus === 'Approved') {
                    actionsCell.innerHTML = `<button onclick="promptLogHours(${appId})" class="btn btn-primary btn-xs">Mark Completed</button>`;
                } else if (newStatus === 'Denied') {
                    actionsCell.innerHTML = `<span class="muted-text">—</span>`;
                }
            }
            
            // Adjust pending counter in header
            const pendingNum = document.getElementById('admin-pending-num');
            if (pendingNum) {
                let count = parseInt(pendingNum.innerText);
                if (count > 0) pendingNum.innerText = count - 1;
            }
        } else {
            showToast(data.message || 'Update status failed.', 'error');
        }
    } catch (err) {
        showToast('Network error.', 'error');
    }
}

function promptLogHours(appId) {
    const hoursModal = document.getElementById('hours-modal');
    if (!hoursModal) return;
    
    document.getElementById('log-app-id').value = appId;
    document.getElementById('logged-hours').value = 2.0; // Reset to default
    hoursModal.classList.add('active');
}

function closeHoursModal() {
    const hoursModal = document.getElementById('hours-modal');
    if (hoursModal) hoursModal.classList.remove('active');
}

async function handleLogHoursSubmit(e) {
    e.preventDefault();
    
    const appId = document.getElementById('log-app-id').value;
    const hours = document.getElementById('logged-hours').value;
    
    try {
        const res = await fetch(`/api/admin/application/${appId}/status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: 'Completed', hours: hours })
        });
        
        const data = await res.json();
        if (data.success) {
            showToast(data.message, 'success');
            closeHoursModal();
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showToast(data.message || 'Logging hours failed.', 'error');
        }
    } catch (err) {
        showToast('Network error.', 'error');
    }
}
