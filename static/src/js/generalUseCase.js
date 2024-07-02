/**
 * htmx indicator
 */
document.addEventListener("DOMContentLoaded", function() {
  const forms = document.querySelectorAll('form');

  forms.forEach((form, index) => {
    const spinner = document.createElement('span');
    spinner.className = 'loading loading-spinner loading-sm htmx-indicator';
    spinner.id = `spinner-${index}`; 
    
    const submitButton = form.querySelector('button[type="submit"]');

    if (submitButton) {
      submitButton.insertBefore(spinner, submitButton.firstChild);

      form.setAttribute('hx-indicator', `#${spinner.id}`);
    }
  });
});
