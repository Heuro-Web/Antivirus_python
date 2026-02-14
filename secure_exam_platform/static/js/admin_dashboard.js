(() => {
  const table = document.getElementById('events-table');
  if (!table) return;

  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  const ws = new WebSocket(`${protocol}://${window.location.host}/ws/admin/`);

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${data.session_id}</td>
      <td>${data.student}</td>
      <td>${data.event}</td>
      <td>${data.violations_count}</td>
      <td>${data.webcam_active}</td>
      <td>${data.fullscreen_status}</td>
    `;
    table.prepend(row);
  };
})();
