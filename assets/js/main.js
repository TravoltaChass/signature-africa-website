// Signature Africa — site scripts

// Central booking link. Every "Book Now" button on the site reads from
// this one place.
const BOOKING_URL = "https://bookings.signatureafrica.com/";

document.addEventListener("DOMContentLoaded", () => {
  // Wire booking buttons
  document.querySelectorAll(".js-book-btn").forEach((el) => {
    el.setAttribute("href", BOOKING_URL);
    el.setAttribute("target", "_blank");
    el.setAttribute("rel", "noopener");
  });

  // Header scroll state
  const header = document.querySelector(".site-header");
  const onScroll = () => {
    if (window.scrollY > 40) {
      header.classList.add("is-light");
    } else if (!document.body.classList.contains("nav-open")) {
      header.classList.remove("is-light");
    }
  };
  window.addEventListener("scroll", onScroll);
  onScroll();

  // Mobile nav toggle
  const toggle = document.querySelector(".nav-toggle");
  if (toggle) {
    toggle.addEventListener("click", () => {
      document.body.classList.toggle("nav-open");
      if (document.body.classList.contains("nav-open")) {
        header.classList.add("is-light");
      } else {
        onScroll();
      }
    });
    document.querySelectorAll(".nav-links a").forEach((a) => {
      a.addEventListener("click", () => document.body.classList.remove("nav-open"));
    });
  }

  // Reveal-on-scroll
  const revealEls = document.querySelectorAll("[data-reveal]");
  if ("IntersectionObserver" in window && revealEls.length) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12 }
    );
    revealEls.forEach((el) => io.observe(el));
  }

  // Footer year
  const yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = new Date().getFullYear();
});
