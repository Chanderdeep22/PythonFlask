 "use strict";

const form = document.querySelector("#submission-form");
const feedback = document.querySelector("#form-feedback");
const submitButton = document.querySelector("#submit-button");

if (form && feedback && submitButton) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    feedback.textContent = "";
    feedback.removeAttribute("data-state");
    submitButton.disabled = true;

    try {
      const response = await fetch(form.action, {
        method: form.method,
        body: new FormData(form),
        headers: { Accept: "application/json" },
      });

      let result = {};
      try {
        result = await response.json();
      } catch (_parseError) {
        throw new Error("The server returned an unexpected response. Please try again.");
      }

      if (!response.ok) {
        throw new Error(result.error || `The server returned ${response.status}.`);
      }

      if (result.redirect_url) {
        window.location.assign(result.redirect_url);
        return;
      }

      throw new Error("The submission response did not include a success redirect.");
    } catch (error) {
      feedback.dataset.state = "error";
      feedback.textContent = error.message || "Unable to save your submission. Please try again.";
    } finally {
      submitButton.disabled = false;
    }
  });
}
