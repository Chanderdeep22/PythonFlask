"use strict";

const form = document.querySelector("#submission-form");
const feedback = document.querySelector("#form-feedback");
const submitButton = document.querySelector("#submit-button");

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
    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error || `The server returned ${response.status}.`);
    }

    feedback.textContent = "Your submission was saved successfully.";
    form.reset();
  } catch (error) {
    feedback.dataset.state = "error";
    feedback.textContent = `Unable to save your submission. ${error.message}`;
  } finally {
    submitButton.disabled = false;
  }
});
