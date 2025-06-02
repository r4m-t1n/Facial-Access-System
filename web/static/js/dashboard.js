function showTab(id) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    const tab = document.getElementById('tab-' + id);
    if (tab) tab.classList.add('active');
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

            const result = await response.json();
            
            if (response.ok) {
                const btn = document.createElement('button');
                btn.textContent = name;
                btn.onclick = () => {
                    showTab(name);
                };
                document.getElementById('sidebar').insertBefore(btn, document.querySelector('#sidebar hr'));

                const div = document.createElement('div');
                div.id = `tab-${name}`;
                div.className = 'tab-content';
                div.innerHTML = `
                    <h2>${name}</h2>
                    <button onclick="deleteMember('${name}')">Delete Member</button>
                    <form id="upload-form-${name}" enctype="multipart/form-data">
                        <input type="file" name="photos" accept="image/*" multiple required>
                        <button type="button" onclick="uploadPhotos('${name}')">Upload Photo</button>
                    </form>
                    <div id="photos-${name}"></div>
                `;
                document.getElementById('main').appendChild(div);

                showTab(name);
                document.getElementById('new_member_name').value = '';
                
                alert(result.message || 'Member added successfully!');
            } else {
                alert(result.message || 'Failed to add member', 'error');
            }
        } catch (error) {
            alert(`Error: ${error.message}`, 'error');
        }
    });
});

async function uploadPhotos(member) {
    const form = document.getElementById(`upload-form-${member}`);
    const formData = new FormData(form);
    formData.append('member', member);

    try {
        const response = await fetch('/upload-photo', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            alert('Files uploaded successfully!');
        } else {
            console.error('Upload failed:', result.message);
        }
    } catch (error) {
        console.error('Error:', error.message);
    }
}

async function deleteMember(member) {
    if (!confirm(`Are you sure you want to delete ${member}?`)) return;

    try {
        const response = await fetch('/delete-member', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `member=${encodeURIComponent(member)}`
        });

        const result = await response.json();

        if (response.ok) {
            location.reload()
        } else {
            console.error('Failed to delete member:', result.message);
        }
    } catch (error) {
        console.error('Error:', error.message);
    }
}

window.history.replaceState({}, document.title, "/dashboard");
