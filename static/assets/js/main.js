/**
 * Main Script for St. Theresa of Avila Secondary School
 * Updated: June 22, 2025 with Bootstrap v5.3.3
 * Author: Adapted from BootstrapMade.com's Dewi template
 * License: https://bootstrapmade.com/license/
 */

(function() {
  "use strict";

  /**
   * Apply .scrolled class to the body as the page is scrolled down
   */
  function toggleScrolled() {
    const selectBody = document.querySelector('body');
    const selectHeader = document.querySelector('#header');
    if (!selectHeader || (!selectHeader.classList.contains('scroll-up-sticky') && !selectHeader.classList.contains('sticky-top') && !selectHeader.classList.contains('fixed-top'))) return;
    window.scrollY > 100 ? selectBody.classList.add('scrolled') : selectBody.classList.remove('scrolled');
  }

  document.addEventListener('scroll', toggleScrolled);
  window.addEventListener('load', toggleScrolled);

  /**
   * Scroll Progress Bar
   */
  function toggleScrollProgress() {
    const progressBar = document.createElement('div');
    progressBar.classList.add('scroll-progress');
    document.body.appendChild(progressBar);
    window.addEventListener('scroll', () => {
      let scrollTop = window.scrollY;
      let docHeight = document.documentElement.scrollHeight - window.innerHeight;
      let scrollPercent = (scrollTop / docHeight) * 100;
      progressBar.style.width = scrollPercent + '%';
    });
  }
  window.addEventListener('load', toggleScrollProgress);

  /**
   * High-Contrast Mode Toggle
   */
  document.querySelectorAll('.contrast-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      document.body.classList.toggle('high-contrast');
      localStorage.setItem('highContrast', document.body.classList.contains('high-contrast'));
    });
  });
  window.addEventListener('load', () => {
    if (localStorage.getItem('highContrast') === 'true') {
      document.body.classList.add('high-contrast');
    }
  });

  /**
   * Mobile Nav Toggle
   */
  const mobileNavToggleBtn = document.querySelector('.mobile-nav-toggle');
  const offcanvasNav = document.querySelector('#offcanvasNav');

  function mobileNavToggle() {
    if (mobileNavToggleBtn && offcanvasNav) {
      document.querySelector('body').classList.toggle('mobile-nav-active');
      mobileNavToggleBtn.classList.toggle('bi-list');
      mobileNavToggleBtn.classList.toggle('bi-x');
      offcanvasNav.classList.toggle('show');
      offcanvasNav.style.transition = 'transform 0.3s ease';
      if (offcanvasNav.classList.contains('show')) {
        offcanvasNav.style.transform = 'translateX(0)';
      } else {
        offcanvasNav.style.transform = 'translateX(100%)';
      }
    }
  }

  if (mobileNavToggleBtn) {
    mobileNavToggleBtn.addEventListener('click', mobileNavToggle);
  }

  /**
   * Hide mobile nav on same-page/hash links
   */
  document.querySelectorAll('#navmenu a, #offcanvasNav .nav-link').forEach(navmenu => {
    navmenu.addEventListener('click', (e) => {
      if (navmenu.hash && document.querySelector('.mobile-nav-active')) {
        e.preventDefault();
        mobileNavToggle();
        setTimeout(() => {
          document.querySelector(navmenu.hash).scrollIntoView({ behavior: 'smooth' });
        }, 300);
      }
    });
  });

  /**
   * Preloader
   */
  const preloader = document.querySelector('#preloader');
  if (preloader) {
    window.addEventListener('load', () => {
      preloader.style.opacity = '0';
      setTimeout(() => {
        preloader.style.display = 'none';
      }, 500);
    });
  }

  /**
   * Scroll Top Button
   */
  let scrollTop = document.querySelector('.scroll-top');

  function toggleScrollTop() {
    if (scrollTop) {
      window.scrollY > 100 ? scrollTop.classList.add('active') : scrollTop.classList.remove('active');
    }
  }

  if (scrollTop) {
    scrollTop.addEventListener('click', (e) => {
      e.preventDefault();
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });
    window.addEventListener('load', toggleScrollTop);
    document.addEventListener('scroll', toggleScrollTop);
  }

  /**
   * Animation on Scroll (AOS) Initialization
   */
  function aosInit() {
    AOS.init({
      duration: 1000,
      easing: 'ease-in-out',
      once: true,
      offset: 100,
    });
  }
  window.addEventListener('load', aosInit);

  /**
   * Initiate GLightbox
   */
  const glightbox = GLightbox({
    selector: '.glightbox',
    touchNavigation: true,
    loop: true,
    autoplayVideos: true,
  });

  /**
   * Initiate Pure Counter
   */
  new PureCounter();

  /**
   * Ripple Effect for Buttons
   */
  document.querySelectorAll('.btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
      let x = e.clientX - e.target.offsetLeft;
      let y = e.clientY - e.target.offsetTop;
      let ripple = document.createElement('span');
      ripple.style.left = x + 'px';
      ripple.style.top = y + 'px';
      ripple.classList.add('ripple');
      this.appendChild(ripple);
      setTimeout(() => ripple.remove(), 600);
    });
  });

  /**
   * Dynamic Read More for Departments
   */
  document.querySelectorAll('.read-more').forEach(button => {
    button.addEventListener('click', () => {
      const parent = button.parentElement;
      const fullText = button.getAttribute('data-full-text');
      const isExpanded = parent.classList.contains('expanded');
      if (isExpanded) {
        parent.textContent = parent.textContent.substring(0, 100) + '... ';
        parent.classList.remove('expanded');
        button.textContent = 'Read More';
      } else {
        parent.textContent = fullText + ' ';
        parent.classList.add('expanded');
        button.textContent = 'Read Less';
      }
      parent.appendChild(button);
    });
  });

  /**
   * Department Filtering
   */
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const filter = btn.getAttribute('data-filter');
      document.querySelectorAll('.dept-card').forEach(card => {
        if (filter === 'all' || card.getAttribute('data-category') === filter) {
          card.classList.remove('hidden');
        } else {
          card.classList.add('hidden');
        }
      });
    });
  });

  /**
   * Init Swiper Sliders
   */
  function initSwiper() {
    // Hero Slider
    new Swiper('.hero-slider', {
      effect: 'fade',
      fadeEffect: { crossFade: true },
      loop: true,
      autoplay: {
        delay: 3000,
        disableOnInteraction: false,
      },
      navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
      },
      pagination: {
        el: '.swiper-pagination',
        clickable: true,
      },
    });

    // Gallery Slider
    new Swiper('.gallery-slider', {
      slidesPerView: 1,
      spaceBetween: 30,
      loop: true,
      autoplay: {
        delay: 5000,
        disableOnInteraction: false,
      },
      navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
      },
      pagination: {
        el: '.swiper-pagination',
        clickable: true,
      },
      breakpoints: {
        768: {
          slidesPerView: 2,
        },
        992: {
          slidesPerView: 3,
        },
      },
    });

    // Testimonials Slider
    new Swiper('.testimonials-slider', {
      slidesPerView: 1,
      spaceBetween: 30,
      loop: true,
      autoplay: {
        delay: 4000,
        disableOnInteraction: false,
      },
      pagination: {
        el: '.swiper-pagination',
        clickable: true,
      },
      breakpoints: {
        768: {
          slidesPerView: 2,
        },
        992: {
          slidesPerView: 3,
        },
      },
    });
  }

  window.addEventListener('load', initSwiper);

  /**
   * Correct scrolling position upon page load for URLs with hash links
   */
  window.addEventListener('load', function(e) {
    if (window.location.hash) {
      if (document.querySelector(window.location.hash)) {
        setTimeout(() => {
          let section = document.querySelector(window.location.hash);
          let scrollMarginTop = getComputedStyle(section).scrollMarginTop;
          window.scrollTo({
            top: section.offsetTop - parseInt(scrollMarginTop) || 0,
            behavior: 'smooth'
          });
        }, 100);
      }
    }
  });

  /**
   * Navmenu Scrollspy
   */
  let navmenulinks = document.querySelectorAll('.navmenu a, #offcanvasNav .nav-link');

  function navmenuScrollspy() {
    navmenulinks.forEach(navmenulink => {
      if (!navmenulink.hash) return;
      let section = document.querySelector(navmenulink.hash);
      if (!section) return;
      let position = window.scrollY + 200;
      if (position >= section.offsetTop && position <= (section.offsetTop + section.offsetHeight)) {
        document.querySelectorAll('.navmenu a.active, #offcanvasNav .nav-link.active').forEach(link => link.classList.remove('active'));
        navmenulink.classList.add('active');
      } else {
        navmenulink.classList.remove('active');
      }
    });
  }

  window.addEventListener('load', navmenuScrollspy);
  document.addEventListener('scroll', navmenuScrollspy);

})();
