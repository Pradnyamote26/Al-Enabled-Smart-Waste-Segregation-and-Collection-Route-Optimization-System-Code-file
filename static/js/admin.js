document.addEventListener('DOMContentLoaded', () => {
    checkAdminSession();
});

async function checkAdminSession() {
    try {
        const response = await fetch('/api/auth/me');
        const data = await response.json();

        if (data.authenticated && data.user.role === 'admin') {
            showAdminDashboard(data.user);
        } else {
            showAdminLogin();
        }
    } catch (err) {
        showAdminLogin();
    }
}

function showAdminLogin() {
    document.getElementById('adminLoginView').classList.remove('hidden');
    document.getElementById('adminDashboardView').classList.add('hidden');
}

function showAdminDashboard(user) {
    document.getElementById('adminLoginView').classList.add('hidden');
    document.getElementById('adminDashboardView').classList.remove('hidden');
    document.getElementById('adminSessionName').textContent = `Admin: ${user.username}`;
    
    loadAdminStats();
    loadAdminUsers();
}

async function handleAdminLogin(e) {
    e.preventDefault();
    const username = document.getElementById('adminUsername').value;
    const password = document.getElementById('adminPassword').value;

    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username_or_email: username, password: password })
        });

        const data = await response.json();

        if (data.success) {
            if (data.user.role !== 'admin') {
                alert('Access denied: Account is not an Admin user.');
                return;
            }
            showAdminDashboard(data.user);
        } else {
            alert('Login failed: ' + data.message);
        }
    } catch (err) {
        alert('Server communication error: ' + err.message);
    }
}



async function handleAdminLogout() {
    await fetch('/api/auth/logout', { method: 'POST' });
    showAdminLogin();
}

async function loadAdminStats() {
    try {
        const res = await fetch('/api/admin/stats');
        const data = await res.json();
        if (data.success) {
            document.getElementById('adminUsersCount').textContent = data.counts.users;
            document.getElementById('adminDetectionsCount').textContent = data.counts.detections;
            document.getElementById('adminCategoriesCount').textContent = data.counts.categories;
            document.getElementById('adminLocationsCount').textContent = data.counts.locations;
        }
    } catch (err) {
        console.error(err);
    }
}

function switchAdminTab(tabName) {
    const tabs = ['users', 'detections', 'categories', 'locations', 'routes'];
    tabs.forEach(t => {
        const tabEl = document.getElementById(`admin${capitalize(t)}Tab`);
        const btnEl = document.getElementById(`tab${capitalize(t)}Btn`);
        if (t === tabName) {
            tabEl.classList.remove('hidden');
            btnEl.classList.add('active');
        } else {
            tabEl.classList.add('hidden');
            btnEl.classList.remove('active');
        }
    });

    if (tabName === 'users') loadAdminUsers();
    if (tabName === 'detections') loadAdminDetections();
    if (tabName === 'categories') loadAdminCategories();
    if (tabName === 'locations') loadAdminLocations();
    if (tabName === 'routes') loadAdminRoutes();
}

function capitalize(s) {
    return s.charAt(0).toUpperCase() + s.slice(1);
}

// 1. Users Data Table
async function loadAdminUsers() {
    const tbody = document.getElementById('usersTableBody');
    const res = await fetch('/api/admin/users');
    const data = await res.json();
    if (data.success) {
        tbody.innerHTML = data.users.map(u => `
            <tr>
                <td>#${u.id}</td>
                <td><strong>${u.username}</strong></td>
                <td>${u.email}</td>
                <td><span class="role-badge role-${u.role}">${u.role}</span></td>
                <td>${u.created_at}</td>
                <td><button onclick="deleteUser(${u.id})" class="btn-delete">🗑️ Delete</button></td>
            </tr>
        `).join('');
    }
}

