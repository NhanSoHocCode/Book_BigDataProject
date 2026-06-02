function renderBarChart(elementId, data) {
  const element = document.getElementById(elementId);
  if (!element || typeof Chart === "undefined") {
    return;
  }
  new Chart(element, {
    type: "bar",
    data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { y: { beginAtZero: true } }
    }
  });
}
