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
    const taskCheckboxes = document.querySelectorAll(".task input[type='checkbox']");
    taskCheckboxes.forEach(checkbox => {
        checkbox.addEventListener("change", (e) => {
            const task = e.target.closest(".task");
            if (e.target.checked) {
                task.classList.add("completed");
            } else {
                task.classList.remove("completed");
            }
        });
    });

    // Delete confirmation
    const deleteButtons = document.querySelectorAll(".task button:last-child");
    deleteButtons.forEach(button => {
        button.addEventListener("click", () => {
            if (confirm("Are you sure you want to delete this task?")) {
                button.closest(".task").remove();
            }
        });
    });

    // Image upload preview
    const fileInput = document.querySelector("input[type='file']");
    const previewArea = document.querySelector(".note-grid");

    if (fileInput && previewArea) {
        fileInput.addEventListener("change", (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    const newCard = document.createElement("div");
                    newCard.classList.add("note-card");
                    newCard.innerHTML = `
                        <div class="image-placeholder" style="background-image: url('${event.target.result}')"></div>
                        <h2>New Note</h2>
                        <p>Subject: Unknown</p>
                        <p>Uploaded: Just now</p>
                        <button>Preview</button>
                        <button>Download</button>
                    `;
                    previewArea.appendChild(newCard);
                };
                reader.readAsDataURL(file);
            }
        });
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