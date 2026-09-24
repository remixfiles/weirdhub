(function () {
  // Replace with your actual Google Apps Script Web App URL
  const SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyZo_M9hon7FcENKxKH8nYJKjPMDK4OgjHl9lVqvcPi24DMrnGI1yUD-JM1TJ3zYsoXPQ/exec";

  const form = document.getElementById("newsletter-form");
  if (!form) return;

  const emailInput = document.getElementById("newsletter-email");
  const submitBtn = document.getElementById("newsletter-btn");
  const btnText = submitBtn.querySelector(".btn-text");
  const btnSpinner = submitBtn.querySelector(".btn-spinner");
  const statusMsg = document.getElementById("newsletter-status");

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const email = emailInput.value.trim();
    if (!email) return;

    // Loading state
    submitBtn.disabled = true;
    btnText.style.display = "none";
    btnSpinner.style.display = "inline";
    statusMsg.textContent = "";
    statusMsg.className = "newsletter-status";

    const formData = new FormData();
    formData.append("email", email);

    fetch(SCRIPT_URL, {
      method: "POST",
      body: formData,
      mode: "no-cors"
    })
      .then(() => {
        statusMsg.textContent = "You're in! Thanks for joining WeirdHub Weekly.";
        statusMsg.className = "newsletter-status success";
        form.reset();
      })
      .catch(() => {
        statusMsg.textContent = "Something went wrong. Please try again.";
        statusMsg.className = "newsletter-status error";
      })
      .finally(() => {
        submitBtn.disabled = false;
        btnText.style.display = "inline";
        btnSpinner.style.display = "none";
      });
  });
})();