let sideBar = document.getElementById("sidebar");
let menuIcon = document.getElementById("menu-icon");
sideBar.style.width = "30px";

menuIcon.addEventListener("click", () => {
    if (sideBar.style.width == "30px") {
        sideBar.style.width = "180px";
    }
    else {
        sideBar.style.width = "30px";
    }
});