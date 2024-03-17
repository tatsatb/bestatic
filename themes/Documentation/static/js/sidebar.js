document.getElementById("scrollToTopButton").addEventListener("click", function(event) {
if (window.matchMedia("(min-width: 768px)").matches) {
  event.preventDefault();
}
else{
window.scrollTo({ top: 0, behavior: "smooth" });
}
});



const currentLink = window.location.pathname; // Get current URL path

const links = document.querySelectorAll('.side-link'); // Select all links

links.forEach(link => {
  if (link.href.endsWith(currentLink)) {
    link.classList.add('active'); // Add 'active' class to matching link
  }
});