async function deleteUser(id) {
    if (!confirm('Are you sure you want to delete this user?')) return;
    const res = await fetch(`/api/admin/users/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.success) {
        loadAdminUsers();
        loadAdminStats();
    } else {
        alert(data.message);
    }
}

// 2. Detections Data Table
async function loadAdminDetections() {
    const tbody = document.getElementById('detectionsTableBody');
    const res = await fetch('/api/admin/detections');
    const data = await res.json();
    if (data.success) {
        tbody.innerHTML = data.detections.map(d => `
            <tr>
                <td>#${d.id}</td>
                <td><img src="${d.image_path}" class="thumb-img"></td>
                <td><strong>${d.category_name}</strong></td>
                <td>${d.waste_type}</td>
                <td><span class="badge-${d.bin_color.toLowerCase()}">${d.bin_color} Bin</span></td>
                <td>${(d.confidence_score * 100).toFixed(1)}%</td>
                <td>${d.user_id ? `User #${d.user_id}` : 'Guest'}</td>
                <td>${d.detected_at}</td>
                <td><button onclick="deleteDetection(${d.id})" class="btn-delete">🗑️ Delete</button></td>
            </tr>
        `).join('');
    }
}

async function deleteDetection(id) {
    if (!confirm('Are you sure you want to delete this detection record?')) return;
    await fetch(`/api/admin/detections/${id}`, { method: 'DELETE' });
    loadAdminDetections();
    loadAdminStats();
}

// 3. Categories Data Table
async function loadAdminCategories() {
    const tbody = document.getElementById('categoriesTableBody');
    const res = await fetch('/api/admin/categories');
    const data = await res.json();
    if (data.success) {
        tbody.innerHTML = data.categories.map(c => `
            <tr>
                <td>#${c.id}</td>
                <td><strong>${c.category_name}</strong></td>
                <td>${c.waste_type}</td>
                <td><span class="badge-${c.recommended_bin_color.toLowerCase()}">${c.recommended_bin_color} Bin</span></td>
                <td>${c.disposal_suggestion}</td>
                <td><button onclick="deleteCategory(${c.id})" class="btn-delete">🗑️ Delete</button></td>
            </tr>
        `).join('');
    }
}

function toggleCategoryModal() {
    document.getElementById('addCategoryModal').classList.toggle('hidden');
}

async function handleAddCategory(e) {
    e.preventDefault();
    const name = document.getElementById('catName').value;
    const type = document.getElementById('catType').value;
    const color = document.getElementById('catColor').value;
    const suggestion = document.getElementById('catSuggestion').value;

    const res = await fetch('/api/admin/categories', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            category_name: name,
            waste_type: type,
            recommended_bin_color: color,
            disposal_suggestion: suggestion
        })
    });

    const data = await res.json();
    if (data.success) {
        toggleCategoryModal();
        loadAdminCategories();
        loadAdminStats();
    } else {
        alert(data.message);
    }
}

async function deleteCategory(id) {
    if (!confirm('Are you sure you want to delete this category?')) return;
    await fetch(`/api/admin/categories/${id}`, { method: 'DELETE' });
    loadAdminCategories();
    loadAdminStats();
}

// 4. Locations Data Table
async function loadAdminLocations() {
    const tbody = document.getElementById('locationsTableBody');
    const res = await fetch('/api/admin/locations');
    const data = await res.json();
    if (data.success) {
        tbody.innerHTML = data.locations.map(l => `
            <tr>
                <td>#${l.id}</td>
                <td><strong>${l.location_name}</strong></td>
                <td>(${l.latitude.toFixed(4)}, ${l.longitude.toFixed(4)})</td>
                <td><span class="fill-pill fill-${l.current_fill_level >= 90 ? 'red' : (l.current_fill_level >= 60 ? 'yellow' : 'green')}">${l.current_fill_level}%</span></td>
                <td>${l.current_weight_kg} kg</td>
                <td>Priority ${l.priority}/5</td>
                <td>${l.status}</td>
                <td><button onclick="deleteAdminLocation(${l.id})" class="btn-delete">🗑️ Delete</button></td>
            </tr>
        `).join('');
    }
}

async function deleteAdminLocation(id) {
    if (!confirm('Delete this collection location?')) return;
    await fetch(`/api/admin/locations/${id}`, { method: 'DELETE' });
    loadAdminLocations();
    loadAdminStats();
}

// 5. Routes Data Table
async function loadAdminRoutes() {
    const tbody = document.getElementById('routesTableBody');
    const res = await fetch('/api/admin/routes');
    const data = await res.json();
    if (data.success) {
        tbody.innerHTML = data.routes.map(r => `
            <tr>
                <td>#${r.id}</td>
                <td><strong>${r.route_name}</strong></td>
                <td>${r.total_distance_km} km</td>
                <td>${r.estimated_time_mins} mins</td>
                <td>${r.fuel_used_liters} L</td>
                <td>${r.visited_bins_count} Bins</td>
                <td>${r.created_at}</td>
                <td><button onclick="deleteRouteLog(${r.id})" class="btn-delete">🗑️ Delete</button></td>
            </tr>
        `).join('');
    }
}

async function deleteRouteLog(id) {
    if (!confirm('Delete this route log?')) return;
    await fetch(`/api/admin/routes/${id}`, { method: 'DELETE' });
    loadAdminRoutes();
}
