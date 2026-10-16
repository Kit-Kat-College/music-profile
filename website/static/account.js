function changeProfilePicture() {
    const area = document.getElementById("profile-picture-area");
    const button = document.getElementById("profile-picture-button");

    area.style.display = "block";

    button.textContent = "Submit Profile Picture";
    button.type = "submit";
}


function changeUsername() {
    const area = document.getElementById("username-area");
    const button = document.getElementById("username-button");

    area.style.display = "block";

    button.textContent = "Submit Username";
    button.type = "submit";
}


function changeEmail() {
    const area = document.getElementById("email-area");
    const button = document.getElementById("email-button");

    area.style.display = "block";

    button.textContent = "Submit Email";
    button.type = "submit";
}


function changePassword() {
    const area = document.getElementById("password-area");
    const button = document.getElementById("password-button");

    area.style.display = "block";

    button.textContent = "Submit Password";
    button.type = "submit";
}

function deleteAccount() {
    const area = document.getElementById("account-deletion-area");
    const input = document.getElementById("account-deletion");
    const button = document.getElementById("account-deletion-button");

    area.style.display = "block";

    button.textContent = "Confirm Deletion";
    button.type = "submit";

    input.focus();
}


function deleteAlbum() {
    const area = document.getElementById("album-deletion-area");
    const input = document.getElementById("album-deletion");
    const button = document.getElementById("album-deletion-button");

    area.style.display = "block";

    button.textContent = "Confirm Deletion";
    button.type = "submit";

    input.focus();
}


document.addEventListener("DOMContentLoaded", function () {

    const input = document.getElementById("account-deletion");
    const button = document.getElementById("account-deletion-button");

    input.addEventListener("input", function () {

        if (input.value === "DELETE") {

            button.classList.remove("default-color");
            button.classList.add("changed-color");

        } else {

            button.classList.remove("changed-color");
            button.classList.add("default-color");

        }

    });

});

function selectAlbum(id, cover, title, creator, trackCount, creationDate) {

    document.querySelectorAll(".album-row").forEach(row => {
        row.classList.remove("selected"); // Removes the selected style from all albums
    });

    event.currentTarget.classList.add("selected"); // Keeps the clicked album selected

    document.getElementById("selected-album").innerHTML = `
        <div class="sub_album_details">
            <section>
                <div class="sub_cover_container">
                    <img src=${cover} alt="Album Cover" class="sub-cover">
                </div>
            </section>
            <section>
                <p><b>${truncateText(title, 18)}</b></p>
                <p>${truncateText(creator, 17)}</p>
            </section>
        </div>
    `;

    document.getElementById("album-edit-form").style.display = "block";

    document.getElementById("album_id").value = id;

    document.getElementById("title").value = title;
    document.getElementById("creator").value = creator;
    document.getElementById("creation_date").value = creationDate;
    document.getElementById("track_count").value = trackCount;
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) {
        return text;
    }

    return text.substring(0, maxLength - 3) + "...";
}

function deselectAlbum() {

    document.querySelectorAll(".album-row").forEach(album => {
        album.classList.remove("selected");
    });

    document.getElementById("album-edit-form").style.display = "none";

    document.getElementById("selected-album").innerHTML = `
        <p class="none_selected">No album selected</p>
    `;

    document.getElementById("album_id").value = "";

    document.getElementById("title").value = "";
    document.getElementById("creator").value = "";
    document.getElementById("creation_date").value = "";
    document.getElementById("track_count").value = "";
}





document.addEventListener("DOMContentLoaded", () => {
    const flashes = document.querySelectorAll(".flash");

    flashes.forEach(flash => {
        setTimeout(() => {
            flash.style.transition = "opacity 0.5s ease";
            flash.style.opacity = "0";

            setTimeout(() => {
                flash.remove();
            }, 500);
        }, 5000);
    });
});
