function toggleForm() {
    var modal = document.getElementById("formModal");
    closeOtherModals(modal);
    modal.classList.toggle("hidden");
    modal.classList.toggle("show");
}

function toggleEditForm() {
    var modal = document.getElementById("editModal");
    closeOtherModals(modal);
    modal.classList.toggle("hidden");
    modal.classList.toggle("show");
}

function closeOtherModals(activeModal) {
    var modals = [document.getElementById("formModal"), document.getElementById("editModal")];
    modals.forEach(modal => {
        // Only close modals that are not the active one
        if (modal !== activeModal && !modal.classList.contains("hidden")) {
            modal.classList.add("hidden");
            modal.classList.remove("show");
        }
    });
}

function openEditForm(idNumber, firstName, lastName, courseCode, year, gender) {
    // Ensure the modal is visible before populating the form fields
    toggleEditForm();

    // Populate the edit form fields with the existing student data
    document.getElementById("editIdNumber").value = idNumber;
    document.getElementById("editFirstName").value = firstName;
    document.getElementById("editLastName").value = lastName;
    document.getElementById("editCourseInput").value = courseCode;
    document.getElementById("editYear").value = year;
    document.getElementById("editGender").value = gender;

    // Dynamically update the form action to include the correct idNumber
    document.getElementById("edit-student-form").action = `/edit_student/${idNumber}`;
}

function confirmDelete() {
    return confirm("Are you sure you want to delete this student?");
}

function confirmUpdate() {
    return confirm("Are you sure you want to update this student?");
}
function validateImageUpload(input) {
    const file = input.files[0];
    if (!file) {
        alert("Please select a file.");
        return false;
    }

    const allowedTypes = ["image/jpeg", "image/png", "image/jpg"];
    const maxSizeMB = 25;
    const maxSizeBytes = maxSizeMB * 1024 * 1024;

    if (!allowedTypes.includes(file.type)) {
        alert("Only JPEG and PNG files are allowed.");
        input.value = ""; // Clear the input
        return false;
    }

    if (file.size > maxSizeBytes) {
        alert(`File size must be less than ${maxSizeMB} MB.`);
        input.value = ""; // Clear the input
        return false;
    }

    return true;
}
