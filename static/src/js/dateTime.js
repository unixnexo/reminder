function toLocalISOString(date) {
  const localDate = new Date(date - date.getTimezoneOffset() * 60000); //offset in milliseconds.
  // remove second/millisecond
  localDate.setSeconds(null);
  localDate.setMilliseconds(null);
  return localDate.toISOString().slice(0, -1);
}

document.getElementById("dateTimePicker").value = toLocalISOString(new Date());

document.body.addEventListener('htmx:afterRequest', () => {
  console.log('dateTime updated');
  document.getElementById("dateTimePicker").value = toLocalISOString(new Date());
});
