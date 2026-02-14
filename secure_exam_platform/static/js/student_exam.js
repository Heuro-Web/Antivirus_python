(() => {
  const body = document.body;
  if (!body.dataset.sessionId) return;

  const sessionId = body.dataset.sessionId;
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  const ws = new WebSocket(`${protocol}://${window.location.host}/ws/session/${sessionId}/`);
  const video = document.getElementById('webcam');
  const canvas = document.getElementById('capture-canvas');
  const ctx = canvas.getContext('2d');
  const violationsDisplay = document.getElementById('violations-count');
  let violations = 0;
  let stream;

  const sendEvent = (type, data = {}) => {
    if (ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ type, data }));
  };

  async function initExam() {
    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
      video.srcObject = stream;
    } catch (e) {
      alert('Webcam obligatoire pour commencer cet examen.');
      sendEvent('webcam_refused', { reason: e.message, severity: 'critical' });
      return;
    }

    if (document.documentElement.requestFullscreen) {
      await document.documentElement.requestFullscreen();
    }

    sendEvent('heartbeat', { webcam_active: true, fullscreen: !!document.fullscreenElement });
  }

  setInterval(() => sendEvent('heartbeat', {
    webcam_active: !!(video.srcObject && video.srcObject.active),
    fullscreen: !!document.fullscreenElement,
  }), 5000);

  setInterval(() => {
    if (!video.srcObject) return;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    sendEvent('snapshot_upload', { image: canvas.toDataURL('image/jpeg', 0.5) });
  }, 15000);

  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      violations += 1;
      violationsDisplay.textContent = String(violations);
      sendEvent('tab_change', { severity: 'high' });
    }
  });

  window.addEventListener('blur', () => sendEvent('focus_change', { severity: 'medium' }));
  document.addEventListener('fullscreenchange', () => {
    if (!document.fullscreenElement) {
      violations += 1;
      violationsDisplay.textContent = String(violations);
      sendEvent('fullscreen_exit', { severity: 'critical' });
    }
  });

  document.addEventListener('contextmenu', (e) => { e.preventDefault(); sendEvent('right_click', { severity: 'low' }); });
  document.addEventListener('copy', (e) => { e.preventDefault(); sendEvent('copy_attempt', { severity: 'medium' }); });
  document.addEventListener('paste', (e) => { e.preventDefault(); sendEvent('paste_attempt', { severity: 'medium' }); });
  document.addEventListener('selectstart', (e) => e.preventDefault());

  document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && ['c', 'v', 't', 'w'].includes(e.key.toLowerCase())) {
      e.preventDefault();
      sendEvent('shortcut_blocked', { key: e.key, severity: 'medium' });
    }
  });

  window.addEventListener('beforeunload', () => {
    sendEvent('session_closed', { severity: 'critical' });
    navigator.sendBeacon(`/api/sessions/${sessionId}/close/`, '');
  });

  ws.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    if (msg.type === 'admin_command' && msg.data.command === 'force_submit') {
      fetch(`/api/sessions/${sessionId}/submit/`, { method: 'POST', headers: { 'X-Requested-With': 'XMLHttpRequest' } });
    }
  };

  document.getElementById('submit-btn').addEventListener('click', async () => {
    await fetch(`/api/sessions/${sessionId}/submit/`, { method: 'POST' });
    alert('Examen soumis.');
  });

  initExam();
})();
