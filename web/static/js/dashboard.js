function showTab(id) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    const tab = document.getElementById('tab-' + id);
    if (tab) tab.classList.add('active');
}

async function loadPhotos(member) {
    try {
        const response = await fetch(`/get-photos?member=${encodeURIComponent(member)}`);
        if (response.ok) {
            const photos = await response.json();
            const container = document.getElementById(`photos-${member}`);
            if (container) {
                container.innerHTML = photos.map(photo => 
                    `<img src="/photos/${member}/${photo}" alt="${photo}" style="max-width: 200px; margin: 5px;">`
                ).join('');
            }
        }
    } catch (error) {
        console.error('Error loading photos:', error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('add-member-form');
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        const name = document.getElementById('new_member_name').value.trim();
        if (!name) return;

        try {
            const response = await fetch('/add-member', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ new_member: name })
            });

            if (response.ok) {
                const btn = document.createElement('button');
                btn.textContent = name;
                btn.onclick = () => {
                    showTab(name);
                    loadPhotos(name);
                };
                document.getElementById('sidebar').insertBefore(btn, document.querySelector('#sidebar hr'));

                const div = document.createElement('div');
                div.id = `tab-${name}`;
                div.className = 'tab-content';
                div.innerHTML = `
                    <h2>${name}</h2>
                    <form method="post" action="/delete-member" onsubmit="return confirm('Are you sure you want to delete ${name}?')">
                        <input type="hidden" name="member" value="${name}">
                        <button type="submit">Delete Member</button>
                    </form>
                    <form method="post" action="/upload-photo" enctype="multipart/form-data" id="upload-form-${name}">
                        <input type="hidden" name="member" value="${name}">
                        <input type="file" name="photos" accept="image/*" multiple required>
                        <button type="submit">Upload Photo</button>
                    </form>
                    <div id="photos-${name}"></div>
                `;
                document.getElementById('main').appendChild(div);

                showTab(name);
                document.getElementById('new_member_name').value = '';

                loadPhotos(name);
            } else {
                const error = await response.text();
                alert(`Failed to add member: ${error}`);
            }
        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    });

    const activeTab = document.querySelector('.tab-content.active');
    if (activeTab && activeTab.id !== 'tab-add') {
        const member = activeTab.id.replace('tab-', '');
        loadPhotos(member);
    }

    document.querySelectorAll('form[action="/upload-photo"]').forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const member = formData.get('member');
            
            try {
                const response = await fetch('/upload-photo', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    alert('Photos uploaded successfully!');
                    loadPhotos(member);
                } else {
                    const error = await response.text();
                    alert(`Upload failed: ${error}`);
                }
            } catch (error) {
                alert(`Error: ${error.message}`);
            }
        });
    });
});

window.history.replaceState({}, document.title, "/dashboard");