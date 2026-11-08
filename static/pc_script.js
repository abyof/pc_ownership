const Toggle = document.querySelector(".nav-toggle");
const navItems = document.querySelector(".nav-items");
Toggle.addEventListener("click", function(){
    navItems.classList.toggle("active");
})
