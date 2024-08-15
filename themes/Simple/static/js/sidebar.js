document.getElementById("scrollToTopButton").addEventListener("click", function(event) {
if (window.matchMedia("(min-width: 768px)").matches) {
  event.preventDefault();
}
else{
window.scrollTo({ top: 0, behavior: "smooth" });
}
});




const currentLink = new URL(window.location.href).pathname; // Get path without extension

const links = document.querySelectorAll('.main-link');


links.forEach(link => {
  const linkPath = new URL(link.href).pathname; // Get link path without extension
  console.log(linkPath);
  if (linkPath === currentLink) {
    link.classList.add('active');
  }
});





document.addEventListener('DOMContentLoaded', function() {
  const toggleButton = document.getElementById('scrollToTopButton');
  const targetElement = document.getElementById('navbarTogglerDemo04');

  // Initially set the target element to hidden or collapsed (adjust CSS if needed)
  targetElement.classList.add('show'); // Bootstrap collapse class

  toggleButton.addEventListener('show', function() {
    targetElement.classList.toggle('show'); // Bootstrap show class for visibility
  });
});




var TxtType = function(el, toRotate, period) {
  this.toRotate = toRotate;
  this.el = el;
  this.loopNum = 0;
  this.period = parseInt(period, 10) || 2000;
  this.txt = '';
  this.tick();
  this.isDeleting = false;
};

TxtType.prototype.tick = function() {
  var i = this.loopNum % this.toRotate.length;
  var fullTxt = this.toRotate[i];

  if (this.isDeleting) {
  this.txt = fullTxt.substring(0, this.txt.length - 1);
  } else {
  this.txt = fullTxt.substring(0, this.txt.length + 1);
  }

  this.el.innerHTML = '<span class="wrap">'+this.txt+'</span>';

  var that = this;
  var delta = 200 - Math.random() * 100;

  if (this.isDeleting) { delta /= 2; }

  if (!this.isDeleting && this.txt === fullTxt) {
  delta = this.period;
  this.isDeleting = true;
  } else if (this.isDeleting && this.txt === '') {
  this.isDeleting = false;
  this.loopNum++;
  delta = 500;
  }

  setTimeout(function() {
  that.tick();
  }, delta);
};

window.onload = function() {
  var elements = document.getElementsByClassName('typewrite');
  for (var i=0; i<elements.length; i++) {
      var toRotate = elements[i].getAttribute('data-type');
      var period = elements[i].getAttribute('data-period');
      if (toRotate) {
        new TxtType(elements[i], JSON.parse(toRotate), period);
      }
  }
  // INJECT CSS
  var css = document.createElement("style");
  css.type = "text/css";
  css.innerHTML = ".typewrite > .wrap { border-right: 0.08em solid #fff}";
  document.body.appendChild(css);
};