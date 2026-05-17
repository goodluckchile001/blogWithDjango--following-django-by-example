// Blog JavaScript - Reactive Features
console.log("Blog JS loaded successfully");
document.addEventListener("DOMContentLoaded", function () {
  // Fade in posts on scroll
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px",
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = "1";
        entry.target.style.transform = "translateY(0)";
      }
    });
  }, observerOptions);

  // Observe post cards and comments
  document.querySelectorAll(".post-card, .comment").forEach((el) => {
    el.style.opacity = "0";
    el.style.transform = "translateY(20px)";
    el.style.transition = "opacity 0.6s ease, transform 0.6s ease";
    observer.observe(el);
  });

  // Back to top button
  const backToTopBtn = document.createElement("button");
  backToTopBtn.innerHTML = "↑";
  backToTopBtn.id = "back-to-top";
  backToTopBtn.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #007bff;
        color: white;
        border: none;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        font-size: 20px;
        cursor: pointer;
        opacity: 1;
        transition: opacity 0.3s ease;
        z-index: 1000;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    `;
  document.body.appendChild(backToTopBtn);

  // Show/hide back to top button
    window.addEventListener("scroll", () => {
    if (window.pageYOffset > 300) { // Show later
      backToTopBtn.style.opacity = "1";
      backToTopBtn.style.pointerEvents = "auto";
    } else {
      backToTopBtn.style.opacity = "0";
      backToTopBtn.style.pointerEvents = "none"; // Stop it from being clickable while invisible
    }
  });

  // Smooth scroll to top
  backToTopBtn.addEventListener("click", () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  });

  // Sidebar toggle
  const sidebar = document.getElementById("sidebar");
  const headerInner = document.querySelector(".header-inner");

  // Create toggle button
  const toggleBtn = document.createElement("button");
  toggleBtn.innerHTML = "☰";
  toggleBtn.id = "sidebar-toggle";
  toggleBtn.setAttribute("aria-label", "Toggle Sidebar");

  if (headerInner) {
    headerInner.appendChild(toggleBtn);
  } else {
    document.body.appendChild(toggleBtn);
  }

  // Initially hide sidebar on small screens
  if (window.innerWidth <= 992) {
    sidebar.style.display = "none";
  }

  // Toggle sidebar
  toggleBtn.addEventListener("click", () => {
    sidebar.classList.toggle('active');
    
    // Smooth transition logic
    if (sidebar.classList.contains('active')) {
      sidebar.style.display = "block";
      toggleBtn.innerHTML = "✕";
    } else {
      sidebar.style.display = "none";
      toggleBtn.innerHTML = "☰";
    }
  });

  // Responsive reset
  window.addEventListener('resize', () => {
    if (window.innerWidth > 992) {
      sidebar.style.display = "block";
      toggleBtn.innerHTML = "☰";
    } else {
      sidebar.style.display = "none";
      toggleBtn.innerHTML = "☰";
    }
  });

  // Form validation feedback
  const forms = document.querySelectorAll("form");
  forms.forEach((form) => {
    form.addEventListener("submit", function (e) {
      const requiredFields = form.querySelectorAll(
        "input[required], textarea[required]",
      );
      let isValid = true;

      requiredFields.forEach((field) => {
        if (!field.value.trim()) {
          field.style.borderColor = "#dc3545";
          isValid = false;
        } else {
          field.style.borderColor = "#28a745";
        }
      });

      if (!isValid) {
        e.preventDefault();
        alert("Please fill in all required fields.");
      }
    });
  });

  // Theme switch handling
  const themeToggle = document.querySelector('#theme-checkbox');
  const currentTheme = localStorage.getItem('theme') || 'light';

  const applyTheme = (theme) => {
    if (theme === 'dark') {
      document.body.classList.add('dark-mode');
      if (themeToggle) themeToggle.checked = true;
    } else {
      document.body.classList.remove('dark-mode');
      if (themeToggle) themeToggle.checked = false;
    }
  };

  applyTheme(currentTheme);

  if (themeToggle) {
    themeToggle.addEventListener('change', function (e) {
      const theme = e.target.checked ? 'dark' : 'light';
      applyTheme(theme);
      localStorage.setItem('theme', theme);
    });
  }
});
