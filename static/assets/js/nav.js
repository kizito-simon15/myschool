/**
 * Navigation Script for St. Theresa of Avila Secondary School
 * Updated: June 15, 2025
 * Purpose: Enhance mobile toggle, sticky header, smooth scrolling, active state, and Read More functionality
 */

document.addEventListener("DOMContentLoaded", () => {
  // Mobile Navigation Toggle
  const mobileNavToggle = document.querySelector(".mobile-nav-toggle");
  const offcanvasNav = document.querySelector("#offcanvasNav");
  const navLinks = offcanvasNav ? offcanvasNav.querySelectorAll(".nav-link") : [];

  if (mobileNavToggle && offcanvasNav) {
    mobileNavToggle.addEventListener("click", () => {
      const isOpen = offcanvasNav.classList.contains("show");
      offcanvasNav.classList.toggle("show");
      mobileNavToggle.classList.toggle("active");
      offcanvasNav.style.transition = "transform 0.3s ease";
      if (isOpen) {
        offcanvasNav.style.transform = "translateX(100%)";
      } else {
        offcanvasNav.style.transform = "translateX(0)";
      }
    });

    // Close offcanvas and handle active state on link click
    navLinks.forEach(link => {
      link.addEventListener("click", (e) => {
        const href = link.getAttribute("href");
        if (href && href.startsWith("#")) {
          e.preventDefault();
          const target = document.querySelector(href);
          if (target) {
            target.scrollIntoView({ behavior: "smooth" });
            const bootstrap = window.bootstrap;
            if (bootstrap && offcanvasNav.classList.contains("show")) {
              const offcanvas = new bootstrap.Offcanvas(offcanvasNav);
              offcanvas.hide();
              mobileNavToggle.classList.remove("active");
              offcanvasNav.style.transform = "translateX(100%)";
              // Update active state in offcanvas
              navLinks.forEach(l => l.classList.remove("active"));
              link.classList.add("active");
            }
          }
        }
      });
    });
  }

  // Sticky Header
  const header = document.querySelector(".header");
  if (header) {
    window.addEventListener("scroll", () => {
      if (window.scrollY > 50) {
        header.classList.add("scrolled");
      } else {
        header.classList.remove("scrolled");
      }
    });
  }

  // Smooth Scroll for Navigation Links
  const navMenu = document.querySelector("#navmenu");
  if (navMenu) {
    navMenu.querySelectorAll("a").forEach(anchor => {
      anchor.addEventListener("click", function (e) {
        if (this.hash && this.hash !== "#") {
          e.preventDefault();
          const target = document.querySelector(this.hash);
          if (target) {
            target.scrollIntoView({ behavior: "smooth" });
            // Update active state on desktop
            navMenu.querySelectorAll("a").forEach(a => a.classList.remove("active"));
            this.classList.add("active");
            // Handle mobile offcanvas close if open
            if (window.innerWidth <= 991 && offcanvasNav && offcanvasNav.classList.contains("show")) {
              const bootstrap = window.bootstrap;
              if (bootstrap) {
                const offcanvas = new bootstrap.Offcanvas(offcanvasNav);
                offcanvas.hide();
                mobileNavToggle.classList.remove("active");
                offcanvasNav.style.transform = "translateX(100%)";
                // Update mobile active state
                const mobileLink = offcanvasNav.querySelector(`a[href="${this.hash}"]`);
                if (mobileLink) {
                  navLinks.forEach(l => l.classList.remove("active"));
                  mobileLink.classList.add("active");
                }
              }
            }
          }
        }
      });
    });
  }

  // Highlight Active Section on Scroll
  const sections = document.querySelectorAll("section");
  window.addEventListener("scroll", () => {
    let currentSection = "";
    sections.forEach(section => {
      const sectionTop = section.offsetTop - 100;
      if (window.scrollY >= sectionTop) {
        currentSection = section.getAttribute("id");
      }
    });
    if (navMenu) {
      navMenu.querySelectorAll("a").forEach(a => {
        a.classList.remove("active");
        if (a.getAttribute("href") === `#${currentSection}`) {
          a.classList.add("active");
        }
      });
    }
    if (offcanvasNav) {
      offcanvasNav.querySelectorAll(".nav-link").forEach(l => {
        l.classList.remove("active");
        if (l.getAttribute("href") === `#${currentSection}`) {
          l.classList.add("active");
        }
      });
    }
  });

  // Read More Functionality for Departments
  const readMoreButtons = document.querySelectorAll(".read-more");
  readMoreButtons.forEach(button => {
    const p = button.parentElement;
    button.addEventListener("click", () => {
      if (button.textContent === "Read More") {
        p.classList.add("expanded");
        p.innerHTML = button.getAttribute("data-full-text") + ' <span class="read-more">Read Less</span>';
      } else {
        p.classList.remove("expanded");
        const shortText = p.innerHTML.split('<span class="read-more">')[0].trim();
        p.innerHTML = shortText + ' <span class="read-more" data-full-text="' + button.getAttribute("data-full-text") + '">Read More</span>';
      }
    });
  });
});
