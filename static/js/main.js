document.addEventListener("DOMContentLoaded", () => {
    // Mobile nav toggle
    const navToggle = document.querySelector(".nav-toggle");
    const sidebar = document.querySelector(".sidebar");

    if (navToggle) {
        navToggle.addEventListener("click", () => {
            sidebar.classList.toggle("open");
        });
    }

    // Task checkbox toggle
    const taskCheckboxes = document.querySelectorAll(".task-card input[type='checkbox']");
    taskCheckboxes.forEach(checkbox => {
        checkbox.addEventListener("change", (e) => {
            const task = e.target.closest(".task-card");
            if (task) {
                if (e.target.checked) {
                    task.classList.add("completed");
                } else {
                    task.classList.remove("completed");
                }
            }
        });
    });

    // Edit task rows
    const editButtons = document.querySelectorAll(".edit-task");
    editButtons.forEach(button => {
        button.addEventListener("click", () => {
            const taskId = button.dataset.taskId;
            const taskCard = button.closest(".task-card");
            if (!taskCard) return;
            const editForm = taskCard.querySelector(".task-edit-form");
            if (editForm) {
                editForm.classList.toggle("hidden");
            }
        });
    });

    const cancelButtons = document.querySelectorAll(".cancel-edit");
    cancelButtons.forEach(button => {
        button.addEventListener("click", () => {
            const taskCard = button.closest(".task-card");
            if (!taskCard) return;
            const editForm = taskCard.querySelector(".task-edit-form");
            if (editForm) {
                editForm.classList.add("hidden");
            }
        });
    });

    // Delete confirmation for task list
    const deleteButtons = document.querySelectorAll(".task-delete-form button");
    deleteButtons.forEach(button => {
        button.addEventListener("click", (e) => {
            if (!confirm("Are you sure you want to delete this task?")) {
                e.preventDefault();
            }
        });
    });

    // Image upload preview
    const fileInput = document.querySelector("input[name='image']");
    const previewSection = document.querySelector(".upload-preview");
    const previewImage = document.querySelector(".preview-image");
    const previewTitle = document.querySelector("#preview-title");
    const previewSubject = document.querySelector("#preview-subject");
    const titleInput = document.querySelector("input[name='title']");
    const subjectInput = document.querySelector("input[name='subject']");

    if (fileInput && previewSection && previewImage) {
        const updatePreviewText = () => {
            previewTitle.textContent = titleInput.value.trim() || 'Note preview';
            previewSubject.textContent = subjectInput.value.trim() ? `Subject: ${subjectInput.value.trim()}` : 'Subject: General';
        };

        fileInput.addEventListener("change", (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    previewImage.style.backgroundImage = `url('${event.target.result}')`;
                    previewSection.classList.remove("hidden");
                    updatePreviewText();
                };
                reader.readAsDataURL(file);
            }
        });

        if (titleInput) {
            titleInput.addEventListener("input", updatePreviewText);
        }
        if (subjectInput) {
            subjectInput.addEventListener("input", updatePreviewText);
        }
    }

    // Like button toggle
    const likeButtons = document.querySelectorAll(".journal-card .actions button:first-child");
    likeButtons.forEach(button => {
        button.addEventListener("click", () => {
            button.classList.toggle("liked");
        });
    });

    // Active navigation state
    const navLinks = document.querySelectorAll(".sidebar nav ul li a");
    navLinks.forEach(link => {
        if (link.href === window.location.href) {
            link.classList.add("active");
        }
    });
});