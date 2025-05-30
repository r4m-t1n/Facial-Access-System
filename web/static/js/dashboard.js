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
            btn.onclick = () => showTab(name);
            document.getElementById('sidebar').insertBefore(btn, document.querySelector('#sidebar hr'));

            const div = document.createElement('div');
            div.id = `tab-${name}`;
            div.className = 'tab-content';
            div.innerHTML = `
                <h2>${name}</h2>
                <form method="post" action="/delete-member">
                    <input type="hidden" name="member" value="${name}">
                    <button type="submit">Delete Member</button>
                </form>
                <form method="post" action="/upload-photo" enctype="multipart/form-data">
                    <input type="hidden" name="member" value="${name}">
                    <input type="file" name="photos" accept="image/*" multiple required>
                    <button type="submit">Upload Photo</button>
                </form>
            `;
            document.getElementById('main').appendChild(div);

            showTab(name);

            document.getElementById('new_member_name').value = '';
        } else {
            alert("Failed to add member.\nThis member may already exist.");
        }
    });
});

document.querySelectorAll('.upload-form').forEach(form => {
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const member = form.dataset.member;
        const input = form.querySelector('input[type="file"]');

        if (!input.files.length) {
            alert("Please select at least one file.");
            return;
        }

        const formData = new FormData();
        formData.append('member', member);

        for (const file of input.files) {
            formData.append('photos', file);
        }

        const response = await fetch('/upload-photo', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            if (data.status === "success") {
                window.location.href = "/";
            }
            } else {
                alert("Upload failed");
            }

        return false;
    });
});

document.querySelectorAll('.delete-form').forEach(form => {
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        const member = form.dataset.member;
        if (!confirm(`Are you sure you want to delete "${member}"?`)) return;

        const formData = new FormData();
        formData.append('member', member);

        const response = await fetch('/delete-member', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            if (data.status === "success") {
                window.location.href = "/";
            }
            } else {
                alert("Upload failed");
            }

        return false;
    });
});
