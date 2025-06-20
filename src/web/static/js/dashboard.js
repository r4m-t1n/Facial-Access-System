function showMainTab(id) {
    document.querySelectorAll('.main-tab-content').forEach(el => el.classList.remove('active'));
    const tab = document.getElementById('main-tab-' + id);
    if (tab) {
        tab.classList.add('active');
    } else {
        console.warn(`Main tab with ID 'main-tab-${id}' not found.`);
    }
}

function showMemberSubTab(id) {
    showMainTab('members'); 

    document.querySelectorAll('.sub-tab-content').forEach(el => el.classList.remove('active'));
    const subTab = document.getElementById('sub-tab-' + id);
    if (subTab) {
        subTab.classList.add('active');
    } else {
        console.warn(`Sub-tab with ID 'sub-tab-${id}' not found.`);
    }
}

function openLiveCamera() {
    window.location.href = '/live-camera';
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('add-member-form');
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            const name = document.getElementById('new_member_name').value.trim();
            if (!name) {
                alert('Member name cannot be empty.');
                return;
            }

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
                        showMemberSubTab(name); 
                    };
                    const hrs = document.querySelectorAll('#sidebar hr');
                    if (hrs.length >= 2) {
                        document.getElementById('sidebar').insertBefore(btn, hrs[1]);
                    } else {
                        document.getElementById('sidebar').appendChild(btn);
                    }


                    const membersMainTabDiv = document.getElementById('main-tab-members');
                    const div = document.createElement('div');
                    div.id = `sub-tab-${name}`;
                    div.className = 'sub-tab-content';
                    div.innerHTML = `
                        <h2>${name}</h2>
                        <button onclick="deleteMember('${name}')">Delete Member</button>
                        <form id="upload-form-${name}" enctype="multipart/form-data">
                            <input type="hidden" name="member" value="${name}">
                            <input type="file" name="photos" accept="image/*" multiple required>
                            <button type="button" onclick="uploadPhotos('${name}')">Upload Photo</button>
                        </form>
                        <div id="photos-${name}"></div>
                    `;
                    const addSubTab = document.getElementById('sub-tab-add');
                    if (membersMainTabDiv && addSubTab) {
                        membersMainTabDiv.insertBefore(div, addSubTab);
                    } else if (membersMainTabDiv) {
                        membersMainTabDiv.appendChild(div);
                    }

                    showMemberSubTab(name);
                    document.getElementById('new_member_name').value = '';

                    alert(result.message);
                } else {
                    alert(result.message);
                }
            } catch (error) {
                alert(`Error: ${error.message}`);
            }
        });
    }
});

async function uploadPhotos(member) {
    const form = document.getElementById(`upload-form-${member}`);
    const filesInput = form.querySelector('input[type="file"]');
    const uploadButton = form.querySelector('button[type="button"]');

    if (!filesInput || !filesInput.files.length) {
        alert('Please select files to upload.');
        return;
    }

    uploadButton.disabled = true;
    uploadButton.textContent = 'Uploading...';

    const formData = new FormData(form);
    formData.append('member', member);

    try {
        const response = await fetch('/upload-photo', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            alert(result.message);
            filesInput.value = '';
        } else {
            alert(`Upload failed: ${result.message}`);
        }
    } catch (error) {
        alert(`Error during upload: ${error.message}`);
    } finally {
        uploadButton.disabled = false;
        uploadButton.textContent = 'Upload Photo';
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
            alert('Member deleted successfully!');
            location.reload();
        } else {
            alert(`Failed to delete member: ${result.message}`);
        }
    } catch (error) {
        alert(`Error during deletion: ${error.message}`);
    }
}

async function loadAssignPhotos() {
    const container = document.getElementById('assign-photos-container');
    container.innerHTML = 'Loading...';

    const response = await fetch('/captured-photos');
    const result = await response.json();

    const members = await fetch('/members').then(res => res.json());

    container.innerHTML = '';

    result.photos.forEach(photo => {
        const photoBox = document.createElement('div');
        photoBox.style.border = '1px solid #ccc';
        photoBox.style.padding = '10px';
        photoBox.style.textAlign = 'center';
        photoBox.innerHTML = `
            <img src="/captured_photos/${photo}" width="150"><br>
            <select id="select-${photo}">
                ${members.members.map(m => `<option value="${m}">${m}</option>`).join('')}
            </select><br>
            <button class="assign-btn" onclick="assignPhoto('${photo}')">Assign</button>
            <button class="delete-btn" onclick="deletePhoto('${photo}')">Delete</button>
        `;

        container.appendChild(photoBox);
    });
}

async function assignPhoto(filename) {
    const button = event.target;
    button.disabled = true;
    button.innerText = 'Loading...';

    const select = document.getElementById(`select-${filename}`);
    const member = select.value;

    const formData = new FormData();
    formData.append('member', member);
    formData.append('filename', filename);

    try {
        const response = await fetch('/assign-photo', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        alert(result.message)

        button.parentElement.remove();
    } catch (error) {

        alert(`Error: ${error.message}`);

    } finally {

        button.disabled = false;
        button.innerText = 'Assign';

    }
}

async function deletePhoto(filename) {
    const confirmDelete = confirm("Are you sure you want to delete this photo?");
    if (!confirmDelete) return;

    try {
        const response = await fetch('/delete-photo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename })
        });
        const result = await response.json();
        alert(result.message);
    } catch (error) {
        alert(`Error: ${error.message}`);
    } finally {
        loadAssignPhotos();
    }
}